from cm.cmtabletop.scenes.scene import Scene
from cm.cmtabletop.types.card import Card
from cm.cmtabletop.types.actor import Actor
from cm.cmtabletop.types.msg import Msg
from .. import screen
import pygame
from pygame import transform


class SceneBoard(Scene):
    im = None
    board_space = 5

    def __init__(self, cards, half):
        self.half = half
        Scene.__init__(self, cards)
        self.select = -1
        self.targeted = SceneBoard.board_space * [0]

    def draw(self, onto):
        for abg_i in range(SceneBoard.board_space):
            x, y = self.get_coords(abg_i)
            onto.blit(SceneBoard.im, (x, y))
        Scene.draw(self, onto)

    def _get_image(self, pos):
        clr = None
        flag = None
        if pos < 0:
            return SceneBoard.im

        if type(self.actors[pos]) == Card:
            im_ret = self.actors[pos].im
            im_ret = transform.smoothscale(im_ret, (int(screen.card_w), int(screen.card_h)))
            self.actors[pos].show_board_state(im_ret)
            if self.targeted[pos] == 1:
                flag = pygame.BLEND_RGB_ADD
                clr = (150, 50, 50, 255)
            elif self.select == pos:
                flag = pygame.BLEND_RGB_ADD
                clr = (50, 150, 50, 255)
        else:
            im_ret = SceneBoard.im.copy()

        if flag is not None and clr is not None:
            im_ret.fill(clr, (0, 0, screen.card_w, screen.card_h-screen.card_w*0.5), flag)
        return im_ret

    def activate(self, active_half, pos):
        print('click', pos)
        if active_half == self.half:
            if type(self.actors[pos]) != Card:
                self.select = pos
                return Msg.emptyToSelf(Msg.FLAG_BOARD_EMPTY_SPOT, (self.half, -1), self.get_coords(self.select))
            else:
                ability = self.actors[pos].get_action(next=True)
                if ability is not None:
                    self.select = pos
                    return Msg.toOpposite(Msg.FLAG_BOARD_CREATURE_READY, ability[0], (self.half, self.select))
        else:
            if self.targeted[pos] == 1:
                return Msg.emptyToOpposite(Msg.FLAG_BOARD_TARGET_CHOOSEN, (self.half, pos), self.get_coords(pos))
        pass

    def react_to(self, msg):
        if msg.flag == Msg.FLAG_SKIP:
            self.select = -1
            self.reset_targets()
            self.reset_cards()

        if self.half == msg.rcv_half:

            if msg.flag == Msg.FLAG_HAND_TO_BOARD:
                self.swap(msg.arg, self.select)
                self.select = -1

            if msg.flag == Msg.FLAG_BOARD_CREATURE_READY:
                self.mark_targets(msg.snd_pos, msg.arg)

            if msg.flag == Msg.FLAG_BOARD_TARGET_CHOOSEN:
                sel_temp = self.select
                self.reset_targets()
                ability = self.actors[sel_temp].get_action(wasteit=True)
                if ability is not None:
                    return Msg(Msg.FLAG_BOARD_CREATURE_ACTION, ability, (self.half, sel_temp),
                               self.get_coords(sel_temp), (msg.snd_half, msg.snd_pos), (msg.snd_x, msg.snd_y))

            if msg.flag == Msg.BOARD_TO_GRAVE:
                self.bury_card(msg.rcv_pos)

            if msg.flag == Msg.FLAG_BOARD_CREATURE_ACTION:
                if self.targeted[msg.rcv_pos] == 0:
                    pass
                flag = self.actors[msg.rcv_pos].apply_action(msg.arg[0], msg.arg[1])
                self.reset_targets()
                if flag == Card.FLAG_DEAD:
                    # self.bury_card(msg.rcv_pos)
                    return Msg.emptyToSelf(Msg.BOARD_TO_GRAVE, (self.half, msg.rcv_pos), self.get_coords(msg.rcv_pos))
        else:
            if msg.flag == Msg.FLAG_BOARD_EMPTY_SPOT:
                self.reset_targets()
        pass

    def swap(self, actor, pos):
        self.actors[pos] = actor
        x, y = self.get_coords(self.select)
        self.actors[pos].slideTo(x, y)

    def get_coords(self, pos, half=-1):
        if half < 0:
            half = self.half
        ygap = [3, 2, 1, 2, 3]
        marginx = screen.bg_w * 0.25
        xgap = (screen.bg_w - marginx * 2 - screen.card_w * SceneBoard.board_space) / \
               (SceneBoard.board_space + 1)
        xpos = marginx + xgap * (pos + 1) + screen.card_w * pos
        ypos = screen.bg_h / 2 + (half - 1) * screen.card_h
        ypos += screen.card_h * (2 * half - 1) * ygap[pos] * 0.1
        return xpos, ypos

    def mark_targets(self, from_pos, atk_type):
        import math
        self.reset_targets()
        covered = type(self.actors[from_pos]) == Card
        variance = math.fabs(from_pos - 2)

        if atk_type == 'Melee':
            if variance == 2:
                return
            if covered:
                self.targeted[from_pos] = 1
                return
        if atk_type == 'Ranged':
            if variance == 0:
                return

        for t_i in range(len(self.targeted)):
            distance = math.fabs(t_i - from_pos)
            if type(self.actors[t_i]) == Card:
                if atk_type == 'Melee':
                    if distance < 2:
                        self.targeted[t_i] = 1
                if atk_type == 'Ranged':
                    if distance > 1:
                        self.targeted[t_i] = 1
                if atk_type == 'Magic':
                    if distance < 2:
                        self.targeted[t_i] = 1
        pass

    def reset_targets(self):
        self.targeted = [0, 0, 0, 0, 0]
        self.select = -1
        pass

    def bury_card(self, pos):
        x, y = self.get_coords(pos)
        self.actors[pos] = Actor(SceneBoard.im.copy())
        self.actors[pos].moveTo(x, y)
        self.targeted[pos] = 0
        pass

    def reset_cards(self):
        for c in self.actors:
            if type(c) == Card:
                c.refresh()
        pass
