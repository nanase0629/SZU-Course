from heapq import heappop, heappush

# 初始状态和目标状态
initial_board = (2, 8, 3, 1, 0, 4, 7, 6, 5)
goal_board = (1, 2, 3, 8, 0, 4, 7, 6, 5)
# 定义四个移动方向：右、左、下、上
moves = [1, -1, 3, -3]


def get_new_state(board, empty_index, move):
    new_board = list(board)
    new_board[empty_index], new_board[empty_index + move] = new_board[empty_index + move], new_board[empty_index]
    return tuple(new_board)


# ucs-2022150221
def uniform_cost_search(initial_state, goal_state):
    # 使用优先队列（最小堆）来存储状态和路径代价
    priority_queue = [(0, initial_state, [initial_state])]  # (代价, 当前状态, 解路径)
    visited = {initial_state}  # 记录已访问过的状态

    while priority_queue:
        cost, current_state, path = heappop(priority_queue)  # 取出代价最小的状态进行扩展

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
                        new_cost = cost + 1  # 每次移动后状态代价+1
                        new_path = path + [new_board]  # 更新解路径
                        heappush(priority_queue, (new_cost, new_board, new_path))  # 将新状态和代价加入优先队列

    return None


# 执行一致代价搜索
solution_path = uniform_cost_search(initial_board, goal_board)

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
