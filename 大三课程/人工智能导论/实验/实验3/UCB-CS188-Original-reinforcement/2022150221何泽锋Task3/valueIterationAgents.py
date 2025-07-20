# valueIterationAgents.py
# -----------------------
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


# valueIterationAgents.py
# -----------------------
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


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(s)
              mdp.getTransitionStatesAndProbs(s, action)
              mdp.getReward(s, action, nextState)
              mdp.isTerminal(s)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    # 2022150221
    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        for i in range(self.iterations):
            new_values = self.values.copy()
            for s in self.mdp.getStates():
                if self.mdp.isTerminal(s):  # 终端状态跳过
                    continue
                actions = self.mdp.getPossibleActions(s)  # 获取当前状态下所有可能的行动
                if not actions:
                    continue
                max_value = float('-inf')
                for action in actions:
                    q_value = self.computeQValueFromValues(s, action)  # 计算当前动作的Q值
                    max_value = max(max_value, q_value)
                new_values[s] = max_value   # 将更新后的最大值赋给新值列表中的对应状态
            self.values = new_values

    def getValue(self, s):
        """
          Return the value of the s (computed in __init__).
        """
        return self.values[s]

    # 2022150221
    def computeQValueFromValues(self, s, action):
        """
          Compute the Q-value of action in s from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        q_value = 0  # 初始化
        for next_state, prob in self.mdp.getTransitionStatesAndProbs(s, action):   # 遍历所有可能的下一状态及其概率
            reward = self.mdp.getReward(s, action, next_state)    # 当前动作的奖励
            q_value += prob * (reward + self.discount * self.values[next_state])  # 值迭代状态更新方程
        return q_value

    # 2022150221
    def computeActionFromValues(self, s):
        """
          The policy is the best action in the given s
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal s, you should return None.
        """
        "*** YOUR CODE HERE ***"
        if self.mdp.isTerminal(s):
            return None
        actions = self.mdp.getPossibleActions(s)  # 当前状态所有可能的动作
        if not actions:
            return None
        best_action = None  # 初始化
        best_value = float('-inf')
        for action in actions:  # 遍历这些动作
            q_value = self.computeQValueFromValues(s, action)  # 计算每个动作的Q值
            if q_value > best_value: # 更新最大值和最好动作
                best_value = q_value
                best_action = action
        return best_action

    def getPolicy(self, s):
        return self.computeActionFromValues(s)

    def getAction(self, s):
        "Returns the policy at the s (no exploration)."
        return self.computeActionFromValues(s)

    def getQValue(self, s, action):
        return self.computeQValueFromValues(s, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one s, which cycles through
          the states list. If the chosen s is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(s)
              mdp.getTransitionStatesAndProbs(s, action)
              mdp.getReward(s)
              mdp.isTerminal(s)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    # 2022150221
    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        states = self.mdp.getStates()  # 获取所有状态
        for i in range(self.iterations):  # 迭代次数
            s = states[i % len(states)]  # 选择一个状态
            if self.mdp.isTerminal(s):
                continue
            actions = self.mdp.getPossibleActions(s)  # 获取当前状态下的所有动作
            max_value = float('-inf')  # 最大价值（初始化为负无穷）
            for action in actions:
                q_value = self.computeQValueFromValues(s, action)  # 计算当前动作的Q值
                max_value = max(max_value, q_value)
            if max_value > float('-inf'):
                self.values[s] = max_value
            else:
                self.values[s] = 0

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    # 2022150221
    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        states = self.mdp.getStates()  # 获取所有状态
        predecessors = {s: set() for s in states}  # 每个状态的前驱状态集合
        for s in states:
            for action in self.mdp.getPossibleActions(s):  # 获取该状态的所有动作
                # 获取该动作到达的下一状态和概率
                for nextState, prob in self.mdp.getTransitionStatesAndProbs(s, action):
                    predecessors[nextState].add(s)   # 将当前状态添加到下一状态的前驱状态集合中

        q = util.PriorityQueue()  # 优先队列

        for s in states:
            if not self.mdp.isTerminal(s):
                best_action = self.computeActionFromValues(s)  # 最好动作
                best_value = self.computeQValueFromValues(s, best_action)  # 最高价值
                diff = abs(best_value - self.values[s])  # 计算最优状态和当前状态的Q值差
                q.push(s, -diff)  # 将状态及和差值添加到优先级队列

        for iteration in range(self.iterations):
            if q.isEmpty():
                return
            s = q.pop()

            if not self.mdp.isTerminal(s):
                actions = self.mdp.getPossibleActions(s)  # 获取当前状态的所有可能动作
                max_value = float('-inf')
                for action in actions:  # 遍历动作
                    q_value = self.computeQValueFromValues(s, action)  # 计算当前动作的Q值
                    max_value = max(max_value, q_value)
                if max_value > float('-inf'):
                    self.values[s] = max_value
                else:
                    self.values[s] = 0

            for p in predecessors[s]:  # 遍历当前状态的所有前驱状态
                best_action = self.computeActionFromValues(p)  # 获取前驱状态的最佳动作
                if best_action is not None:
                    best_value = self.computeQValueFromValues(p, best_action)
                    diff = abs(best_value - self.values[p])
                    if diff > self.theta:
                        q.update(p, -diff)  # 更新优先级队列中的前驱状态，使用差值的负值作为新的优先级
