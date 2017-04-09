import numpy as np
import vispy
from vispy.util.transforms import ortho
from vispy import gloo
from vispy import app
from scipy import misc
vispy.use('pyqt5', 'gl2')

I = misc.imread('features/Ranged.png')
I2 = misc.imread('cmtabletop/res/tabletop.jpg')
W, H, xx = I.shape
W /= 4
H /= 4



Ncopy = 4
data2 = np.zeros(6 * Ncopy, dtype=[('a_position', np.float32, 4),
                                   ('a_texcoord', np.float32, 2)])
temp_pos = np.array([[0, 0, 0, 1], [W, 0, 0, 1], [0, H, 0, 1], [W, 0, 0, 1], [W, H, 0, 1], [0, H, 0, 1]])
temp_tex = np.array([[0, 1], [1, 1], [0, 0], [1, 1], [1, 0], [0, 0]])
fin_pos = np.copy(temp_pos)
fin_tex = np.copy(temp_tex)

for _ in range(1, Ncopy):
    fin_pos = np.concatenate((fin_pos, temp_pos), axis=0)
    fin_tex = np.concatenate((fin_tex, temp_tex), axis=0)

data2['a_position'] = np.copy(fin_pos)
data2['a_texcoord'] = np.copy(fin_tex)

VERT_SHADER = """
// Uniforms
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform float u_antialias;
// Attributes
attribute vec4 a_position;
attribute vec2 a_texcoord;
// Varyings
varying vec2 v_texcoord;
// Main
void main (void)
{
    v_texcoord = a_texcoord;
    gl_Position = u_projection * u_view * u_model * a_position;
}
"""

FRAG_SHADER = """
uniform sampler2D u_texture;
varying vec2 v_texcoord;
void main()
{
    gl_FragColor = texture2D(u_texture, v_texcoord);
}
"""


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, keys='interactive', size=((1600 * 0.5), (900 * 0.5)))

        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        from cm.cmtabletop.types import surface_vispy
        self.surface = surface_vispy.Surface('features/Ranged.png', scale=1.0)

        self.program['u_texture'] = self.surface.get_tex()
        self.surface.translate(50, 0)
        self.program.bind(self.surface.get_vbo())

        self.view = np.eye(4, dtype=np.float32)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)

        self.program['u_model'] = self.model
        self.program['u_view'] = self.view
        w, h = self.physical_size
        print(w, h)
        self.projection = ortho(0, w, h, 0, -1, 1)
        self.program['u_projection'] = self.projection

        gloo.set_clear_color('white')
        gloo.set_viewport(0, 0, w, h)

        self._timer = app.Timer('auto', connect=self.update, start=True)
        self.once = False
        self.show()

    def on_draw(self, event):
        gloo.clear(color=True, depth=True)
        self.program.draw('triangles')

    def on_mouse_press(self, event):
        mx, my = event.pos
        print("Clicked on:", mx, my)


if __name__ == '__main__':
    c = Canvas()
    c.measure_fps()
    app.run()
