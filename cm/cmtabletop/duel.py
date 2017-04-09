global gameState
global click
global isReleased
isReleased = None
click = None


def createGame(deck, op_deck):
    global gameState
    from cm.cmtabletop import game
    from cm.cmtabletop import screen
    gameState = game.Game((deck, op_deck), screen.scale / 6)


def drawGameState(dest):
    global isReleased, click
    if isReleased:
        click = None
    gameState.draw_scenes(dest, click)
    isReleased = True
    return


def acceptClick(coords_tuple):
    global click, isReleased
    click = coords_tuple
    isReleased = False
    return
