import numpy as np
from vispy.color import ColorArray
from opengl.display import Display


class SurfaceList:
    color_dict = {}

    @staticmethod
    def get_color(color):
        fetch = Surface.color_dict.get(color, None)
        if fetch is None:
            Surface.color_dict[color] = ColorArray(color).rgba
        fetch = Surface.color_dict[color]
        return fetch

    def __init__(self, amount=1, width=5, height=5, color='black', parent=None):
        if amount <= 0:
            raise ValueError('list needs at least 1 element')

        color = Surface.get_color(color)
        self._v = 4
        self.shape = (width, height)

        self._vbo = np.zeros(self._v * amount, dtype=[('a_pos', np.float32, 4),
                                                      ('a_color', np.float32, 4),
                                                      ('a_tsl_xy', np.float32, 2)])

        W, H = self.shape
        self._org_pos = np.array([[0, 0, 0, 1], [W, 0, 0, 1], [0, H, 0, 1], [W, H, 0, 1]])
        self._vbo['a_pos'] = np.tile([[0, 0, 0, 1], [W, 0, 0, 1], [0, H, 0, 1], [W, H, 0, 1]], (amount, 1))
        self._vbo['a_color'] = np.tile(np.tile(color, (self._v, 1)), (amount, 1))
        self._vbo['a_tsl_xy'] = np.tile(np.tile([[0., 0.]], (self._v, 1)), (amount, 1))
        self._parent = parent
        self._amount = amount

    @property
    def model(self):
        return self._vbo

    def __setitem__(self, key, value):
        s_id, s_prop = key
        if 0 <= s_id <= self._amount:
            i_from = self._v * s_id
            i_to = i_from + self._v
            if s_prop == 'color':
                color, alpha = value
                if color != "same":
                    color = SurfaceList.get_color(color)
                else:
                    color = self._vbo['a_color'][i_from]
                color[3] = alpha
                self._vbo['a_color'][i_from:i_to] = np.tile(list(color), (self._v, 1))
            elif s_prop == 'pos':
                x, y = value
                self._vbo['a_pos'][i_from:i_to] = self._org_pos + [x, y, 0., 1.]
            elif s_prop == 'translate':
                x, y = value
                self._vbo['a_tsl_xy'][i_from:i_to] = [x, y]


class Surface:
    color_dict = {}

    @staticmethod
    def get_color(color):
        fetch = Surface.color_dict.get(color, None)
        if fetch is None:
            Surface.color_dict[color] = ColorArray(color).rgba
        fetch = Surface.color_dict[color]
        return fetch

    def __init__(self, width, height, image=None, color='black', parent=None):
        self.parent = parent
        self.color = Surface.get_color(color)
        self.atlas_key = None
        self.atlas_coords = (0, 0)
        self.shape = (width, height)

        self.vbo = np.zeros(4, dtype=[('a_pos', np.float32, 4),
                                      ('a_tex_xy', np.float32, 2),
                                      ('a_color', np.float32, 4),
                                      ('a_tsl_xy', np.float32, 2),
                                      ('a_tex_id', np.float32, 1)])

        W, H = self.shape
        self.org_position = np.array([[0, 0, 0, 1], [W, 0, 0, 1], [0, H, 0, 1], [W, H, 0, 1]])
        self.vbo['a_pos'] = np.array([[0, 0, 0, 1], [W, 0, 0, 1], [0, H, 0, 1], [W, H, 0, 1]])
        self.vbo['a_tex_xy'] = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
        self.vbo['a_color'] = np.tile(self.color, (4, 1))
        self.vbo['a_tex_id'] = np.array(4 * [0])
        self.vbo['a_tsl_xy'] = np.tile([[0., 0.]], (4, 1))
        self.angle = 0.0
        self.coords = [0, 0, 0]
        self.valid = True
        Display.atlas(self, image)
        pass

    def change_color(self, color):
        self.color = Surface.get_color(color)
        self.vbo['a_color'] = np.tile(self.color, (4, 1))
        self.valid = False

    def calculate_model(self):
        if self.valid and (self.parent is None or self.parent.valid):
            return
        tsl_coords = list(self.coords)
        if self.parent is not None:
            tsl_coords[0] += self.parent.coords[0]
            tsl_coords[1] += self.parent.coords[1]
        self.vbo['a_tsl_xy'] = np.tile([tsl_coords[0], tsl_coords[1]], (4, 1))
        # for i in range(len(self.vbo)):
        #    self.vbo[i][0] = np.dot(self.org_position[i], self.model)
        self.valid = True
        pass

    def set_atlas_info(self, x, y, tex_coords, tex_id):
        self.vbo['a_tex_xy'] = tex_coords
        self.vbo['a_tex_id'] = np.array(4 * [tex_id])
        self.atlas_coords = (x, y)
        self.valid = False

    def copy(self):
        new_surf = Surface(*self.shape)
        new_surf.set_atlas_info(self.atlas_coords[0], self.atlas_coords[1],
                                np.copy(self.vbo['a_tex_xy']), self.vbo['a_tex_id'][0])
        new_surf.color = np.copy(self.color)
        return new_surf

    def get_vbo(self):
        if not self.valid:
            self.calculate_model()
        return self.vbo

    def translate(self, x, y, fixed=False):
        if fixed:
            self.coords[0] = x
            self.coords[1] = y
        else:
            self.coords[0] += x
            self.coords[1] += y
        self.valid = False

    def rotate(self, angle):
        self.angle = angle
        self.valid = False
