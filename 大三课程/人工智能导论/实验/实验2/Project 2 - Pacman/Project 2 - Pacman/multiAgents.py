# multiAgents.py
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


from util import manhattanDistance
from game import Directions
import random, util
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

        getAction takes a GameState and returns some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
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
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        # 获取食物的最近距离-2022150221
        foodList = newFood.asList()
        if foodList:
            minFoodDistance = min([self.manhattanDistance(newPos, food) for food in foodList])
        else:
            minFoodDistance = 0

        # 如果吃到了豆子则获得加分-2022150221
        foodBonus = 0
        if currentGameState.getNumFood() > successorGameState.getNumFood():
            foodBonus = 100

        # 获取距离最近的幽灵-2022150221
        ghostPositions = [ghostState.getPosition() for ghostState in newGhostStates]
        minGhostDistance = min([self.manhattanDistance(newPos, ghostPos) for ghostPos in ghostPositions])

        # 如果靠的太近则扣分（数值较大，惩罚项）-2022150221
        ghostTooClosePenalty = 0
        if minGhostDistance <= 1:
            ghostTooClosePenalty = -100000

        # 根据胶囊距离调整奖励值，距离越近奖励越高-2022150221
        capsuleBonus = 0
        capsules = currentGameState.getCapsules()
        for capsule in capsules:
            capsuleDistance = self.manhattanDistance(newPos, capsule)
            capsuleBonus += 1000 / (capsuleDistance + 1)  # 防止分母为0

        # 如果Pacman吃掉了胶囊，并且附近有幽灵可以被吃，给予额外奖励-2022150221
        scaredBonus = 0
        if currentGameState.getCapsules() > successorGameState.getCapsules():
            for scaredTime in newScaredTimes:
                if scaredTime > 0 and minGhostDistance <= 5:
                    scaredBonus += 500000
                    break  # 只需要检查是否有至少一个幽灵可以被吃

        # 权重 - 2022150221
        WEIGHT_FOOD = 100  # food的权值
        WEIGHT_DISTANCE_FOOD = 100
        WEIGHT_GHOST = 1000  # Ghost的权值
        WEIGHT_SCARED_GHOST = 1  # Scared ghost的权值
        WEIGHT_CAPSULE = 100  # capsule的权值

        evaluation = successorGameState.getScore() \
                     + WEIGHT_FOOD * foodBonus \
                     - WEIGHT_DISTANCE_FOOD * minFoodDistance \
                     + WEIGHT_GHOST * ghostTooClosePenalty \
                     + WEIGHT_CAPSULE * capsuleBonus \
                     + WEIGHT_SCARED_GHOST * scaredBonus

        return evaluation

    # 计算曼哈顿距离
    def manhattanDistance(self, xy1, xy2):
        return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])


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

    def __init__(self, evalFn='betterEvaluationFunction', depth='2'):
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.
        """
        # 主要判断函数，根据传入的对象决定调用max还是min-2022150221
        def minimax(agentIndex, depth, gameState):
            # 终止条件：达到指定深度或游戏结束

            if depth == self.depth or gameState.isWin() or gameState.isLose():
                return self.evaluationFunction(gameState)
            # Pacman的决策层（MAX）
            if agentIndex == 0:
                return max_value(agentIndex, depth, gameState)
            # 幽灵的决策层（MIN）
            else:
                return min_value(agentIndex, depth, gameState)

        # 计算max的函数-2022150221
        def max_value(agentIndex, depth, gameState):
            v = float('-inf')
            for action in gameState.getLegalActions(agentIndex):
                successor = gameState.generateSuccessor(agentIndex, action)
                v = max(v, minimax(agentIndex + 1, depth, successor))
            return v

        # 计算min的函数-2022150221
        def min_value(agentIndex, depth, gameState):
            v = float('inf')
            for action in gameState.getLegalActions(agentIndex):
                successor = gameState.generateSuccessor(agentIndex, action)
                # 如果当前是最后一个幽灵，下一个决策层是Pacman，深度+1
                if agentIndex == gameState.getNumAgents() - 1:
                    v = min(v, minimax(0, depth + 1, successor))
                else:
                    v = min(v, minimax(agentIndex + 1, depth, successor))
            return v

        def argmax(f, actions):
            bestValue = float('-inf')
            bestAction = None
            for action in actions:
                value = f(action)
                if value > bestValue:
                    bestValue = value
                    bestAction = action
            return bestAction

        # 初始化
        legalActions = gameState.getLegalActions(0)
        action = argmax(lambda x: minimax(1, 0, gameState.generateSuccessor(0, x)), legalActions)
        return action


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        # 计算max的函数-2022150221
        def max_value(gameState, depth, agentIndex, alpha, beta):
            if gameState.isWin() or gameState.isLose() or depth == 0:
                return self.evaluationFunction(gameState), None

            v = float("-inf")
            bestAction = None
            for action in gameState.getLegalActions(agentIndex):
                successor = gameState.generateSuccessor(agentIndex, action)
                nextAgentIndex = (agentIndex + 1) % gameState.getNumAgents()
                nextDepth = depth - 1 if nextAgentIndex == 0 else depth
                value, _ = min_value(successor, nextDepth, nextAgentIndex, alpha, beta)
                if value > v:
                    v = value
                    bestAction = action
                if v > beta:
                    return v, bestAction
                alpha = max(alpha, v)
            return v, bestAction

        # 计算min的函数 - 2022150221
        def min_value(gameState, depth, agentIndex, alpha, beta):
            if gameState.isWin() or gameState.isLose() or depth == 0:
                return self.evaluationFunction(gameState), None

            v = float("inf")
            bestAction = None
            for action in gameState.getLegalActions(agentIndex):
                successor = gameState.generateSuccessor(agentIndex, action)
                nextAgentIndex = (agentIndex + 1) % gameState.getNumAgents()
                nextDepth = depth - 1 if nextAgentIndex == 0 else depth
                if nextAgentIndex == 0:
                    value, _ = max_value(successor, nextDepth, nextAgentIndex, alpha, beta)
                else:
                    value, _ = min_value(successor, nextDepth, nextAgentIndex, alpha, beta)
                if value < v:
                    v = value
                    bestAction = action
                if v < alpha:
                    return v, bestAction
                beta = min(beta, v)
            return v, bestAction

        alpha = float("-inf")
        beta = float("inf")
        _, action = max_value(gameState, self.depth, 0, alpha, beta)
        return action

def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 4).

    DESCRIPTION: <write something here so we know what you did>
    """
    newPos = currentGameState.getPacmanPosition()
    newFood = currentGameState.getFood()
    newGhostStates = currentGameState.getGhostStates()

    # 权重参数 - 2022150221
    WEIGHT_FOOD = 1  # food的权值
    WEIGHT_GHOST = 1 / 10  # Ghost的权值
    WEIGHT_SCARED_GHOST = 100  # Scared ghost的权值
    WEIGHT_CAPSULE  = 1  # capsule的权值

    # 基于目前的得分来进行计算
    score = currentGameState.getScore()
    # 计算和食物的距离 - 2022150221
    distancesToFoodList = [util.manhattanDistance(newPos, foodPos) for foodPos in newFood.asList()]
    # 距离食物越近，奖励越多
    if len(distancesToFoodList) > 0:
        score += WEIGHT_FOOD / min(distancesToFoodList)
    else:
        score += WEIGHT_FOOD

    # 胶囊距离影响 - 2022150221
    capsules = currentGameState.getCapsules()
    capsuleDistanceList = [util.manhattanDistance(newPos, capsule) for capsule in capsules]
    if len(capsuleDistanceList) > 0 and min(capsuleDistanceList) <= 5:
        score += WEIGHT_CAPSULE / min(capsuleDistanceList)

    # 获取幽灵位置 - 2022150221
    for ghost in newGhostStates:
        distance = util.manhattanDistance(newPos, ghost.getPosition())
        if distance > 0:
            # 距离Sacred ghost越近奖励越多，鼓励它去进攻
            if ghost.scaredTimer > 1:
                score += WEIGHT_SCARED_GHOST / distance
            # 否则，躲开
            elif distance <= 10:
                score -= WEIGHT_GHOST / distance

        # 下一步就要碰到ghost了
        else:
            return -float(1000000)

    return score

# Abbreviation
better = betterEvaluationFunction
