import vispy
from vispy import gloo, app

from OpenGL.GL import *

from cm_vispy.cmtabletop import global_vars as GV
from cm_vispy.cmtabletop.scenes.scene_animation import SceneAnimation
from cm_vispy.cmtabletop.scenes.scene_board import SceneBoard
from cm_vispy.cmtabletop.scenes.scene_champ import SceneChamp
from cm_vispy.cmtabletop.scenes.scene_crystal import SceneCrystal
from cm_vispy.cmtabletop.scenes.scene_deck import SceneDeck
from cm_vispy.cmtabletop.scenes.scene_grave import SceneGrave
from cm_vispy.cmtabletop.scenes.scene_hand import SceneHand
from cm_vispy.cmtabletop.types.display import Surface, Display
from cm_vispy.cmtabletop.types.msg import Msg


class Game(app.Canvas):
    # static fields

    def __init__(self, decks):
        app.Canvas.__init__(self, keys='interactive', size=(GV.SCR_W, GV.SCR_H))

        GV.CARD_W, GV.CARD_H = 510 * GV.SCALE * 0.25, 720 * GV.SCALE * 0.25
        GV.CR_W, GV.CR_H = GV.CARD_W * 0.15, GV.CARD_H * 0.15

        # card back
        path = '../../cm/cmtabletop/res/'
        im_temp = Surface(path + 'cardback.jpg', shape=(GV.CARD_W, GV.CARD_H))

        SceneDeck.im = im_temp.copy()
        SceneBoard.im = im_temp.copy()
        SceneChamp.im = im_temp.copy()
        SceneHand.im = im_temp.copy()
        SceneGrave.im = im_temp.copy()

        # background
        self.bg = Surface(path + 'tabletop.jpg', shape=(GV.SCR_W, GV.SCR_H))

        # crystal
        path = '/root/PycharmProjects/equations/cm/features/'
        SceneCrystal.im = Surface(path + 'Crystal.png', shape=(GV.CR_W, GV.CR_H))

        self.scene_anim = SceneAnimation()
        self.scenes = [{'crystal': SceneCrystal(0, 0),
                        'champ': SceneChamp(1, 0),
                        'board': SceneBoard(5, 0),
                        'grave': SceneGrave(0, 0),
                        'deck': SceneDeck(len(decks[0]), 0),
                        'hand': SceneHand(0, 0)},

                       {'champ': SceneChamp(1, 1),
                        'crystal': SceneCrystal(0, 1),
                        'board': SceneBoard(5, 1),
                        'grave': SceneGrave(0, 1),
                        'deck': SceneDeck(len(decks[1]), 1),
                        'hand': SceneHand(0, 1)}]
        self.scenes[0]['deck'].add_cards_list(decks[0])
        self.scenes[1]['deck'].add_cards_list(decks[1])

        self.turn = 0
        self.cmdque = [
            Msg(Msg.FLAG_SKIP, None, (0, 0), None, (1, 1), None),
            Msg(Msg.FLAG_SKIP, None, (1, 0), None, (0, 1), None),
            Msg(Msg.FLAG_DRAW, None, (0, 0), None, (0, 1), None),
            Msg(Msg.FLAG_DRAW, None, (0, 0), None, (0, 1), None),
            Msg(Msg.FLAG_DRAW, None, (1, 0), None, (1, 1), None),
            Msg(Msg.FLAG_DRAW, None, (1, 0), None, (1, 1), None)
        ]

        from vispy.visuals.transforms.transform_system import TransformSystem, STTransform
        from vispy.visuals import TextVisual
        import numpy as np
        self.tran = TransformSystem(self)
        texterino = 'alfabet'

        from scipy import misc
        im = misc.imread('/root/PycharmProjects/equations/cm/processed/Edge.png')
        buffer = gloo.Texture2D((GV.SCR_H, GV.SCR_W, 4), interpolation='linear')
        self.fbo = gloo.FrameBuffer(buffer, gloo.RenderBuffer(buffer.shape[:2]))
        self.text = TextVisual(texterino, font_size=100, anchor_y='top', anchor_x='left')

        import FTGL
        sysargv = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"
        self.fonts = FTGL.PixmapFont(sysargv)
        self.fonts.FaceSize(100, 100)

        gloo.set_state(clear_color='white', blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))

        Display.init_display(*self.physical_size)

        with self.fbo:
            gloo.set_viewport(0, 0, self.fbo.shape[1], self.fbo.shape[0])
            #gloo.set_viewport(0, 0, 5*30*len(texterino), 5*100)
            #gloo.clear(color=False, depth=True)

            # gloo.set_state(blend=True)
            #glRasterPos(-0.5, 0.5)
            #self.fonts.Render("kanapka wiejska")
            self.text.draw(self.tran)
            data = self.fbo.read()

        from matplotlib import pyplot as plt
        print(np.array(data, np.uint8).shape)
        plt.imshow(np.array(data, np.uint8))
        plt.show()
        exit()

        self._timer = app.Timer(1.0 / 300.0, connect=self.update, start=True)
        self.show()

    def on_draw(self, event):
        self.handle_cmd()

        gloo.set_viewport(0, 0, *self.physical_size)
        gloo.clear(color=True)
        gloo.set_state(depth_test=False)

        gloo.clear(color='white', depth=True)

        Display.add(self.bg)
        # self.display.add_surface(self.bg)
        # self.display.que_surface(self.bg)
        self.draw_scenes()
        Display.draw()

        # glRasterPos(-1.0, 0)
        # self.fonts.Render("/usr/share/fonts/truetype/freefont/FreeMono.ttf")
        # import numpy as np
        # Display.program.bind(gloo.VertexBuffer(self.font))
        # Display.program.draw('triangles', indices=gloo.IndexBuffer(np.array([3, 1, 0, 3, 2, 1], np.uint32)))
        # print(self.text._vertices)
        # self.text.draw(self.tran)

    def on_mouse_press(self, event):
        mx, my = event.pos
        for d in [0, 1]:
            for s in GV.SCENES:
                scn = self.scenes[d][s]
                hit = scn.listen(mx, my)
                if hit is not False:
                    answer = scn.activate(self.turn, hit)
                    if answer is not None:
                        self.cmdque.append(answer)
                    return

    def draw_scenes(self):
        for d in [0, 1]:
            for s in GV.SCENES:
                scn = self.scenes[d][s]
                scn.update()
                scn.draw_new2(Display)
                # self.display.draw_atlased()

    def handle_cmd(self):
        while len(self.cmdque) > 0:
            if self.scene_anim.playing():
                break

            msg = self.cmdque[0]
            del self.cmdque[0]

            if msg.flag == Msg.FLAG_SKIP:
                self.turn = 1 - self.turn
            # print(msg.flag)

            for turn in [0, 1]:
                for s in GV.SCENES:
                    reaction = self.scenes[turn][s].react_to(msg)
                    if reaction is not None:
                        self.cmdque.append(reaction)
            self.scene_anim.react_to(msg)
            return


if __name__ == '__main__':
    vispy.use('PyQt5', 'gl2')
    card_names = ['Edge', 'Darkblade', 'Isickle', 'Kurtey', 'Precious', 'Sniperoo', 'Tridentite', 'Kurtey', 'Precious',
                  'Tridentite']
    card_names2 = list(card_names)
    from random import shuffle

    shuffle(card_names2)

    c = Game((card_names, card_names2))
    c.measure_fps()
    app.run()
