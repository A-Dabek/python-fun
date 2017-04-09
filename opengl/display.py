from vispy import gloo
import numpy as np
from vispy.util.transforms import ortho
from opengl import global_vars as GV


class TextureAtlas:
    texture_count = 0

    def __init__(self, tile_width, tile_height):
        self.tile_w = tile_width
        self.tile_h = tile_height
        self.hor_tiles = 0
        self.ver_tiles = 0
        self.elements = 0
        self.image = None
        self.atlas = []
        self.valid = False
        self.texture_object = None
        self.texture_id = TextureAtlas.texture_count
        TextureAtlas.texture_count += 1

        image = np.full((100, 100, 4), 255, dtype=np.uint8)
        self.add_texture(image)

    def add_texture(self, image):
        w, h = len(image), len(image[0])
        if w != self.tile_w or h != self.tile_h:
            raise TypeError("wrong size")
        if self.image is None:
            self.hor_tiles = 1
            self.ver_tiles = 1
            self.elements = 1
            self.image = image
            self.texture_object = gloo.Texture2D(self.image)
            self.valid = True
            return self.texture_id, 0, 0
        if self.elements == self.hor_tiles * self.ver_tiles:
            self.valid = False
            if self.hor_tiles == self.ver_tiles:
                self.hor_tiles += 1
                self.image = np.pad(self.image, ((0, 0), (0, self.tile_h), (0, 0)), mode='constant', constant_values=0)
            else:
                self.ver_tiles += 1
                self.image = np.pad(self.image, ((0, self.tile_w), (0, 0), (0, 0)), mode='constant', constant_values=0)

        self.elements += 1
        spiral_to_linear = self.elements - 1
        if self.hor_tiles > self.ver_tiles:
            diff = self.hor_tiles * self.ver_tiles - self.elements + 1
            if diff >= 2:
                spiral_to_linear -= (diff - 1) * self.ver_tiles

        x = (spiral_to_linear % self.hor_tiles)
        y = (spiral_to_linear // self.hor_tiles)
        for r in range(self.tile_w * y, self.tile_w * (y + 1)):
            for c in range(self.tile_h * x, self.tile_h * (x + 1)):
                self.image[r, c] = image[r - self.tile_w * y, c - self.tile_h * x]
        return self.texture_id, (self.elements - 1) % self.hor_tiles, (self.elements - 1) // self.hor_tiles

    def get_tex(self):
        if not self.valid:
            self.texture_object = gloo.Texture2D(self.image)
            self.valid = True
        return self.texture_object

    def get_tex_vertices(self, x, y):
        if x < 0 or y < 0 or self.hor_tiles <= 0 or self.ver_tiles <= 0:
            return None
        min_x = x / self.hor_tiles
        min_y = y / self.hor_tiles
        max_x = (x + 1) / self.hor_tiles
        max_y = (y + 1) / self.hor_tiles
        return np.array(
            [[min_x, min_y], [max_x, min_y], [min_x, max_y], [max_x, max_y]])


class Display:
    program = gloo.Program(GV.VERT_SHADER, GV.FRAG_SHADER)
    particle_program = gloo.Program(GV.PARTICLE_VERT_SHADER, GV.PARTICLE_FRAG_SHADER)
    atlases = {}
    surfaces = []
    surface_lookup_index = 0
    vbo = []
    textures_loaded = False
    collection_valid = False
    surfaces_invalid = []
    special_tex = None
    indices = []

    @staticmethod
    def init_display(w, h):
        gloo.set_state(clear_color='white', blend=True, depth_test=False,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))
        view = np.eye(4, dtype=np.float32)
        projection = ortho(0, w, h, 0, -100, 100)
        Display.program['u_view'] = view
        Display.program['u_projection'] = projection
        Display.particle_program['u_view'] = view
        Display.particle_program['u_projection'] = projection
        gloo.set_clear_color('white')
        gloo.set_viewport(0, 0, w, h)

    @staticmethod
    def atlas(surface, image):
        if image is None:
            w, h, = 100, 100
        else:
            w, h, _ = image.shape
        key = str((w, h))

        if Display.atlases.get(key, 0) == 0:
            Display.atlases[key] = TextureAtlas(w, h)
            Display.atlases[key].shader_id = len(Display.atlases) - 1
            Display.textures_loaded = False

        if image is None:
            tex_id, x, y = Display.atlases[key].texture_id, 0, 0
        else:
            tex_id, x, y = Display.atlases[key].add_texture(image)

        surface.set_atlas_info(x, y, Display.atlases[key].get_tex_vertices(x, y), tex_id)

    actors_tex = []
    actors_notex = []

    @staticmethod
    def add(collidable, tex=False):
        pass

    @staticmethod
    def add(surface):
        if len(Display.surfaces) > Display.surface_lookup_index:
            if Display.surfaces[Display.surface_lookup_index] != surface:
                Display.surfaces.insert(Display.surface_lookup_index, surface)
                Display.collection_valid = False
        else:
            Display.collection_valid = False
            Display.surfaces.append(surface)

        Display.surface_lookup_index += 1
        if not surface.valid:
            Display.surfaces_invalid.append(Display.surface_lookup_index - 1)
        pass

    @staticmethod
    def batch_draws():
        if not Display.collection_valid:
            Display.vbo = []
            Display.indices = []
            for s in Display.surfaces:
                if len(Display.vbo) == 0:
                    Display.vbo = s.get_vbo()
                else:
                    Display.vbo = np.append(Display.vbo, s.get_vbo())
            Display.indices = gloo.IndexBuffer(
                np.array([0, 1, 2, 1, 2, 3], np.uint32) + np.arange(0, 4 * len(Display.surfaces), 4,
                                                                    dtype=np.uint32)[:, np.newaxis])
            Display.collection_valid = True
            Display.surfaces_invalid = []
        else:
            while len(Display.surfaces_invalid) > 0:
                start = Display.surfaces_invalid[0]
                new_vbo = Display.surfaces[start].get_vbo()
                Display.vbo[4 * start:4 + 4 * start] = new_vbo
                del Display.surfaces_invalid[0]

    @staticmethod
    def draw():
        if len(Display.surfaces) > Display.surface_lookup_index:
            Display.surfaces = Display.surfaces[:Display.surface_lookup_index]
            Display.collection_valid = False

        Display.surface_lookup_index = 0

        if not Display.textures_loaded:
            for v in list(Display.atlases.values()):
                Display.program['u_texture[' + str(v.shader_id) + ']'] = v.get_tex()
            Display.textures_loaded = True

        Display.batch_draws()
        Display.program.bind(gloo.VertexBuffer(Display.vbo))
        Display.program.draw('triangles', indices=Display.indices)
        pass

    @staticmethod
    def draw_particle(particle):
        Display.particle_program.bind(gloo.VertexBuffer(particle.model))
        indices = gloo.IndexBuffer(
            np.array([0, 1, 2, 1, 2, 3], np.uint32) + np.arange(0, 4 * particle._amount, 4,
                                                                dtype=np.uint32)[:, np.newaxis])
        Display.particle_program.draw('triangles', indices=indices)
