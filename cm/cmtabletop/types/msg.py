class Msg:

    BOARD_TO_GRAVE = "to grave"
    FLAG_CHAMP_EMPTY_SPOT = "empty champ spot"
    FLAG_HAND_TO_CHAMP = "hand to champ"
    FLAG_ANIMATE = "animate"
    FLAG_CRYSTALS_SPARE = "crystal_spare"
    FLAG_BOARD_TARGET_CHOOSEN = "target_choosen"
    FLAG_BOARD_CREATURE_READY = "creature_ready"
    FLAG_BOARD_CREATURE_ACTION = "creature_action"
    FLAG_DRAW = "draw"
    FLAG_SKIP = "skip"
    FLAG_DECK_TO_HAND = "deck to hand"
    FLAG_HAND_TO_BOARD = "hand to board"
    FLAG_BOARD_EMPTY_SPOT = "empty spot"

    @staticmethod
    def toOpposite(flag, arg, snd_hp, snd_xy=None):
        return Msg(flag, arg, snd_hp, snd_xy, (1-snd_hp[0], snd_hp[1]), None)

    @staticmethod
    def emptyToOpposite(flag, snd_hp, snd_xy=None):
        return Msg(flag, None, snd_hp, snd_xy, (1-snd_hp[0], snd_hp[1]), None)
        pass

    @staticmethod
    def toSelf(flag, arg, snd_hp, snd_xy=None):
        return Msg(flag, arg, snd_hp, snd_xy, snd_hp, snd_xy)

    @staticmethod
    def emptyToSelf(flag, snd_hp, snd_xy=None):
        return Msg(flag, None, snd_hp, snd_xy, snd_hp, snd_xy)

    @staticmethod
    def toOppositeAdjacent(flag, arg, snd_hp, snd_xy, rcv_pos, rcv_xy=None):
        return Msg(flag, arg, snd_hp, snd_xy, (1-snd_hp[0], rcv_pos), rcv_xy)

    @staticmethod
    def toAdjacent(flag, arg, snd_hp, snd_xy, rcv_pos, rcv_xy=None):
        return Msg(flag, arg, snd_hp, snd_xy, (snd_hp[0], rcv_pos), rcv_xy)

    def __init__(self, flag=None, arg=None, snd_hp=None, snd_xy=None, rcv_hp=None, rcv_xy=None):
        if snd_xy is not None:
            self.snd_x = snd_xy[0]
            self.snd_y = snd_xy[1]
        else:
            self.snd_x = -1
            self.snd_y = -1
        if snd_hp is not None:
            self.snd_half = snd_hp[0]
            self.snd_pos = snd_hp[1]
        else:
            self.snd_half = -1
            self.snd_ypos = -1
        self.flag = flag
        self.arg = arg
        if rcv_xy is not None:
            self.rcv_x = rcv_xy[0]
            self.rcv_y = rcv_xy[1]
        else:
            self.rcv_x = -1
            self.rcv_y = -1
        if rcv_hp is not None:
            self.rcv_half = rcv_hp[0]
            self.rcv_pos = rcv_hp[1]
        else:
            self.rcv_half = -1
            self.rcv_pos = -1

    def snd_data(self, half, pos, x, y):
        self.snd_half = half
        self.snd_pos = pos
        self.snd_x = x
        self.snd_y = y

    def rcv_data(self, half, pos, x, y):
        self.rcv_half = half
        self.rcv_pos = pos
        self.rcv_x = x
        self.rcv_y = y