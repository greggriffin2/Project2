# multiAgents.py
# --------------
# Greg Griffin and David Novak
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import random, util, math

from game import Agent


class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """

    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        # print("----------------------\n\nSuccessor Game State:: \n" + str(successorGameState))

        newPos = successorGameState.getPacmanPosition()
        # print("\n\nNew Position:: " + str(newPos))

        newFood = successorGameState.getFood()
        # print("\n\nNew Food:: \n" + str(newFood))

        newGhostStates = successorGameState.getGhostStates()
        # print("\n\nNew Ghost States:: \n")
        # for i in newGhostStates:
        # print(str(i) + "\n")

        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
        # print("\n\nNew Scared Times:: " + str(newScaredTimes) + "\n\n\n\n")

        "*** YOUR CODE HERE ***"

        # Rewards:
        # ==============================================

        closerToFoodReward = 3
        foodHereReward = 3

        furtherFromGhostReward = 4
        closerToCapsuleReward = 1

        # Penalties:
        # ==============================================

        furtherFromFoodP = -3
        closerToGhostP = -4
        furtherFromCapsuleP = -2

        # ==============================================

        # Positions of the ghosts
        ghostPositions = [ghostState.getPosition() for ghostState in newGhostStates]

        # Value to be modified and returned
        score = 100

        # If the ghosts are far away, don't punish for getting nearer to them,
        # instead incentivize food and capsules
        currDistToGhosts = [distanceTo(currentGameState.getPacmanPosition(), ghostXY) for ghostXY in ghostPositions]
        if min(currDistToGhosts) > 5:
            closerToGhostP = 0
            furtherFromFoodP *= 2
            furtherFromCapsuleP *= 2

        # MAKE PACMAN STOP STALLING

        # THINGS THAT INCREASE OR DECREASE THE SCORE
        # ------------------------------------------
        foodList = newFood.asList()
        # IF state has food increase the score
        for xy in foodList:
            if newPos == xy:
                score += foodHereReward

        # Modify the score based on food
        f = foodDistanceCalc(currentGameState, successorGameState, foodList, closerToFoodReward, furtherFromFoodP)
        try:
            score += f
        except TypeError:
            pass

        # Modify the score based on capsules
        c = capsuleDistanceCalc(currentGameState, successorGameState, closerToCapsuleReward, furtherFromCapsuleP)
        try:
            score += c
        except TypeError:
            pass

        # IF state has a ghost heavily penalize
        for item in ghostPositions:
            if newPos == item:
                score -= 100

        # Modify the score based on ghosts
        g = ghostDistanceCalc(currentGameState, successorGameState, furtherFromGhostReward, closerToGhostP)
        try:
            score += g
        except TypeError:
            pass

        # print(str(distanceTo(newPos, ghostPositions[0])))
        # return successorGameState.getScore()
        return score


def distanceTo(xy1, xy2):
    """
    Returns the cartesian distance to xy2 from xy1
    """
    result = math.sqrt(((xy1[0] - xy2[0]) ** 2) + ((xy1[1] - xy2[1]) ** 2))
    return round(result, 2)


def foodDistanceCalc(currState, succState, foodList, r, p):
    """
    Takes the current and successor states and the boolean grid of food values and returns a number to incentivize
    picking successors that are closer to food

    If the successor is closer to the closest food on the board, then pick that one
    """

    # Lists of the distances to the ghosts for the current state and the successor state
    currDistTo = [distanceTo(currState.getPacmanPosition(), foodXY) for foodXY in foodList]
    succDistTo = [distanceTo(succState.getPacmanPosition(), foodXY) for foodXY in foodList]

    try:
        if min(currDistTo) > min(succDistTo):
            return r
        else:
            return p
    except ValueError:
        return


def ghostDistanceCalc(currState, succState, r, p):
    """
    Returns a reward or punishment based on if the successor being explored is becoming closer to a ghost or not
    """
    currGhosts = currState.getGhostStates()
    succGhosts = succState.getGhostStates()
    currStateGhosts = [ghostState.getPosition() for ghostState in currGhosts]
    succStateGhosts = [ghostState.getPosition() for ghostState in succGhosts]

    # Lists of the distances to the ghosts for the current state and the successor state
    currDistTo = [distanceTo(currState.getPacmanPosition(), ghostXY) for ghostXY in currStateGhosts]
    succDistTo = [distanceTo(succState.getPacmanPosition(), ghostXY) for ghostXY in succStateGhosts]

    # Create a list of the difference between the current and successors node's distances to the ghosts
    try:
        if min(currDistTo) < min(succDistTo):
            return r
        else:
            return p
    except ValueError:
        return


def capsuleDistanceCalc(currState, succState, r, p):
    """
    Returns a reward or punishment based on if the successor being explored is becoming closer to a capsule or not
    """
    currStateCapsules = currState.getCapsules()
    succStateCapsules = succState.getCapsules()

    # Lists of the distances to the capsules for the current state and the successor state
    currDistTo = [distanceTo(currState.getPacmanPosition(), capsuleXY) for capsuleXY in currStateCapsules]
    succDistTo = [distanceTo(succState.getPacmanPosition(), capsuleXY) for capsuleXY in succStateCapsules]

    try:
        if min(currDistTo) > min(succDistTo):
            return r
        else:
            return p
    except ValueError:
        return


def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn='scoreEvaluationFunction', depth='2'):
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.
          Here are some method calls that might be useful when implementing minimax.
          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1
          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action
          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        print("MinimaxAgent with depth ", self.depth)
        legal = gameState.getLegalActions(0)
        successors = [gameState.generateSuccessor(0, action) for action in legal]
        maxValue = -float('inf')
        goalIndex = 0
        for x in range(len(successors)):
            actionValue = self.value(successors[x], 1, 0)
            if actionValue > maxValue:
                maxValue = actionValue
                goalIndex = x

        return legal[goalIndex]

    def MAXvalue(self, gameState, agentIndex, depthSoFar):
        legal = gameState.getLegalActions(agentIndex)
        successors = [gameState.generateSuccessor(agentIndex, action) for action in legal]
        x = -float('inf')
        for successor in successors:
            x = max(x, self.value(successor, 1, depthSoFar))
        return x

    def MINvalue(self, gameState, agentIndex, depthSoFar):
        legal = gameState.getLegalActions(agentIndex)
        successors = [gameState.generateSuccessor(agentIndex, action) for action in legal]
        x = float('inf')
        for successor in successors:
            if agentIndex + 1 == gameState.getNumAgents():  # all the ghost(s) finished their turn, Pacman next
                x = min(x, self.value(successor, 0, depthSoFar + 1))
            else:  # Another ghost's turn
                x = min(x, self.value(successor, agentIndex + 1, depthSoFar))
        return x

    def value(self, gameState, agentIndex, depthSoFar):

        "If requisite no. of searches complete, evaluation function"
        if depthSoFar == self.depth or gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState)
        "If agentIndex is 0, perform MAX"
        if agentIndex == 0:
            return self.MAXvalue(gameState, agentIndex, depthSoFar)
        "Else (if agentIndex > 0), perform MIN"
        if agentIndex > 0:
            return self.MINvalue(gameState, agentIndex, depthSoFar)


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.
          Here are some method calls that might be useful when implementing minimax.
          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1
          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action
          gameState.getNumAgents():
            Returns the total number of agents in the game
        """

        print("AlphaBetaAgent with depth ", self.depth)
        legal = gameState.getLegalActions(0)
        successors = [gameState.generateSuccessor(0, action) for action in legal]
        maxValue = -float('inf')
        goalIndex = 0
        for x in range(len(successors)):
            actionValue = self.value(successors[x], 1, 0, -float('inf'), float('inf'))
            if actionValue > maxValue:
                maxValue = actionValue
                goalIndex = x

        return legal[goalIndex]

    def MAXvalue(self, gameState, agentIndex, depthSoFar, alpha, beta):
        legal = gameState.getLegalActions(agentIndex)
        successors = [gameState.generateSuccessor(agentIndex, action) for action in legal]
        x = -float('inf')
        for successor in successors:
            x = max(x, self.value(successor, 1, depthSoFar, alpha, beta))
            if x > beta:
                return x
            alpha = max(alpha, x)
        return x

    def MINvalue(self, gameState, agentIndex, depthSoFar, alpha, beta):
        legal = gameState.getLegalActions(agentIndex)
        successors = [gameState.generateSuccessor(agentIndex, action) for action in legal]
        x = float('inf')
        for successor in successors:
            if agentIndex + 1 == gameState.getNumAgents():  # all the ghost(s) finished their turn, Pacman next
                x = min(x, self.value(successor, 0, depthSoFar + 1, alpha, beta))
                if x < alpha:
                    return x
                beta = min(beta, x)
            else:  # Another ghost's turn
                x = min(x, self.value(successor, agentIndex + 1, depthSoFar, alpha, beta))
                if x < alpha:
                    return x
                beta = min(beta, x)
        return x

    def value(self, gameState, agentIndex, depthSoFar, alpha, beta):

        "If requisite no. of searches complete, evaluation function"
        if depthSoFar == self.depth or gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState)
        "If agentIndex is 0, perform MAX"
        if agentIndex == 0:
            return self.MAXvalue(gameState, agentIndex, depthSoFar, alpha, beta)
        "Else (if agentIndex > 0), perform MIN"
        if agentIndex > 0:
            return self.MINvalue(gameState, agentIndex, depthSoFar, alpha, beta)


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"

        print("ExpectimaxAgent with depth ", self.depth)
        legal = gameState.getLegalActions(0)
        successors = [gameState.generateSuccessor(0, action) for action in legal]
        maxValue = -float('inf')
        goalIndex = 0
        for x in range(len(successors)):
            actionValue = self.value(successors[x], 1, 0)
            if actionValue > maxValue:
                maxValue = actionValue
                goalIndex = x

        return legal[goalIndex]

    def MAXvalue(self, gameState, agentIndex, depthSoFar):
        legal = gameState.getLegalActions(agentIndex)
        successors = [gameState.generateSuccessor(agentIndex, action) for action in legal]
        x = -float('inf')
        for successor in successors:
            x = max(x, self.value(successor, 1, depthSoFar))
        return x

    # Creates a list of successors that took random actions, then for each successor, adds its value to x.
    # then returns x divided by the amount of successors to get the expected value.

    # THIS IS NOT CORRECT
    def EXPECTIvalue(self, gameState, agentIndex, depthSoFar):
        legal = gameState.getLegalActions(agentIndex)
        successors = []  # May need to create this list differently, with or without the random choice
        for i in range(len(legal)):
            successors.append(gameState.generateSuccessor(agentIndex, random.choice(legal)))

        # Change this block
        x = 0
        for successor in successors:
            if agentIndex + 1 == gameState.getNumAgents():  # all the ghost(s) finished their turn, Pacman next
                x += self.value(successor, 0, depthSoFar + 1)
            else:  # Another ghost's turn
                x += self.value(successor, agentIndex + 1, depthSoFar)
        return x / len(successors)

    def value(self, gameState, agentIndex, depthSoFar):

        "If requisite no. of searches complete, evaluation function"
        if depthSoFar == self.depth or gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState)
        "If agentIndex is 0, perform MAX"
        if agentIndex == 0:
            return self.MAXvalue(gameState, agentIndex, depthSoFar)
        "Else (if agentIndex > 0), perform EXPECTI"
        if agentIndex > 0:
            return self.EXPECTIvalue(gameState, agentIndex, depthSoFar)


def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()


# Abbreviation
better = betterEvaluationFunction
