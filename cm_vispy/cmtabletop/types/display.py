from vispy import gloo
import numpy as np
from scipy import misc
from vispy.util.transforms import ortho


class TextureAtlas:
    def __init__(self, tile_width, tile_height):
        self.tile_w = tile_width
        self.tile_h = tile_height
        self.hor_tiles = 0
        self.ver_tiles = 0
        self.elements = 0
        self.image = None
        self.atlas = []
        self.translator = {}
        self.valid = False
        self.texture = None
        self.shader_id = -1

    def add_texture(self, name, image=None):
        if image is None:
            image = misc.imread(name)
        w, h = len(image), len(image[0])
        if w != self.tile_w or h != self.tile_h:
            raise TypeError("wrong size")
        if self.translator.get(name, 0) != 0:
            return
        if self.image is None:
            self.hor_tiles = 1
            self.ver_tiles = 1
            self.elements = 1
            self.translator[name] = (0, 0)
            self.image = image
            self.texture = gloo.Texture2D(self.image)
            self.valid = True
            return
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
        self.translator[name] = ((self.elements - 1) % self.hor_tiles, (self.elements - 1) // self.hor_tiles)
        pass

    def get_coords(self, name):
        answer = self.translator.get(name, 0)
        if answer == 0:
            return None
        x, y = answer
        return x, y

    def get_tex(self):
        if not self.valid:
            self.texture = gloo.Texture2D(self.image)
            self.valid = True
        return self.texture

    def get_tex_vertices(self, x, y):
        if x < 0 or y < 0 or self.hor_tiles <= 0 or self.ver_tiles <= 0:
            return None
        min_x = x / self.hor_tiles
        min_y = y / self.hor_tiles
        max_x = (x + 1) / self.hor_tiles
        max_y = (y + 1) / self.hor_tiles
        # return np.array(
        #     [[min_x, min_y], [max_x, min_y], [min_x, max_y], [max_x, min_y], [max_x, max_y], [min_x, max_y]])
        return np.array(
            [[min_x, min_y], [max_x, min_y], [min_x, max_y], [max_x, max_y]])


class Display:
    VERT_SHADER = """
    // Uniforms
    uniform mat4 u_view;
    uniform mat4 u_projection;
    uniform float u_antialias;
    // Attributes
    attribute vec4 a_position;
    attribute vec2 a_texcoord;
    attribute float a_tex;
    // Varyings
    varying vec2 v_texcoord;
    varying float f_tex;
    // Main
    void main (void)
    {
        f_tex = a_tex;
        v_texcoord = a_texcoord;
        gl_Position = u_projection * u_view * a_position;
    }
    """

    FRAG_SHADER = """
    uniform sampler2D u_texture[4];
    varying float f_tex;
    varying vec2 v_texcoord;
    void main()
    {
        gl_FragColor = texture2D(u_texture[int(f_tex)], v_texcoord);
    }
    """

    program = gloo.Program(VERT_SHADER, FRAG_SHADER)
    atlases = {}
    surfaces = []
    surface_lookup_index = 0
    vbo = []
    textures_loaded = False
    surfaces_valid = False
    special_tex = None
    indices = []

    @staticmethod
    def init_display(w, h):
        view = np.eye(4, dtype=np.float32)
        projection = ortho(0, w, h, 0, -1, 1)
        Display.program['u_view'] = view
        Display.program['u_projection'] = projection
        gloo.set_clear_color('black')
        gloo.set_viewport(0, 0, w, h)

    @staticmethod
    def add(surface):
        if len(Display.surfaces) > Display.surface_lookup_index:
            if Display.surfaces[Display.surface_lookup_index] != surface:
                Display.surfaces.insert(Display.surface_lookup_index, surface)
                Display.surfaces_valid = False
        else:
            Display.surfaces_valid = False
            Display.surfaces.append(surface)

        Display.surface_lookup_index += 1
        if not surface.valid:
            Display.surfaces_valid = False

        if surface.get_atlas_info()[0] is not None:
            return

        im = misc.imread(surface.get_path())
        w, h, _ = im.shape
        key = str((w, h))
        if Display.atlases.get(key, 0) == 0:
            Display.atlases[key] = TextureAtlas(w, h)
            Display.atlases[key].shader_id = len(Display.atlases) - 1
            Display.textures_loaded = False

        Display.atlases[key].add_texture(surface.get_path(), im)
        surface.set_atlas_key(key)
        pass

    @staticmethod
    def batch_draws():
        if Display.surfaces_valid:
            return
        Display.vbo = []
        Display.indices = []
        for s in Display.surfaces:
            atlas = Display.atlases[s.atlas_key]
            x, y = atlas.get_coords(s.path)
            s.set_atlas_info(x, y, tex_coords=atlas.get_tex_vertices(x, y), tex_id=atlas.shader_id)
            if len(Display.vbo) == 0:
                Display.vbo = s.get_vbo()
            else:
                Display.vbo = np.append(Display.vbo, s.get_vbo())
        Display.indices = gloo.IndexBuffer(
            np.array([0, 1, 2, 1, 2, 3], np.uint32) + np.arange(0, 4 * len(Display.surfaces), 4,
                                                                dtype=np.uint32)[:, np.newaxis])
        Display.surfaces_valid = True

    @staticmethod
    def draw():
        if len(Display.surfaces) > Display.surface_lookup_index:
            Display.surfaces = Display.surfaces[:Display.surface_lookup_index]
            Display.surfaces_valid = False

        Display.surface_lookup_index = 0

        if not Display.textures_loaded:
            for v in list(Display.atlases.values()):
                Display.program['u_texture[' + str(v.shader_id) + ']'] = v.get_tex()
            Display.textures_loaded = True

        Display.batch_draws()
        Display.program.bind(gloo.VertexBuffer(Display.vbo))
        Display.program.draw('triangles', indices=Display.indices)
        pass


class Surface:
    def __init__(self, image_path, shape):
        self.path = image_path
        self.atlas_key = None
        self.atlas_coords = (0, 0)
        self.shape = shape

        # before - 6
        self.vbo = np.zeros(4, dtype=[('a_position', np.float32, 4),
                                      ('a_texcoord', np.float32, 2),
                                      ('a_tex', np.float32, 1)])

        W, H = self.shape
        # self.vbo['a_position'] = np.array(
        #     [[0, 0, 0, 1], [W, 0, 0, 1], [0, H, 0, 1], [W, 0, 0, 1], [W, H, 0, 1], [0, H, 0, 1]])
        self.vbo['a_position'] = np.array(
            [[0, 0, 0, 1], [W, 0, 0, 1], [0, H, 0, 1], [W, H, 0, 1]])
        # self.vbo['a_texcoord'] = np.array([[0, 0], [1, 0], [0, 1], [1, 0], [1, 1], [0, 1]])
        self.vbo['a_texcoord'] = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
        # self.vbo['a_tex'] = np.array([0, 0, 0, 0, 0, 0])
        self.vbo['a_tex'] = np.array([0, 0, 0, 0])
        self.m_rotation = np.eye(4, dtype=np.float32)
        self.m_translation = np.eye(4, dtype=np.float32)
        self.model = np.copy(self.vbo)
        self.valid = False
        pass

    def calculate_model(self):
        if self.valid:
            return
        for i in range(len(self.model)):
            self.model[i][0] = np.dot(self.vbo[i][0], np.dot(self.m_rotation, self.m_translation))
        self.valid = True
        pass

    def set_atlas_info(self, x, y, tex_coords, tex_id=0):
        self.vbo['a_texcoord'] = tex_coords
        # self.vbo['a_tex'] = np.array([tex_id, tex_id, tex_id, tex_id, tex_id, tex_id])
        self.vbo['a_tex'] = np.array([tex_id, tex_id, tex_id, tex_id])
        self.model = np.copy(self.vbo)
        self.atlas_coords = (x, y)
        self.valid = False

    def set_atlas_key(self, atlas_key):
        self.atlas_key = atlas_key

    def get_atlas_info(self):
        return self.atlas_key, self.atlas_coords

    def get_shape(self):
        return self.shape

    def get_path(self):
        return self.path

    def copy(self):
        return Surface(self.path, self.shape)

    def get_vbo(self):
        if not self.valid:
            self.calculate_model()
        return self.model

    def translate(self, x, y):
        from vispy.util import transforms
        self.m_translation = transforms.translate((x, y, 0.0), dtype=np.float32)
        self.valid = False
