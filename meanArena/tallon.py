# tallon.py

import world
import random
import utils
from utils import Directions

#
import config
import numpy as np
import time
import math
import mdptoolbox
import random


class Tallon():

    def __init__(self, arena):

        # Make a copy of the world an attribute, so that Tallon can
        # query the state of the world
        self.gameWorld = arena

        # What moves are possible.
        self.moves = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]
        self.number = 0
        #self.number = self.number + 1
        # print('self.number',self.number)
        self.number_allMeanies = len(self.gameWorld.getMeanieLocation())
        print('self.number_allMeanies:',self.number_allMeanies)

        self.value = 1 / float(config.worldLength * config.worldBreadth)
        self.init_belief = np.full((self.number_allMeanies,len(self.moves),
                                    config.worldLength * config.worldBreadth,
                                    config.worldLength * config.worldBreadth), self.value)  # init_belief


        self.old_belief  = np.full((self.number_allMeanies,len(self.moves), config.worldLength * config.worldBreadth, config.worldLength * config.worldBreadth), 0.0)
        self.updated_belief = np.full((self.number_allMeanies,len(self.moves), config.worldLength * config.worldBreadth, config.worldLength * config.worldBreadth), 0.0)


    def k_largest_index_argsort(self, a, k): #get the max_k from a
        idx = np.argsort(a.ravel())[:-k - 1:-1]
        return np.column_stack(np.unravel_index(idx, a.shape))

    def makeMove(self):
        # This is the function you need to define

        # For now we have a placeholder, which always moves Tallon
        # directly towards any existing bonuses. It ignores Meanies
        # and pits.
        # 
        # Get the location of the Bonuses.
        allBonuses = self.gameWorld.getBonusLocation()


        if config.partialVisibility: # partially Observable

            Bonuses = self.gameWorld.getBonusLocation()
            Meanies = self.gameWorld.getMeanieLocation()
            Pits = self.gameWorld.getPitsLocation()

            observable_number = len(Bonuses)+len(Meanies)+len(Pits)
            print('observable_number',observable_number)
            if observable_number !=0:
                MyPolicy = self.decision_PartiallyObservable()
                print('MyPolicy', MyPolicy)
                print('\n')
                if MyPolicy == 0:
                    return Directions.EAST
                if MyPolicy == 1:
                    return Directions.WEST
                if MyPolicy == 2:
                    return Directions.NORTH
                if MyPolicy == 3:
                    return Directions.SOUTH
            else: #prevent stuck when there is no any observable stuffs
                random_action=random.sample([0,1,2,3], 1)
                print('random_action',random_action[0])
                if random_action[0]==0:
                    return Directions.EAST
                if random_action[0]==1:
                    return Directions.WEST
                    # If not at the same y coordinate, reduce the difference
                if random_action[0]==2:
                    return Directions.NORTH
                if random_action[0]==3:
                    return Directions.SOUTH

        else:  # Fully Observable

            # if there are still bonuses, move towards the next one.

            if len(allBonuses) > 0:
                #
                MyPolicy = self.decision_FullyObservable()
                print('MyPolicy', MyPolicy)
                #time.sleep(3)
                print('\n')
                if MyPolicy == 0:
                    return Directions.EAST
                if MyPolicy == 1:
                    return Directions.WEST
                if MyPolicy == 2:
                    return Directions.NORTH
                if MyPolicy == 3:
                    return Directions.SOUTH

                '''
                #
                nextBonus = allBonuses[0]
                myPosition = self.gameWorld.getTallonLocation()
                # If not at the same x coordinate, reduce the difference
                if nextBonus.x > myPosition.x:
                    return Directions.EAST
                if nextBonus.x < myPosition.x:
                    return Directions.WEST
                # If not at the same y coordinate, reduce the difference
                if nextBonus.y < myPosition.y:
                    return Directions.NORTH
                if nextBonus.y > myPosition.y:
                    return Directions.SOUTH
            # if there are no more bonuses, Tallon doesn't move
            '''


    def decision_PartiallyObservable(self):

        myPosition = self.gameWorld.getTallonLocation()
        allBonuses = self.gameWorld.getBonusLocation()
        allMeanies = self.gameWorld.getMeanieLocation()
        allPits = self.gameWorld.getPitsLocation()
        #print('type(allBonuses):',type(allBonuses))

        all_Bonuses = [] #(x,y) list
        all_Meanies = []
        all_Pits = []
        all_MeaniesAndPits = []  #(x,y) list
        print('myPosition:', (myPosition.x, myPosition.y))
        print('\n')
        for i in range(len(allBonuses)):
            print('Bonuse' + str(i) + ':', (allBonuses[i].x, allBonuses[i].y))
            all_Bonuses.append([allBonuses[i].x, allBonuses[i].y])
        print('all_Bonuses:', all_Bonuses)
        print('\n')

        for i in range(len(allMeanies)):
            print('Meanie' + str(i) + ':', (allMeanies[i].x, allMeanies[i].y))
            if [allMeanies[i].x, allMeanies[i].y] not in all_Meanies:
                all_Meanies.append([allMeanies[i].x, allMeanies[i].y]) #
            if [allMeanies[i].x, allMeanies[i].y] not in all_MeaniesAndPits:
                all_MeaniesAndPits.append([allMeanies[i].x, allMeanies[i].y]) # exclude the overlap between Meanies and Pits
        print('\n')
        for i in range(len(allPits)):
            print('Pit' + str(i) + ':', (allPits[i].x, allPits[i].y))
            if [allPits[i].x, allPits[i].y] not in all_Pits:
                all_Pits.append([allPits[i].x, allPits[i].y]) #
            if [allPits[i].x, allPits[i].y] not in all_MeaniesAndPits:
                all_MeaniesAndPits.append([allPits[i].x, allPits[i].y]) # exclude the overlap between Meanies and Pits
        print('\n')
        print('all_Meanies:', all_Meanies)
        print('all_Pits:', all_Pits)
        print('all_MeaniesAndPits:', all_MeaniesAndPits)
        print('\n')


        A = len(self.moves) #Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST
        S= (config.worldLength * config.worldBreadth)


        states = np.zeros((config.worldBreadth,config.worldLength))
        N=0
        for y in range(config.worldBreadth):
            for x in range(config.worldLength):
                states[y,x]= N
                N = N + 1
        print('states: \n', states)
        #print('type(states[1,0]): \n', type(states[0,0]))
        print('\n')

        '''Transition'''
        # The probability array has shape (A, S, S), where A are actions and S
        # are states. So A arrays, each S x S, ie for each action specify the
        # transitions probabilities of reaching the second state by applying
        # that action in the first state.
        #
        # The probability array contains 4 sub-arrays, one for each action.
        # Each of these is SxS.
        #
        # the action model: directionProbability% of the time the agent moves as intended.
        # 1-directionProbability% of the time the agent moves perpendicular to the intended direction,
        # Half the time to the left, half the time to the right.
        # P = np.zeros((A, S, S))
        P = np.zeros((A, S, S))
        Meanies_directionProbability = 0.95
        for a in range(A):  # right,left,up,down
            for y in range(config.worldBreadth):
                for x in range(config.worldLength):
                    P_y = states[y, x]  # P_y， get index from list of states

                    # right
                    if a == 0:
                        if ((x + 1 <= (config.worldLength - 1)) and (
                                y <= (config.worldBreadth - 1))):  # moves as intended
                            P_x = states[y, x + 1]  # state
                            # print('1-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = Meanies_directionProbability
                        else:
                            P_x = states[y, x]
                            # print('1-2:P_y, P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = Meanies_directionProbability

                        if ((0 <= x) and (0 <= (y - 1))):  # up,moves perpendicular to the intended direction
                            P_x = states[y - 1, x]
                            # print('2-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1 - Meanies_directionProbability) / 2.0
                        else:
                            # if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            # print('2-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = P[a, int(P_y), int(P_x)] + (
                                    1 - Meanies_directionProbability) / 2.0

                        if ((x <= (config.worldLength - 1)) and (y + 1 <= (
                                config.worldBreadth - 1))):  # down,moves perpendicular to the intended direction
                            P_x = states[y + 1, x]
                            # print('3-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1 - Meanies_directionProbability) / 2.0
                        else:
                            # if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            # print('3-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = P[a, int(P_y), int(P_x)] + (
                                    1 - Meanies_directionProbability) / 2.0
                    # print('P_right:',P[0,int(P_y),:])

                    # left
                    if a == 1:
                        if ((0 <= x - 1) and (0 <= y)):  # moves as intended
                            P_x = states[y, x - 1]  # state
                            # print('1-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = Meanies_directionProbability
                        else:
                            # if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            # print('1-2:P_y, P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = Meanies_directionProbability

                        if ((0 <= x) and (0 <= (y - 1))):  # up,moves perpendicular to the intended direction
                            P_x = states[y - 1, x]
                            # print('2-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1 - Meanies_directionProbability) / 2.0
                        else:
                            # if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            # print('2-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = P[a, int(P_y), int(P_x)] + (
                                    1 - Meanies_directionProbability) / 2.0

                        if ((x <= (config.worldLength - 1)) and (y + 1 <= (
                                config.worldBreadth - 1))):  # down,moves perpendicular to the intended direction
                            P_x = states[y + 1, x]
                            # print('3-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1 - Meanies_directionProbability) / 2.0
                        else:
                            # if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            # print('3-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = P[a, int(P_y), int(P_x)] + (
                                    1 - Meanies_directionProbability) / 2.0
                    # print('P_left:',P[1,int(P_y),:])

                    # up
                    if a == 2:
                        if ((0 <= x) and (0 <= y - 1)):  # moves as intended
                            P_x = states[y - 1, x]  # state
                            # print('1-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = Meanies_directionProbability
                        else:
                            # if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            # print('1-2:P_y, P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = Meanies_directionProbability

                        if ((x + 1 <= (config.worldLength - 1)) and (
                                y <= (config.worldBreadth - 1))):  # right,moves perpendicular to the intended direction
                            P_x = states[y, x + 1]
                            # print('2-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1 - Meanies_directionProbability) / 2.0
                        else:
                            # if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            # print('2-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = P[a, int(P_y), int(P_x)] + (
                                    1 - Meanies_directionProbability) / 2.0

                        if ((0 <= x - 1) and (0 <= y)):  # left,moves perpendicular to the intended direction
                            P_x = states[y, x - 1]
                            # print('3-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1 - Meanies_directionProbability) / 2.0
                        else:
                            # if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            # print('3-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = P[a, int(P_y), int(P_x)] + (
                                    1 - Meanies_directionProbability) / 2.0
                    # print('P_up:',P[2,int(P_y),:])

                    # down
                    if a == 3:
                        if ((x <= (config.worldLength - 1)) and (
                                (y + 1) <= (config.worldBreadth - 1))):  # moves as intended
                            P_x = states[y + 1, x]  # state
                            # print('1-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = Meanies_directionProbability
                        else:
                            # if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            # print('1-2:P_y, P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = Meanies_directionProbability

                        if ((x + 1 <= (config.worldLength - 1)) and (
                                y <= (config.worldBreadth - 1))):  # right,moves perpendicular to the intended direction
                            P_x = states[y, x + 1]
                            # print('2-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1 - Meanies_directionProbability) / 2.0
                        else:
                            # if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            # print('2-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = P[a, int(P_y), int(P_x)] + (
                                    1 - Meanies_directionProbability) / 2.0

                        if ((0 <= x - 1) and (0 <= y)):  # left,moves perpendicular to the intended direction
                            P_x = states[y, x - 1]
                            # print('3-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1 - Meanies_directionProbability) / 2.0
                        else:
                            # if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            # print('3-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = P[a, int(P_y), int(P_x)] + (
                                    1 - Meanies_directionProbability) / 2.0
                    # print('P_down:',P[3,int(P_y),:])

        # print('P: \n', P)
        # print('\n')
        transition = P
        # print('transition[0]: \n', transition[0])
        print('\n')


        '''sensor'''
        #P = np.full((A, S, S), self.value)  # sensor
        P = np.full((len(all_Meanies),A, S, S), self.value)  # sensor for every Meanie
        # print('init_sensor:',P)
        for m in range(len(all_Meanies)):
            for a in range(A):  # right,left,up,down
                for y in range(config.worldBreadth):
                    for x in range(config.worldLength):

                        # top_left
                        if (all_Meanies[m][0] == 0) and (all_Meanies[m][1] == 0):
                            x1 = all_Meanies[m][0] + 1
                            y1 = all_Meanies[m][1]
                            x2 = all_Meanies[m][0]
                            y2 = all_Meanies[m][1] + 1
                            distance0 = math.sqrt(
                                ((myPosition.x - all_Meanies[m][0]) * (myPosition.x - all_Meanies[m][0])) + \
                                ((myPosition.x - all_Meanies[m][1]) * (myPosition.x - all_Meanies[m][1])))
                            distance1 = math.sqrt(((myPosition.x - x1) * (myPosition.x - x1)) + \
                                                  ((myPosition.x - y1) * (myPosition.x - y1)))
                            distance2 = math.sqrt(((myPosition.x - x2) * (myPosition.x - x2)) + \
                                                  ((myPosition.x - y2) * (myPosition.x - y2)))
                            min_distance = min(distance0, distance1, distance2)
                            if min_distance == distance0:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.8
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                            if min_distance == distance1:
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.3
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.6
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                            if min_distance == distance2:
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.3
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.6
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                            if min_distance == distance1 and min_distance == distance2:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.7
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.15
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.15
                            # print('min_distance:',min_distance,distance0,distance1,distance2)

                        # bottom_left
                        if (all_Meanies[m][0] == 0) and (all_Meanies[m][1] == (config.worldBreadth - 1)):
                            x1 = all_Meanies[m][0] + 1
                            y1 = all_Meanies[m][1]
                            x2 = all_Meanies[m][0]
                            y2 = all_Meanies[m][1] - 1

                            distance0 = math.sqrt(
                                ((myPosition.x - all_Meanies[m][0]) * (myPosition.x - all_Meanies[m][0])) + \
                                ((myPosition.x - all_Meanies[m][1]) * (myPosition.x - all_Meanies[m][1])))
                            distance1 = math.sqrt(((myPosition.x - x1) * (myPosition.x - x1)) + \
                                                  ((myPosition.x - y1) * (myPosition.x - y1)))
                            distance2 = math.sqrt(((myPosition.x - x2) * (myPosition.x - x2)) + \
                                                  ((myPosition.x - y2) * (myPosition.x - y2)))
                            min_distance = min(distance0, distance1, distance2)
                            if min_distance == distance0:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.8
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                            if min_distance == distance1:
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.3
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.6
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                            if min_distance == distance2:
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.3
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.6
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                            if min_distance == distance1 and min_distance == distance2:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.7
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.15
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.15
                            # print('min_distance:', min_distance, distance0, distance1, distance2)

                        # top_right
                        elif (all_Meanies[m][0] == (config.worldLength - 1)) and (all_Meanies[m][1] == 0):
                            x1 = all_Meanies[m][0]
                            y1 = all_Meanies[m][1] + 1
                            x2 = all_Meanies[m][0] - 1
                            y2 = all_Meanies[m][1]
                            distance0 = math.sqrt(
                                ((myPosition.x - all_Meanies[m][0]) * (myPosition.x - all_Meanies[m][0])) + \
                                ((myPosition.x - all_Meanies[m][1]) * (myPosition.x - all_Meanies[m][1])))
                            distance1 = math.sqrt(((myPosition.x - x1) * (myPosition.x - x1)) + \
                                                  ((myPosition.x - y1) * (myPosition.x - y1)))
                            distance2 = math.sqrt(((myPosition.x - x2) * (myPosition.x - x2)) + \
                                                  ((myPosition.x - y2) * (myPosition.x - y2)))
                            min_distance = min(distance0, distance1, distance2)
                            if min_distance == distance0:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.8
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                            if min_distance == distance1:
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.3
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.6
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                            if min_distance == distance2:
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.3
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.6
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                            if min_distance == distance1 and min_distance == distance2:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.7
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.15
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.15
                            # print('min_distance:', min_distance, distance0, distance1, distance2)

                        # bottom_right
                        elif (all_Meanies[m][0] == (config.worldLength - 1)) and (
                                all_Meanies[m][1] == (config.worldBreadth - 1)):
                            x1 = all_Meanies[m][0]
                            y1 = all_Meanies[m][1] - 1
                            x2 = all_Meanies[m][0] - 1
                            y2 = all_Meanies[m][1]
                            distance0 = math.sqrt(
                                ((myPosition.x - all_Meanies[m][0]) * (myPosition.x - all_Meanies[m][0])) + \
                                ((myPosition.x - all_Meanies[m][1]) * (myPosition.x - all_Meanies[m][1])))
                            distance1 = math.sqrt(((myPosition.x - x1) * (myPosition.x - x1)) + \
                                                  ((myPosition.x - y1) * (myPosition.x - y1)))
                            distance2 = math.sqrt(((myPosition.x - x2) * (myPosition.x - x2)) + \
                                                  ((myPosition.x - y2) * (myPosition.x - y2)))
                            min_distance = min(distance0, distance1, distance2)
                            if min_distance == distance0:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.8
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                            if min_distance == distance1:
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.3
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.6
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                            if min_distance == distance2:
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.3
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.6
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                            if min_distance == distance1 and min_distance == distance2:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.7
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.15
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.15
                            # print('min_distance:', min_distance, distance0, distance1, distance2)

                        # x=0 and not ext_boundry_point
                        elif (all_Meanies[m][0] == 0) and (all_Meanies[m][1] != 0) and \
                                (all_Meanies[m][1] != (config.worldBreadth - 1)):
                            x1 = all_Meanies[m][0]
                            y1 = all_Meanies[m][1] - 1
                            x2 = all_Meanies[m][0]
                            y2 = all_Meanies[m][1] + 1
                            x3 = all_Meanies[m][0] + 1
                            y3 = all_Meanies[m][1]
                            distance0 = math.sqrt(
                                ((myPosition.x - all_Meanies[m][0]) * (myPosition.x - all_Meanies[m][0])) + \
                                ((myPosition.x - all_Meanies[m][1]) * (myPosition.x - all_Meanies[m][1])))
                            distance1 = math.sqrt(((myPosition.x - x1) * (myPosition.x - x1)) + \
                                                  ((myPosition.x - y1) * (myPosition.x - y1)))
                            distance2 = math.sqrt(((myPosition.x - x2) * (myPosition.x - x2)) + \
                                                  ((myPosition.x - y2) * (myPosition.x - y2)))
                            distance3 = math.sqrt(((myPosition.x - x3) * (myPosition.x - x3)) + \
                                                  ((myPosition.x - y3) * (myPosition.x - y3)))
                            min_distance = min(distance0, distance1, distance2,distance3)
                            if min_distance == distance0:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.7
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                                P_y = states[y3, x3]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                            if min_distance == distance1:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.5
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.3
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y3, x3]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                            if min_distance == distance2:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.5
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.3
                                P_y = states[y3, x3]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                            if min_distance == distance3:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.5
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y3, x3]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.3
                            # print('min_distance:', min_distance, distance0, distance1, distance2)

                        # y=0 and not ext_boundry_points
                        elif (all_Meanies[m][1] == 0) and (all_Meanies[m][0] != 0) and \
                                (all_Meanies[m][0] != (config.worldLength - 1)):
                            x1 = all_Meanies[m][0] - 1
                            y1 = all_Meanies[m][1]
                            x2 = all_Meanies[m][0] + 1
                            y2 = all_Meanies[m][1] + 1
                            x3 = all_Meanies[m][0]
                            y3 = all_Meanies[m][1] + 1
                            distance0 = math.sqrt(
                                ((myPosition.x - all_Meanies[m][0]) * (myPosition.x - all_Meanies[m][0])) + \
                                ((myPosition.x - all_Meanies[m][1]) * (myPosition.x - all_Meanies[m][1])))
                            distance1 = math.sqrt(((myPosition.x - x1) * (myPosition.x - x1)) + \
                                                  ((myPosition.x - y1) * (myPosition.x - y1)))
                            distance2 = math.sqrt(((myPosition.x - x2) * (myPosition.x - x2)) + \
                                                  ((myPosition.x - y2) * (myPosition.x - y2)))
                            distance3 = math.sqrt(((myPosition.x - x3) * (myPosition.x - x3)) + \
                                                  ((myPosition.x - y3) * (myPosition.x - y3)))
                            min_distance = min(distance0, distance1, distance2, distance3)
                            if min_distance == distance0:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.7
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y3, x3]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                            if min_distance == distance1:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.5
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.3
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y3, x3]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                            if min_distance == distance2:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.5
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.3
                                P_y = states[y3, x3]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                            if min_distance == distance3:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.5
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y3, x3]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.3
                            # print('min_distance:', min_distance, distance0, distance1, distance2)

                        # X=MAX and not ext_boundry_points
                        elif (all_Meanies[m][0] == (config.worldLength - 1)) and (all_Meanies[m][1] != 0) and \
                                (all_Meanies[m][1] != (config.worldBreadth - 1)):
                            x1 = all_Meanies[m][0]
                            y1 = all_Meanies[m][1] - 1
                            x2 = all_Meanies[m][0]
                            y2 = all_Meanies[m][1] + 1
                            x3 = all_Meanies[m][0] - 1
                            y3 = all_Meanies[m][1]
                            distance0 = math.sqrt(
                                ((myPosition.x - all_Meanies[m][0]) * (myPosition.x - all_Meanies[m][0])) + \
                                ((myPosition.x - all_Meanies[m][1]) * (myPosition.x - all_Meanies[m][1])))
                            distance1 = math.sqrt(((myPosition.x - x1) * (myPosition.x - x1)) + \
                                                  ((myPosition.x - y1) * (myPosition.x - y1)))
                            distance2 = math.sqrt(((myPosition.x - x2) * (myPosition.x - x2)) + \
                                                  ((myPosition.x - y2) * (myPosition.x - y2)))
                            distance3 = math.sqrt(((myPosition.x - x3) * (myPosition.x - x3)) + \
                                                  ((myPosition.x - y3) * (myPosition.x - y3)))
                            min_distance = min(distance0, distance1, distance2, distance3)
                            if min_distance == distance0:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.7
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y3, x3]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                            if min_distance == distance1:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.5
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.3
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y3, x3]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                            if min_distance == distance2:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.5
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.3
                                P_y = states[y3, x3]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                            if min_distance == distance3:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.5
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y3, x3]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.3
                            # print('min_distance:', min_distance, distance0, distance1, distance2)

                        # Y=MAX and not ext_boundry_points
                        elif (all_Meanies[m][1] == (config.worldBreadth - 1)) and (all_Meanies[m][0] != 0) and \
                                (all_Meanies[m][0] != (config.worldLength - 1)):
                            x1 = all_Meanies[m][0] - 1
                            y1 = all_Meanies[m][1]
                            x2 = all_Meanies[m][0] + 1
                            y2 = all_Meanies[m][1]
                            x3 = all_Meanies[m][0]
                            y3 = all_Meanies[m][1] - 1
                            distance0 = math.sqrt(
                                ((myPosition.x - all_Meanies[m][0]) * (myPosition.x - all_Meanies[m][0])) + \
                                ((myPosition.x - all_Meanies[m][1]) * (myPosition.x - all_Meanies[m][1])))
                            distance1 = math.sqrt(((myPosition.x - x1) * (myPosition.x - x1)) + \
                                                  ((myPosition.x - y1) * (myPosition.x - y1)))
                            distance2 = math.sqrt(((myPosition.x - x2) * (myPosition.x - x2)) + \
                                                  ((myPosition.x - y2) * (myPosition.x - y2)))
                            distance3 = math.sqrt(((myPosition.x - x3) * (myPosition.x - x3)) + \
                                                  ((myPosition.x - y3) * (myPosition.x - y3)))
                            min_distance = min(distance0, distance1, distance2, distance3)
                            if min_distance == distance0:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.7
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y3, x3]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                            if min_distance == distance1:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.5
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.3
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y3, x3]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                            if min_distance == distance2:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.5
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.3
                                P_y = states[y3, x3]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                            if min_distance == distance3:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.5
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.1
                                P_y = states[y3, x3]  # P_y， get index from list of states
                                P[m, :, int(P_y), :] = 0.3
                            # print('min_distance:', min_distance, distance0, distance1, distance2)

                        # not the boudry points
                        #if (all_Meanies[m][0]) != 0 and (all_Meanies[m][0]) != (config.worldLength - 1) \
                                #and (all_Meanies[m][1]) != 0 and (all_Meanies[m][1]) != (config.worldBreadth - 1):
                        else:
                            x1 = all_Meanies[m][0] - 1
                            y1 = all_Meanies[m][1]
                            x2 = all_Meanies[m][0] + 1
                            y2 = all_Meanies[m][1]
                            x3 = all_Meanies[m][0]
                            y3 = all_Meanies[m][1] - 1
                            x4 = all_Meanies[m][0]
                            y4 = all_Meanies[m][1] + 1
                            distance0 = math.sqrt(
                                ((myPosition.x - all_Meanies[m][0]) * (myPosition.x - all_Meanies[m][0])) + \
                                ((myPosition.x - all_Meanies[m][1]) * (myPosition.x - all_Meanies[m][1])))
                            distance1 = math.sqrt(((myPosition.x - x1) * (myPosition.x - x1)) + \
                                                  ((myPosition.x - y1) * (myPosition.x - y1)))
                            distance2 = math.sqrt(((myPosition.x - x2) * (myPosition.x - x2)) + \
                                                  ((myPosition.x - y2) * (myPosition.x - y2)))
                            distance3 = math.sqrt(((myPosition.x - x3) * (myPosition.x - x3)) + \
                                                  ((myPosition.x - y3) * (myPosition.x - y3)))
                            distance4 = math.sqrt(((myPosition.x - x4) * (myPosition.x - x4)) + \
                                                  ((myPosition.x - y4) * (myPosition.x - y4)))
                            min_distance = min(distance0, distance1, distance2, distance3, distance4)
                            if min_distance == distance0:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.5
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                                P_y = states[y3, x3]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                                P_y = states[y4, x4]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                            if min_distance == distance1:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.5
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.2
                                #print('x2，y2:', (x2, y2))
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                                P_y = states[y3, x3]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                                P_y = states[y4, x4]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                            if min_distance == distance2:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.5
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.2
                                P_y = states[y3, x3]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                                P_y = states[y4, x4]  # P_y， get index from list of states
                                # print('x4，y4:', (x4, y4))
                                P[m, : , int(P_y), :] = 0.1
                            if min_distance == distance3:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.5
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                                P_y = states[y3, x3]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.3
                                P_y = states[y4, x4]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                            if min_distance == distance4:
                                P_y = states[all_Meanies[m][1], all_Meanies[m][0]]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.5
                                P_y = states[y1, x1]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                                P_y = states[y2, x2]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                                P_y = states[y3, x3]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.1
                                P_y = states[y4, x4]  # P_y， get index from list of states
                                P[m, : , int(P_y), :] = 0.2

                    # print('P[a]', P[a, :, :])
                    # time.sleep(1)
        sensor = P
        #for m in range(len(all_Meanies)):
            #print('sensor[m][0]:', sensor[m][0])
        # print('P[0]',P[0,:,:])
        # print('P[]', P)
        # time.sleep(100)





        ''' belief for M'''
        if self.number == 0:
            self.old_belief = self.init_belief
        #for i in range((self.old_belief).shape[0]):
            #print('old_belief[i][0]:', self.old_belief[i][0])
        self.number = self.number + 1
        #print('self.number:', self.number)
        #print('self.old_belief.shape[0]',self.old_belief.shape[0])
        print('self.init_belief:', self.init_belief)


        '''get the max_belief and filtered position of Meanies, then update_belief'''
        filter_MeaniesIndex = []  # index of state,not the (x,y)position
        predict_MeaniesIndex = []  # index of predicted_state,not the (x,y)position
        filter_Meanies = []  # index of state,not the (x,y)position
        predict_Meanies = []  # index of predicted_state,not the (x,y)position
        all_updated_belief = []
        updated_belief = []
        print('self.init_belief:',(self.init_belief).shape[0])
        for m in range(len(all_Meanies)):
            #print('m', m)

            if (((self.old_belief).shape[0] - 1) < m):
                #print('sensor[m]:',sensor[m])
                #print('self.init_belief.shape[0]:', (self.init_belief).shape[0])
                #print('self.init_belief[0]:', self.init_belief[0])
                if (self.init_belief).shape[0]!=0:
                    updated_belief = self.init_belief[0] * sensor[m] * transition  #when new Meanies present
                else:
                    self.init_belief = np.full((len(self.moves),
                                                config.worldLength * config.worldBreadth,
                                                config.worldLength * config.worldBreadth), self.value)  # init_belief
                    updated_belief = self.init_belief * sensor[m] * transition

            else:
                updated_belief = self.old_belief[m] * sensor[m] * transition
            all_updated_belief.append(updated_belief)
            #print('all_updated_belief:',np.array(all_updated_belief).shape)
            Max_beliefIndex = self.k_largest_index_argsort(updated_belief, 1)

            if len(Max_beliefIndex)>0:
                print('Max_beliefIndex', Max_beliefIndex)
                print('Max_belief: %.15f' % (updated_belief[Max_beliefIndex[0][0], Max_beliefIndex[0][1], Max_beliefIndex[0][2]]))
                filter_MeaniesIndex.append(Max_beliefIndex[0][1])
                predict_MeaniesIndex.append(Max_beliefIndex[0][2])
                filter_Meanies.append(
                    [(Max_beliefIndex[0][1] % config.worldLength),int(Max_beliefIndex[0][1] / config.worldLength)])
                predict_Meanies.append(
                    [(Max_beliefIndex[0][2] % config.worldLength),int(Max_beliefIndex[0][2] / config.worldLength)])

        print('filter_MeaniesIndex', filter_MeaniesIndex)
        print('predict_MeaniesIndex', predict_MeaniesIndex)
        print('filter_Meanies', filter_Meanies)
        print('predict_Meanies', predict_Meanies)
        #for i in range(len(all_updated_belief)):
            #print('all_updated_belief[i][0]:', all_updated_belief[i][0])
        self.old_belief = np.array(all_updated_belief)
        #for i in range(self.old_belief.shape[0]):
            #print('self.old_belief[i][0]:', self.old_belief[i][0])



        #time.sleep(100000)
        #time.sleep(10)

        # The probability array has shape (A, S, S), where A are actions and S
        # are states. So A arrays, each S x S, ie for each action specify the
        # transitions probabilities of reaching the second state by applying
        # that action in the first state.
        #
        # The probability array contains 4 sub-arrays, one for each action.
        # Each of these is SxS.
        #
        # the action model: directionProbability% of the time the agent moves as intended.
        # 1-directionProbability% of the time the agent moves perpendicular to the intended direction,
        # Half the time to the left, half the time to the right.
        P = np.zeros((A, S, S))
        for a in range(A):  # right,left,up,down
            for y in range(config.worldBreadth):
                for x in range(config.worldLength):
                    P_y = states[y, x]  # P_y， get index from list of states

                    # right
                    if a == 0:
                        if ((x + 1 <= (config.worldLength - 1)) and (y <= (config.worldBreadth - 1))) \
                                and ([x + 1, y] not in all_MeaniesAndPits):  # moves as intended
                            P_x = states[y, x + 1]  # state
                            # print('1-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = config.directionProbability
                        else:
                            P_x = states[y, x]
                            # print('1-2:P_y, P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = config.directionProbability

                        if ((0 <= x) and (0 <= (y - 1))) \
                                and ([x,
                                      y - 1] not in all_MeaniesAndPits):  # up,moves perpendicular to the intended direction
                            P_x = states[y - 1, x]
                            # print('2-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1 - config.directionProbability) / 2.0
                        else:
                            # if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            # print('2-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = P[a, int(P_y), int(P_x)] + (
                                        1 - config.directionProbability) / 2.0

                        if ((x <= (config.worldLength - 1)) and (y + 1 <= (config.worldBreadth - 1))) \
                                and ([x,
                                      y + 1] not in all_MeaniesAndPits):  # down,moves perpendicular to the intended direction
                            P_x = states[y + 1, x]
                            # print('3-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1 - config.directionProbability) / 2.0
                        else:
                            # if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            # print('3-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = P[a, int(P_y), int(P_x)] + (
                                        1 - config.directionProbability) / 2.0
                    # print('P_right:',P[0,int(P_y),:])

                    # left
                    if a == 1:
                        if ((0 <= x - 1) and (0 <= y)) \
                                and ([x - 1, y] not in all_MeaniesAndPits):  # moves as intended
                            P_x = states[y, x - 1]  # state
                            # print('1-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = config.directionProbability
                        else:
                            # if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            # print('1-2:P_y, P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = config.directionProbability

                        if ((0 <= x) and (0 <= (y - 1))) \
                                and ([x,
                                      y - 1] not in all_MeaniesAndPits):  # up,moves perpendicular to the intended direction
                            P_x = states[y - 1, x]
                            # print('2-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1 - config.directionProbability) / 2.0
                        else:
                            # if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            # print('2-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = P[a, int(P_y), int(P_x)] + (
                                        1 - config.directionProbability) / 2.0

                        if ((x <= (config.worldLength - 1)) and (y + 1 <= (config.worldBreadth - 1))) \
                                and ([x,
                                      y + 1] not in all_MeaniesAndPits):  # down,moves perpendicular to the intended direction
                            P_x = states[y + 1, x]
                            # print('3-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1 - config.directionProbability) / 2.0
                        else:
                            # if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            # print('3-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = P[a, int(P_y), int(P_x)] + (
                                        1 - config.directionProbability) / 2.0
                    # print('P_left:',P[1,int(P_y),:])

                    # up
                    if a == 2:
                        if ((0 <= x) and (0 <= y - 1)) \
                                and ([x, y - 1] not in all_MeaniesAndPits):  # moves as intended
                            P_x = states[y - 1, x]  # state
                            # print('1-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = config.directionProbability
                        else:
                            # if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            # print('1-2:P_y, P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = config.directionProbability

                        if ((x + 1 <= (config.worldLength - 1)) and (y <= (config.worldBreadth - 1))) \
                                and ([x + 1,
                                      y] not in all_MeaniesAndPits):  # right,moves perpendicular to the intended direction
                            P_x = states[y, x + 1]
                            # print('2-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1 - config.directionProbability) / 2.0
                        else:
                            # if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            # print('2-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = P[a, int(P_y), int(P_x)] + (
                                        1 - config.directionProbability) / 2.0

                        if ((0 <= x - 1) and (0 <= y)) \
                                and ([x - 1,
                                      y] not in all_MeaniesAndPits):  # left,moves perpendicular to the intended direction
                            P_x = states[y, x - 1]
                            # print('3-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1 - config.directionProbability) / 2.0
                        else:
                            # if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            # print('3-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = P[a, int(P_y), int(P_x)] + (
                                        1 - config.directionProbability) / 2.0
                    # print('P_up:',P[2,int(P_y),:])

                    # down
                    if a == 3:
                        if ((x <= (config.worldLength - 1)) and ((y + 1) <= (config.worldBreadth - 1))) \
                                and ([x, y + 1] not in all_MeaniesAndPits):  # moves as intended
                            P_x = states[y + 1, x]  # state
                            # print('1-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = config.directionProbability
                        else:
                            # if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            # print('1-2:P_y, P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = config.directionProbability

                        if ((x + 1 <= (config.worldLength - 1)) and (y <= (config.worldBreadth - 1))) \
                                and ([x + 1,
                                      y] not in all_MeaniesAndPits):  # right,moves perpendicular to the intended direction
                            P_x = states[y, x + 1]
                            # print('2-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1 - config.directionProbability) / 2.0
                        else:
                            # if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            # print('2-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = P[a, int(P_y), int(P_x)] + (
                                        1 - config.directionProbability) / 2.0

                        if ((0 <= x - 1) and (0 <= y)) \
                                and ([x - 1,
                                      y] not in all_MeaniesAndPits):  # left,moves perpendicular to the intended direction
                            P_x = states[y, x - 1]
                            # print('3-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1 - config.directionProbability) / 2.0
                        else:
                            # if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            # print('3-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = P[a, int(P_y), int(P_x)] + (
                                        1 - config.directionProbability) / 2.0
                    # print('P_down:',P[3,int(P_y),:])

        #print('P: \n', P)
        print('\n')



        '''reward'''
        # The reward array has shape (S, A), so there is a set of S vectors,
        # one for each state, and each is a vector with one element for each
        # the actions --- each element is the reward for executing the relevant
        # action in the state (so this is really modelling cost of the action).
        cost = -0.04
        R = np.full((S, A), cost)
        allBonuses = self.gameWorld.getBonusLocation()
        for y in range(config.worldBreadth):
            for x in range(config.worldLength):

                # rewards distribution for B
                n = 0
                if [x,y] in all_Bonuses:
                    if (x==0):
                        n=n+1
                    if (y==0):
                        n = n + 1
                    if x==(config.worldLength-1):
                        n=n+1
                    if y==(config.worldBreadth-1):
                        n=n+1

                    if [x+1,y] in all_Pits:
                        n=n+1
                    if [x-1,y] in all_Pits:
                        n=n+1
                    if [x,y+1] in all_Pits:
                        n=n+1
                    if [x,y-1] in all_Pits:
                        n=n+1

                    '''
                    if [x+1,y] in all_MeaniesAndPits:
                        n=n+1
                    if [x-1,y] in all_MeaniesAndPits:
                        n=n+1
                    if [x,y+1] in all_MeaniesAndPits:
                        n=n+1
                    if [x,y-1] in all_MeaniesAndPits:
                        n=n+1
                    '''

                    Bonuse_y = states[y, x]
                    print('Bonuse_y:', int(Bonuse_y))
                    if n == 0:
                        R[int(Bonuse_y), :] = 10
                    else:
                        R[int(Bonuse_y), :] = 4 + 4/n


                #rewards distribution for M and P
                if [x,y] in predict_Meanies:
                    Meanies_y = states[y,x]
                    #print('all_Meanies_y:',int(all_Meanies_y))
                    R[int(Meanies_y), :] = -5

                if [x,y] in filter_Meanies:
                    Meanies_y = states[y,x]
                    #print('all_Meanies_y:',int(all_Meanies_y))
                    R[int(Meanies_y), :] = -10


                if [x,y] in all_Pits:
                    all_Pits_y = states[y,x]
                    #print('all_Pits_y:',int(all_Pits_y))
                    R[int(all_Pits_y), :] = -10


                # avoid meanies ana pits in advance
                if [x,y] not in all_Pits and [x,y] not in filter_Meanies and [x,y] not in all_Bonuses:
                    for i in range(len(all_Pits)):
                       distance = math.sqrt(((x - all_Pits[i][0]) * (x - all_Pits[i][0])) + \
                                  ((y - all_Pits[i][1]) * (y - all_Pits[i][1])))
                       if distance<=1:
                            close_Pits_y = states[y, x]
                            #print('close_Pits:',(x,y))
                            #print('close_Pits_y:', int(close_Pits_y))
                            #R[int(close_Pits_y), :] = R[int(close_Pits_y), :] + (-2.5)
                            R[int(close_Pits_y), :] = cost + (-5)

                    for i in range(len(filter_Meanies)):
                       distance = math.sqrt(((x - filter_Meanies[i][0]) * (x - filter_Meanies[i][0])) + \
                                  ((y - filter_Meanies[i][1]) * (y - filter_Meanies[i][1])))
                       if distance<=3:
                            close_Meanies_y = states[y, x]
                            #print('close_Meanies:',(x,y))
                            #print('close_Meanies_y:', int(close_Meanies_y))
                            #R[int(close_Meanies_y), :] = R[int(close_Meanies_y), :] + ((-1)/float(distance))*5
                            R[int(close_Meanies_y), :] = cost + ((-1) / float(distance)) * 5

                    #increse the cost of blink box which close the Means_Pits as the increasement of Mean's number
                    n=0
                    for i in range(len(filter_Meanies)):
                       distance = math.sqrt(((x - filter_Meanies[i][0]) * (x - filter_Meanies[i][0])) + \
                                  ((y - filter_Meanies[i][1]) * (y - filter_Meanies[i][1])))
                       if distance<=1:
                           n=n+1
                    if 2<=n:
                        close_Meanies_y = states[y, x]
                        #print('close_Meanies:',(x,y))
                        #print('close_Meanies_y:', int(close_Meanies_y))
                        #R[int(close_Meanies_y), :] = R[int(close_Meanies_y), :] + ((-1)/float(distance))*5
                        #print('(R[int(close_Meanies_y), :] + (-n)):',(R[int(close_Meanies_y), :][0] + (-n)))
                        R[int(close_Meanies_y), :] = max((R[int(close_Meanies_y), :][0] + (-n)),-8)

                    n = 0
                    for i in range(len(all_Pits)):
                        distance = math.sqrt(((x - all_Pits[i][0]) * (x - all_Pits[i][0])) + \
                                             ((y - all_Pits[i][1]) * (y - all_Pits[i][1])))
                        if distance <= 1:
                            n = n + 1
                    if 2 <= n:
                        close_Pits_y = states[y, x]
                        #print('close_Meanies:', (x, y))
                        #print('close_Meanies_y:', int(close_Pits_y))
                        # R[int(close_Meanies_y), :] = R[int(close_Meanies_y), :] + ((-1)/float(distance))*5
                        # print('(R[int(close_Meanies_y), :] + (-n)):',(R[int(close_Meanies_y), :][0] + (-n)))
                        R[int(close_Pits_y), :] = max((R[int(close_Pits_y), :][0] + (-n)), -8)

        print('R: \n', R)


        '''
        # (1)run value iteration
        # The util.check() function checks that the reward and probability matrices
        # are well-formed, and match.
        #
        # Success is silent, failure provides somewhat useful error messages.
        mdptoolbox.util.check(P, R)
        # To run value iteration we create a value iteration object, and run it. Note that
        # discount value is 0.9
        vi = mdptoolbox.mdp.ValueIteration(P, R, 0.9)
        vi.run()
        # We can then display the values (utilities) computed, and look at the policy:
        #print('Values:\n', vi.V)
        #print('Policy:\n', vi.policy)
        print('\n')
        '''


        # (2)run policy iteration
        mdptoolbox.util.check(P, R)
        vi = mdptoolbox.mdp.PolicyIteration(P, R, 0.9)
        vi.run()
        #print('Values:\n', vi.V)
        #print('Policy:\n', vi.policy)



        # (3)run QLearning
        '''
        mdptoolbox.util.check(P, R)
        vi = mdptoolbox.mdp.QLearning(P, R, 0.9)
        vi.run()
        #print('Values:\n', vi.V)
        #print('Policy:\n', vi.policy)
        #print('time:', time)
        '''


        #visualize
        actions=[]
        for index, value in enumerate(vi.policy):
            if value==0:
                actions.append('right')
            if value==1:
                actions.append('left')
            if value==2:
                actions.append('up')
            if value==3:
                actions.append('down')
        #print('actions:',actions)
        #print('\n')

        #for debug view
        #print('(myPosition.x, myPosition.y):',(myPosition.x, myPosition.y))
        #print('states: \n', states)
        #print('R: \n', R)

        #action from current my position
        myPosition_state = int(states[myPosition.y, myPosition.x])
        #print('myPosition_state',myPosition_state)
        my_policy = vi.policy[myPosition_state]
        print('my_policy',my_policy)

        print('----------------------------------------------------------------')
        print('\n')

        return my_policy





    # consider meanies and pits as minus rewards
    def decision_FullyObservable(self):

        myPosition = self.gameWorld.getTallonLocation()
        allBonuses = self.gameWorld.getBonusLocation()
        allMeanies = self.gameWorld.getMeanieLocation()
        allPits = self.gameWorld.getPitsLocation()
        #print('type(allBonuses):',type(allBonuses))

        all_Bonuses = [] #(x,y) list
        all_Meanies = []
        all_Pits = []
        all_MeaniesAndPits = []  #(x,y) list
        print('myPosition:', (myPosition.x, myPosition.y))
        print('\n')
        for i in range(len(allBonuses)):
            print('Bonuse' + str(i) + ':', (allBonuses[i].x, allBonuses[i].y))
            all_Bonuses.append([allBonuses[i].x, allBonuses[i].y])
        print('all_Bonuses:', all_Bonuses)
        print('\n')

        for i in range(len(allMeanies)):
            print('Meanie' + str(i) + ':', (allMeanies[i].x, allMeanies[i].y))
            if [allMeanies[i].x, allMeanies[i].y] not in all_Meanies:
                all_Meanies.append([allMeanies[i].x, allMeanies[i].y]) #
            if [allMeanies[i].x, allMeanies[i].y] not in all_MeaniesAndPits:
                all_MeaniesAndPits.append([allMeanies[i].x, allMeanies[i].y]) # exclude the overlap between Meanies and Pits
        print('\n')
        for i in range(len(allPits)):
            print('Pit' + str(i) + ':', (allPits[i].x, allPits[i].y))
            if [allPits[i].x, allPits[i].y] not in all_Pits:
                all_Pits.append([allPits[i].x, allPits[i].y]) #
            if [allPits[i].x, allPits[i].y] not in all_MeaniesAndPits:
                all_MeaniesAndPits.append([allPits[i].x, allPits[i].y]) # exclude the overlap between Meanies and Pits
        print('\n')
        print('all_Meanies:', all_Meanies)
        print('all_Pits:', all_Pits)
        print('all_MeaniesAndPits:', all_MeaniesAndPits)
        print('\n')


        A = len(self.moves) #Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST
        S= (config.worldLength * config.worldBreadth)


        states = np.zeros((config.worldBreadth,config.worldLength))
        N=0
        for y in range(config.worldBreadth):
            for x in range(config.worldLength):
                states[y,x]= N
                N = N + 1
        print('states: \n', states)
        #print('type(states[1,0]): \n', type(states[0,0]))
        print('\n')

        '''
        for i in range(states.shape[0]):  # rows
            for j in range(states.shape[1]):  # cols
                states[i][j]=states[i][j].astype(int)
        #states=states.astype(int)
        print('states2: \n',states)
        print('type(states[1,0]): \n', type(states[0, 0]))
        print('\n')
        '''

        distance_thresh = 2

        # The probability array has shape (A, S, S), where A are actions and S
        # are states. So A arrays, each S x S, ie for each action specify the
        # transitions probabilities of reaching the second state by applying
        # that action in the first state.
        #
        # The probability array contains 4 sub-arrays, one for each action.
        # Each of these is SxS.
        #
        #the action model: directionProbability% of the time the agent moves as intended.
        # 1-directionProbability% of the time the agent moves perpendicular to the intended direction,
        # Half the time to the left, half the time to the right.
        P = np.zeros((A, S, S))
        for a in range(A): #right,left,up,down
            for y in range(config.worldBreadth):
                for x in range(config.worldLength):
                    P_y = states[y, x]  # P_y， get index from list of states

                    # right
                    if a==0:
                        if ((x+1<=(config.worldLength-1)) and (y<=(config.worldBreadth-1))) \
                                and ([x+1,y] not in all_MeaniesAndPits): # moves as intended
                            P_x =states[y,x+1] #state
                            #print('1-1:P_y,P_x',P_y,P_x)
                            P[a,int(P_y),int(P_x)] = config.directionProbability
                        else:
                            P_x = states[y, x]
                            #print('1-2:P_y, P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = config.directionProbability

                        if ((0<=x) and (0<=(y-1))) \
                                and ([x,y-1] not in all_MeaniesAndPits): #up,moves perpendicular to the intended direction
                            P_x = states[y-1, x]
                            #print('2-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1-config.directionProbability)/2.0
                        else:
                            #if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            #print('2-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)]=P[a, int(P_y), int(P_x)] + (1-config.directionProbability)/2.0

                        if ((x<=(config.worldLength-1)) and (y+1<=(config.worldBreadth-1))) \
                                and ([x,y+1] not in all_MeaniesAndPits): #down,moves perpendicular to the intended direction
                            P_x = states[y+1, x]
                            #print('3-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1-config.directionProbability)/2.0
                        else:
                            #if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            #print('3-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)]=P[a, int(P_y), int(P_x)] + (1-config.directionProbability)/2.0
                    #print('P_right:',P[0,int(P_y),:])

                    # left
                    if a==1:
                        if ((0<=x-1) and (0<=y)) \
                                and ([x-1,y] not in all_MeaniesAndPits): # moves as intended
                            P_x =states[y,x-1] #state
                            #print('1-1:P_y,P_x',P_y,P_x)
                            P[a,int(P_y),int(P_x)] = config.directionProbability
                        else:
                            #if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            #print('1-2:P_y, P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = config.directionProbability

                        if ((0<=x) and (0<=(y-1))) \
                                and ([x,y-1] not in all_MeaniesAndPits): #up,moves perpendicular to the intended direction
                            P_x = states[y-1, x]
                            #print('2-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1-config.directionProbability)/2.0
                        else:
                            #if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            #print('2-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)]=P[a, int(P_y), int(P_x)] + (1-config.directionProbability)/2.0

                        if ((x<=(config.worldLength-1)) and (y+1<=(config.worldBreadth-1))) \
                                and ([x,y+1] not in all_MeaniesAndPits): #down,moves perpendicular to the intended direction
                            P_x = states[y+1, x]
                            #print('3-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1-config.directionProbability)/2.0
                        else:
                            #if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            #print('3-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)]=P[a, int(P_y), int(P_x)] + (1-config.directionProbability)/2.0
                    #print('P_left:',P[1,int(P_y),:])

                    # up
                    if a==2:
                        if ((0<=x) and (0<=y-1)) \
                                and ([x,y-1] not in all_MeaniesAndPits): # moves as intended
                            P_x =states[y-1,x] #state
                            #print('1-1:P_y,P_x',P_y,P_x)
                            P[a,int(P_y),int(P_x)] = config.directionProbability
                        else:
                            #if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            #print('1-2:P_y, P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = config.directionProbability

                        if ((x+1<=(config.worldLength-1)) and (y<=(config.worldBreadth-1))) \
                                and ([x+1,y] not in all_MeaniesAndPits): #right,moves perpendicular to the intended direction
                            P_x = states[y, x+1]
                            #print('2-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1-config.directionProbability)/2.0
                        else:
                            #if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            #print('2-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)]=P[a, int(P_y), int(P_x)] + (1-config.directionProbability)/2.0

                        if ((0<=x-1) and (0<=y)) \
                                and ([x-1,y] not in all_MeaniesAndPits): #left,moves perpendicular to the intended direction
                            P_x = states[y, x-1]
                            #print('3-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1-config.directionProbability)/2.0
                        else:
                            #if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            #print('3-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)]=P[a, int(P_y), int(P_x)] + (1-config.directionProbability)/2.0
                    #print('P_up:',P[2,int(P_y),:])


                    # down
                    if a==3:
                        if ((x<=(config.worldLength-1)) and ((y+1)<=(config.worldBreadth-1))) \
                                and ([x,y+1] not in all_MeaniesAndPits): # moves as intended
                            P_x =states[y+1,x] #state
                            #print('1-1:P_y,P_x',P_y,P_x)
                            P[a,int(P_y),int(P_x)] = config.directionProbability
                        else:
                            #if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            #print('1-2:P_y, P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)] = config.directionProbability

                        if ((x+1<=(config.worldLength-1)) and (y<=(config.worldBreadth-1))) \
                                and ([x+1,y] not in all_MeaniesAndPits): #right,moves perpendicular to the intended direction
                            P_x = states[y, x+1]
                            #print('2-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1-config.directionProbability)/2.0
                        else:
                            #if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            #print('2-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)]=P[a, int(P_y), int(P_x)] + (1-config.directionProbability)/2.0

                        if ((0<=x-1) and (0<=y)) \
                                and ([x-1,y] not in all_MeaniesAndPits): #left,moves perpendicular to the intended direction
                            P_x = states[y, x-1]
                            #print('3-1:P_y,P_x',P_y,P_x)
                            P[a, int(P_y), int(P_x)] = (1-config.directionProbability)/2.0
                        else:
                            #if (x,y) in all_MeaniesAndPits:
                            P_x = states[y, x]
                            #print('3-2:P_y,P_x', P_y, P_x)
                            P[a, int(P_y), int(P_x)]=P[a, int(P_y), int(P_x)] + (1-config.directionProbability)/2.0
                    #print('P_down:',P[3,int(P_y),:])

        print('P: \n',P)
        print('\n')


        # The reward array has shape (S, A), so there is a set of S vectors,
        # one for each state, and each is a vector with one element for each
        # the actions --- each element is the reward for executing the relevant
        # action in the state (so this is really modelling cost of the action).
        cost = -0.04
        R = np.full((S, A), cost)

        allBonuses = self.gameWorld.getBonusLocation()
        for y in range(config.worldBreadth):
            for x in range(config.worldLength):

                #rewards distribution for B


                n = 0
                if [x,y] in all_Bonuses:
                    if (x==0):
                        n=n+1
                    if (y==0):
                        n = n + 1
                    if x==(config.worldLength-1):
                        n=n+1
                    if y==(config.worldBreadth-1):
                        n=n+1

                    if [x+1,y] in all_Pits:
                        n=n+1
                    if [x-1,y] in all_Pits:
                        n=n+1
                    if [x,y+1] in all_Pits:
                        n=n+1
                    if [x,y-1] in all_Pits:
                        n=n+1

                    Bonuse_y = states[y, x]
                    print('Bonuse_y:', int(Bonuse_y))
                    if n == 0:
                        R[int(Bonuse_y), :] = 10
                    else:
                        R[int(Bonuse_y), :] = 4 + 4/n


                #rewards distribution for M and P

                if [x,y] in all_Meanies:
                    all_Meanies_y = states[y,x]
                    print('all_Meanies_y:',int(all_Meanies_y))
                    R[int(all_Meanies_y), :] = -10

                if [x,y] in all_Pits:
                    all_Pits_y = states[y,x]
                    print('all_Pits_y:',int(all_Pits_y))
                    R[int(all_Pits_y), :] = -10


                # avoid meanies ana pits in advance
                if [x,y] not in all_MeaniesAndPits and [x,y] not in all_Bonuses:
                    for i in range(len(all_Pits)):
                       distance = math.sqrt(((x - all_Pits[i][0]) * (x - all_Pits[i][0])) + \
                                  ((y - all_Pits[i][1]) * (y - all_Pits[i][1])))
                       if distance<=1:
                            close_Pits_y = states[y, x]
                            print('close_Pits:',(x,y))
                            print('close_Pits_y:', int(close_Pits_y))
                            #R[int(close_Pits_y), :] = R[int(close_Pits_y), :] + (-2.5)
                            R[int(close_Pits_y), :] = cost + (-5)

                    for i in range(len(all_Meanies)):
                       distance = math.sqrt(((x - all_Meanies[i][0]) * (x - all_Meanies[i][0])) + \
                                  ((y - all_Meanies[i][1]) * (y - all_Meanies[i][1])))
                       if distance<=3:
                            close_Meanies_y = states[y, x]
                            print('close_Meanies:',(x,y))
                            print('close_Meanies_y:', int(close_Meanies_y))
                            #R[int(close_Meanies_y), :] = R[int(close_Meanies_y), :] + ((-1)/float(distance))*5
                            R[int(close_Meanies_y), :] = cost + ((-1) / float(distance)) * 5

                    #increse the cost of blink box which close the Means_Pits as the increasement of Mean'snumber
                    n=0
                    for i in range(len(all_Meanies)):
                       distance = math.sqrt(((x - all_Meanies[i][0]) * (x - all_Meanies[i][0])) + \
                                  ((y - all_Meanies[i][1]) * (y - all_Meanies[i][1])))
                       if distance<=1:
                           n=n+1
                    if 2<=n:
                        close_Meanies_y = states[y, x]
                        print('close_Meanies:',(x,y))
                        print('close_Meanies_y:', int(close_Meanies_y))
                        #R[int(close_Meanies_y), :] = R[int(close_Meanies_y), :] + ((-1)/float(distance))*5
                        #print('(R[int(close_Meanies_y), :] + (-n)):',(R[int(close_Meanies_y), :][0] + (-n)))
                        R[int(close_Meanies_y), :] = max((R[int(close_Meanies_y), :][0] + (-n)),-8)

                    n = 0
                    for i in range(len(all_Pits)):
                        distance = math.sqrt(((x - all_Pits[i][0]) * (x - all_Pits[i][0])) + \
                                             ((y - all_Pits[i][1]) * (y - all_Pits[i][1])))
                        if distance <= 1:
                            n = n + 1
                    if 2 <= n:
                        close_Pits_y = states[y, x]
                        print('close_Meanies:', (x, y))
                        print('close_Meanies_y:', int(close_Pits_y))
                        # R[int(close_Meanies_y), :] = R[int(close_Meanies_y), :] + ((-1)/float(distance))*5
                        # print('(R[int(close_Meanies_y), :] + (-n)):',(R[int(close_Meanies_y), :][0] + (-n)))
                        R[int(close_Pits_y), :] = max((R[int(close_Pits_y), :][0] + (-n)), -8)


        print('R: \n', R)


        print('----------------------------------------------------------------')
        print('\n')


        # (1)run value iteration
        # The util.check() function checks that the reward and probability matrices
        # are well-formed, and match.
        #
        # Success is silent, failure provides somewhat useful error messages.
        mdptoolbox.util.check(P, R)
        # To run value iteration we create a value iteration object, and run it. Note that
        # discount value is 0.9
        vi = mdptoolbox.mdp.ValueIteration(P, R, 0.9)
        vi.run()
        # We can then display the values (utilities) computed, and look at the policy:
        print('Values:\n', vi.V)
        print('Policy:\n', vi.policy)
        print('\n')



        '''
        # (2)run policy iteration
        mdptoolbox.util.check(P, R)
        vi = mdptoolbox.mdp.PolicyIteration(P, R, 0.9)
        vi.run()
        #print('Values:\n', vi.V)
        #print('Policy:\n', vi.policy)
        '''



        '''
        # (3)run QLearning
        mdptoolbox.util.check(P, R)
        vi = mdptoolbox.mdp.QLearning(P, R, 0.9)
        vi.run()
        print('Values:\n', vi.V)
        print('Policy:\n', vi.policy)
        #print('time:', time)
        '''



        #visualize
        actions=[]
        for index, value in enumerate(vi.policy):
            if value==0:
                actions.append('right')
            if value==1:
                actions.append('left')
            if value==2:
                actions.append('up')
            if value==3:
                actions.append('down')
        print('actions:',actions)
        print('\n')

        #for debug view
        print('(myPosition.x, myPosition.y):',(myPosition.x, myPosition.y))
        print('states: \n', states)
        print('R: \n', R)

        #action from current my position
        myPosition_state = int(states[myPosition.y, myPosition.x])
        print('myPosition_state',myPosition_state)
        my_policy = vi.policy[myPosition_state]
        print('my_policy',my_policy)

        return my_policy







