from vispy import gloo
import numpy as np
from scipy import misc


class Surface:
    _textures = {}

    def __init__(self, image_path, shape=None, scale=None):
        self.path = image_path
        if Surface._textures.get(image_path, None) is None:
            image = misc.imread(image_path)
            Surface._textures[image_path] = gloo.Texture2D(image)

        self.texture = Surface._textures[self.path]

        if shape:
            self.shape = shape
        else:
            self.shape = misc.imread(image_path).shape[:2]
        if scale:
            W, H = self.shape
            self.shape = (W*scale, H*scale)

        self.vbo = np.zeros(6, dtype=[('a_position', np.float32, 4),
                                      ('a_texcoord', np.float32, 2)])

        W, H = self.shape
        self.vbo['a_position'] = np.array([[0, 0, 0, 1], [W, 0, 0, 1], [0, H, 0, 1], [W, 0, 0, 1], [W, H, 0, 1], [0, H, 0, 1]])
        self.vbo['a_texcoord'] = np.array([[0, 0], [1, 0], [0, 1], [1, 0], [1, 1], [0, 1]])
        self.m_rotation = np.eye(4, dtype=np.float32)
        self.m_translation = np.eye(4, dtype=np.float32)
        self.model = np.copy(self.vbo)
        self.valid = False
        pass

    def calculate_model(self):
        for i in range(len(self.model)):
            self.model[i][0] = np.dot(self.vbo[i][0], np.dot(self.m_rotation, self.m_translation))
        pass

    def get_shape(self):
        return self.shape

    def get_path(self):
        return self.path

    def copy(self):
        return Surface(self.path, self.shape)

    def get_vbo(self):
        if not self.valid:
            self.calculate_model()
            self.valid = True
        return gloo.VertexBuffer(self.model)

    def get_tex(self):
        return self.texture

    def translate(self, x, y):
        from vispy.util import transforms
        self.m_translation = transforms.translate((x, y, 0.0), dtype=np.float32)
        self.valid = False