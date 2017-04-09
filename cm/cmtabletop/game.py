from cm.cmtabletop.scenes.scene_board import SceneBoard
from cm.cmtabletop.scenes.scene_hand import SceneHand
from cm.cmtabletop.scenes.scene_deck import SceneDeck
from cm.cmtabletop.scenes.scene_champ import SceneChamp
from cm.cmtabletop.scenes.scene_crystal import SceneCrystal
from cm.cmtabletop.scenes.scene_animation import SceneAnimation
from cm.cmtabletop.scenes.scene_grave import SceneGrave
from pygame import transform, image
from cm.cmtabletop import screen


class Game:
    # static fields
    board_capacity = 5
    scenes = ['crystal', 'champ', 'deck', 'board', 'grave', 'hand']

    def __init__(self, decks, scale):
        # card back
        path = './cmtabletop/res/'
        im_temp = image.load(path + 'cardback.jpg').convert_alpha()
        screen.card_w = int(im_temp.get_width() * scale)
        screen.card_h = int(im_temp.get_height() * scale)
        im_temp = transform.smoothscale(im_temp, (screen.card_w, screen.card_h))
        SceneDeck.im = im_temp.copy()
        SceneBoard.im = im_temp.copy()
        SceneChamp.im = im_temp.copy()
        SceneHand.im = im_temp.copy()
        SceneGrave.im = im_temp.copy()

        # background
        im_temp = image.load(path + 'tabletop.jpg').convert()
        self.bg = transform.smoothscale(im_temp, (screen.w, screen.h))
        screen.bg_w = self.bg.get_width()
        screen.bg_h = self.bg.get_height()

        # crystal
        path = '/root/PycharmProjects/equations/cm/features/'
        im_temp = image.load(path + 'Crystal.png').convert_alpha()
        SceneCrystal.im = transform.smoothscale(im_temp, (int(screen.card_w * 0.15), int(screen.card_h * 0.15)))
        screen.cr_w = SceneCrystal.im.get_width()
        screen.cr_h = SceneCrystal.im.get_height()

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
        from .types.msg import Msg
        self.cmdque = [
            Msg(Msg.FLAG_SKIP, None, (0, 0), None, (1, 1), None),
            Msg(Msg.FLAG_SKIP, None, (1, 0), None, (0, 1), None),
            Msg(Msg.FLAG_DRAW, None, (0, 0), None, (0, 1), None),
            Msg(Msg.FLAG_DRAW, None, (0, 0), None, (0, 1), None),
            Msg(Msg.FLAG_DRAW, None, (1, 0), None, (1, 1), None),
            Msg(Msg.FLAG_DRAW, None, (1, 0), None, (1, 1), None)
        ]
        self.mode = 'observer'
        self.select = None

    def draw_scenes(self, dest, click):
        self.handleCommands()

        dest.blit(self.bg, (0, 0))
        for d in [0, 1]:
            for s in Game.scenes:
                scn = self.scenes[d][s]
                scn.update()
                scn.draw(dest)
        self.scene_anim.update()
        self.scene_anim.draw(dest)

        if click is not None:
            mx, my = click
            for d in [0, 1]:
                for s in Game.scenes:
                    scn = self.scenes[d][s]
                    print(s)
                    hit = scn.listen(mx, my)
                    if hit is not False:
                        answer = scn.activate(self.turn, hit)
                        if answer is not None:
                            self.cmdque.append(answer)
                        return
            self.select = None

    def handleCommands(self):
        while len(self.cmdque) > 0:
            if self.scene_anim.playing():
                break

            from .types.msg import Msg
            msg = self.cmdque[0]
            del self.cmdque[0]

            if msg.flag == Msg.FLAG_SKIP:
                self.turn = 1 - self.turn

            for turn in [0, 1]:
                for s in Game.scenes:
                    reaction = self.scenes[turn][s].react_to(msg)
                    if reaction is not None:
                        self.cmdque.append(reaction)
            self.scene_anim.react_to(msg)
            return
