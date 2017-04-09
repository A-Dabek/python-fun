from .actor import Actor
from .display import Surface
from .. import global_vars as GV


class Card(Actor):
    FLAG_DEAD = 1
    FLAG_ALIVE = 0

    path = '/root/PycharmProjects/equations/cm/processed/'
    abl_path = '/root/PycharmProjects/equations/cm/features/'

    def __init__(self, fromname):
        self.name = fromname
        self.hp = 0
        self.hpmax = 0
        self.abl = {}
        self.clr = None
        self.rare = None
        self.type = None
        self.lvl = None
        self.cost = 0
        self.active_action = -1

        cardfile = open(Card.path + self.name + '.txt')
        self.read(cardfile.readlines())
        cardfile.close()

        im = Surface(Card.path + self.name + '.png', shape=(GV.CARD_W, GV.CARD_H))
        Actor.__init__(self, im)

        self.im_abl = [Surface(Card.abl_path + i + '.png', shape=(50, 50)) for i in self.abl.keys()]

        self.used = [False for _ in range(len(list(self.abl.keys())))]

    def show_board_state(self, dest):
        import pygame
        from pygame import transform, font
        self.font = font.SysFont("impact", int(dest.get_height() / 10))

        a = len(list(self.abl.values()))
        w = dest.get_width()
        h = dest.get_height()
        e = w / 4

        dest.fill((150, 150, 150), (0, h - e * 2, w, 2 * e), pygame.BLEND_RGB_SUB)

        for i, im in enumerate(self.im_abl):
            im_sc = pygame.transform.smoothscale(im, (int(e), int(e)))
            if self.used[i]:
                im_sc.fill((150, 150, 150), None, pygame.BLEND_RGB_SUB)
            if self.active_action == i:
                im_sc.fill((50, 50, 50), None, pygame.BLEND_RGB_ADD)
            dest.blit(im_sc, (e * i, h - e))
            label = self.font.render(str(list(self.abl.values())[i]), False, (0, 0, 0))
            xpos = i * e
            ypos = h - label.get_height()
            dest.blit(label, (xpos - 2, ypos))
            dest.blit(label, (xpos, ypos - 2))
            dest.blit(label, (xpos + 2, ypos))
            dest.blit(label, (xpos, ypos + 2))
            label = self.font.render(str(list(self.abl.values())[i]), True, (255, 255, 255))
            dest.blit(label, (xpos, ypos))

        label = self.font.render(str(self.hp), False, (0, 0, 0))
        xpos = 3 * e
        ypos = h - label.get_height()
        dest.blit(label, (xpos - 2, ypos))
        dest.blit(label, (xpos, ypos - 2))
        dest.blit(label, (xpos + 2, ypos))
        dest.blit(label, (xpos, ypos + 2))
        label = self.font.render(str(self.hp), True, (255, 100, 100))
        dest.blit(label, (xpos, ypos))

    def read(self, datalines):
        import re
        for i in datalines:
            fragm = i[i.find(':') + 1: i.find('\n')]
            if i.find('Cost') >= 0:
                self.cost = int(fragm)
            elif i.find('Color') >= 0:
                self.clr = fragm
            elif i.find('Rarity') >= 0:
                self.rare = fragm
            elif i.find('Skill') >= 0:
                number = re.sub('[^0-9]+', '', fragm)
                text = re.sub('[^A-Za-z]+', '', fragm)
                if number == '':
                    number = 0
                self.abl[text] = int(number)
            elif i.find('Type') >= 0:
                self.type = fragm
            elif i.find('Hp') >= 0:
                self.hp = int(fragm)
                self.hpmax = self.hp
            elif i.find('Lvl') >= 0:
                self.lvl = fragm
        return

    def refresh(self):
        for i in range(len(self.used)):
            self.used[i] = False
        self.active_action = -1

    def get_action(self, next=False, wasteit=False):
        if not next:
            i = self.active_action
            if wasteit:
                self.used[i] = True
            return list(self.abl.keys())[i], list(self.abl.values())[i]

        overflow = 0
        while overflow < 2:

            self.active_action += 1
            if self.active_action >= len(self.used):
                overflow += 1
                self.active_action = 0

            i = self.active_action
            if not self.used[i]:
                if list(self.abl.keys())[i] in ['Melee', 'Ranged', 'Magic']:
                    if wasteit:
                        self.used[i] = True
                    return list(self.abl.keys())[i], list(self.abl.values())[i]
        self.active_action = -1
        return None

        # for i, abl in enumerate(self.abl.keys()):
        #     if self.used[i]:
        #         continue
        #     if abl not in ['Melee', 'Ranged', 'Magic']:
        #         continue
        #     if self.active_action == i:
        #         continue
        #     self.active_action = i
        #     if wasteit:
        #         self.used[i] = True
        #     return abl, self.abl[abl]
        # return None

    def apply_action(self, act_type, value):
        if act_type in ['Melee', 'Ranged', 'Magic']:
            self.hp -= value
            if self.hp <= 0:
                return 1
        return 0
