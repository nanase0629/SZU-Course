from heapq import *

# 初始状态和目标状态
initial_board = (2, 8, 3, 1, 0, 4, 7, 6, 5)
goal_board = (1, 2, 3, 8, 0, 4, 7, 6, 5)

# 定义四个移动方向：右、左、下、上
moves = [1, -1, 3, -3]


# 使用曼哈顿距离作为启发函数-2022150221
def manhattan_distance(state, goal_state):
    distance = 0  # 初始化距离
    for i in range(1, 9):  # 遍历数字1-8，获取当前位置和目标为位置
        current_index = state.index(i)
        goal_index = goal_state.index(i)
        x1, y1 = divmod(current_index, 3)  # 转换坐标
        x2, y2 = divmod(goal_index, 3)
        distance += abs(x1 - x2) + abs(y1 - y2)
    return distance


def get_new_state(board, empty_index, move):
    new_board = list(board)
    new_board[empty_index], new_board[empty_index + move] = new_board[empty_index + move], new_board[empty_index]
    return tuple(new_board)

# 定义A*函数-2022150221
def a_star_search(initial_state, goal_state):
    # 使用优先队列来存储状态和估计代价（移动次数 + 启发式距离）
    priority_queue = [(manhattan_distance(initial_state, goal_state), 0, initial_state, [initial_state])]  # (总代价, 移动代价, 当前状态, 解路径)
    visited = {initial_state}  # 记录已访问过的状态

    while priority_queue:
        _, cost, current_state, path = heappop(priority_queue)  # 取出总代价最小的状态进行扩展

        if current_state == goal_state:
            return path  # 如果当前状态是目标状态，返回解路径

        empty_index = current_state.index(0)  # 找到0的位置

        for move in moves:
            if 0 <= empty_index + move < 9:  # 确保移动后的索引仍在棋盘范围内
                if (move in [-1, 1] and empty_index // 3 == (empty_index + move) // 3) or \
                        (move in [-3, 3] and empty_index % 3 == (empty_index + move) % 3):
                    new_board = get_new_state(current_state, empty_index, move)
                    if new_board not in visited:
                        visited.add(new_board)  # 标记为已访问
                        new_cost = cost + 1  # 移动代价 + 1
                        new_total_cost = new_cost + manhattan_distance(new_board, goal_state)  # 计算新状态的估计代价
                        new_path = path + [new_board]  # 更新解路径
                        heappush(priority_queue, (new_total_cost, new_cost, new_board, new_path))  # 将新状态和总代价加入优先队列

    return None


# A*搜索
solution_path = a_star_search(initial_board, goal_board)

# 打印解路径
if solution_path:
    print(f"步数: {len(solution_path) - 1}")
    for board in solution_path:
        board_str = ""
        for i in range(0, 9, 3):
            row_str = ' '.join(map(str, board[i:i + 3]))
            board_str += row_str + '\n'
        print(board_str)
else:
    print("No solution found")
