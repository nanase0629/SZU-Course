# 初始状态和目标状态-202215021
initial_board = (2, 8, 3, 1, 0, 4, 7, 6, 5)
goal_board = (1, 2, 3, 8, 0, 4, 7, 6, 5)
# 定义四个移动方向：右、左、下、上
moves = [1, -1, -3, 3]


# 交换函数-2022150221
def get_new_state(board, empty_index, move):
    new_board = list(board)
    new_board[empty_index], new_board[empty_index + move] = new_board[empty_index + move], new_board[empty_index]
    return tuple(new_board)


# dfs-2022150221
def dfs(initial_state, goal_state):
    stack = [(initial_state, [initial_state])]  # 使用栈，每个元素是一个元组，包含当前状态和解路径f
    visited = {initial_state}  # 记录已访问过的状态
    len = 0  # 判断搜索次数
    while stack:
        current_state, path = stack.pop()  # 取出栈顶
        if len % 10000 == 0:
            print(len)  # 每搜索10000次输出
        if current_state == goal_state:
            return path  # 如果当前状态是目标状态，返回解路径
        len += 1
        empty_index = current_state.index(0)  # 找到0的位置
        for move in moves:
            if 0 <= empty_index + move < 9:  # 确保移动后仍在棋盘范围内
                if (move in [-1, 1] and empty_index // 3 == (empty_index + move) // 3) or \
                        (move in [-3, 3] and empty_index % 3 == (empty_index + move) % 3):  # 判断移动方向是否合法
                    new_board = get_new_state(current_state, empty_index, move)  # 获取交换后的棋盘
                    if new_board not in visited:
                        visited.add(new_board)  # 标记为已访问
                        new_path = path + [new_board]  # 更新解路径
                        stack.append((new_board, new_path))  # 将新状态和解路径加入栈
    return None  # 无解


# 执行深度优先搜索-2022150221
solution_path = dfs(initial_board, goal_board)

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
