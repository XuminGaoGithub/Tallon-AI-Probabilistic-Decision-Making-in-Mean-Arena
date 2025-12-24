# game.py



from world import World
from tallon  import Tallon
from arena import Arena
import utils
import time

# How we set the game up. Create a world, then connect player and
# display to it.
#gameWorld = World()
#player = Tallon(gameWorld)
#display = Arena(gameWorld)

# Uncomment this for a printout of world state at the start
#utils.printGameState(gameWorld)


# Now run...
i=1
win_number = 0
win_rate = 0
all_score = 0
average_score = 0

while i<=1:

    gameWorld = World()
    player = Tallon(gameWorld)
    display = Arena(gameWorld)
    #gameWorld.isEnded() == None

    while not(gameWorld.isEnded()):
        #time.sleep(5)
        Bonus_number=gameWorld.updateTallon(player.makeMove())
        gameWorld.updateMeanie()
        gameWorld.updateClock()
        gameWorld.addMeanie()
        gameWorld.updateScore()
        display.update()
        #time.sleep(1)
        # Uncomment this for a printout of world state every step
        #utils.printGameState(gameWorld)

    print("Final score:", gameWorld.getScore())
    print("Bonus_number:", Bonus_number)
    print('gameWorld.isEnded()', gameWorld.isEnded())
    print('\n')

    if Bonus_number==0:
        win_number = win_number+1
    win_rate = win_number/float(i)
    all_score = all_score+gameWorld.getScore()
    average_score = all_score/i
    print('win_number:',win_number)
    print('win_rate: %.4f' % round(win_rate,4))
    print('all_score:', all_score)
    print('average_score:', round(average_score))
    #time.sleep(10)
    print('\n')

    if gameWorld.isEnded() == True:
        i=i+1
        #time.sleep(0.5)

