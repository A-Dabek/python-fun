class Deck:
    board_capacity = 5

    def __init__(self, card_names):
        self.crystals = 1
        self.spare = 1
        self.pointer = 0
        self.hand = []
        self.size = len(card_names)
        from random import shuffle
        shuffle(card_names)
        from cm.cmtabletop.types import card
        self.cards = [card.Card(i) for i in card_names]
        self.board = [-1 for _ in range(Deck.board_capacity)]
        self.drawACard()
        self.drawACard()

    def getImages(self, scene):
        if scene == 'hand':
            return [self.cards[i].im for i in self.hand]
        if scene == 'board':
            ims = []
            for i in self.board:
                if i >= 0:
                    ims.append(self.cards[i].im)
            return ims
        return []

    def getLen(self, scene):
        if scene == 'deck':
            return len(self.cards) - self.pointer
        if scene == 'hand':
            return len(self.hand)
        if scene == 'board':
            return len(self.board)
        if scene == 'champ':
            return 1
        if scene == 'crystal':
            return self.spare

    def cardFrom(self, scene, position):
        if scene == 'hand':
            return self.cards[self.hand[position]]
        if scene == 'board':
            if self.board[position] >= 0:
                return self.cards[self.board[position]]
        return None

    def endTurn(self):
        self.crystals += 1
        self.spare = self.crystals
        for i in self.board:
            self.cards[i].refresh()
        self.drawACard()

    def drawACard(self):
        if self.pointer < len(self.cards):
            self.cards[self.pointer].draw(len(self.hand))
            self.hand.append(self.pointer)
            self.pointer += 1
        return

    def playACard(self, fromhand, toboard):
        if self.cards[self.hand[fromhand]].cost <= self.spare:
            self.spare -= self.cards[self.hand[fromhand]].cost
            self.board[toboard] = self.hand[fromhand]
            for i, v in enumerate(self.hand):
                if i <= fromhand:
                    continue
                self.cards[v].pos -= 1
            del self.hand[fromhand]
            return 0
        return 1

    def isAffordableFromHand(self, pos):
        if 0 <= pos < len(self.hand):
            return self.spare >= self.cards[self.hand[pos]].cost
        return False

    def getVulnerableTo(self, action):
        vector = [int(i >= 0) for i in self.board]
        return vector

    def getBoardSpots(self):
        vector = [int(i < 0) for i in self.board]
        return vector

    def updateBoardState(self):
        for k, v in enumerate(self.board):
            if v >= 0:
                if self.cards[v].hp <= 0:
                    self.board[k] = -1
                    self.cards[v].discard()
        return
