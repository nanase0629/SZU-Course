from collections import deque

# 初始状态和目标状态-2022150221
initial_board = (2, 8, 3, 1, 0, 4, 7, 6, 5)
goal_board = (1, 2, 3, 8, 0, 4, 7, 6, 5)
# 定义四个移动方向：右、左、下、上
moves = [1, -1, 3, -3]


# 交换函数-2022150221
def get_new_state(board, empty_index, move):
    new_board = list(board)
    # 在空的地方进行交换
    new_board[empty_index], new_board[empty_index + move] = new_board[empty_index + move], new_board[empty_index]
    return tuple(new_board)


# bfs-202215021
def bfs(initial_state, goal_state):
    queue = deque([initial_state])  # 使用队列实现宽度优先搜索
    visited = {initial_state}  # 记录已访问过的状态，避免重复搜索
    previous = {initial_state: None}  # 记录每个状态的前一个状态，用于构造解路径

    while queue:
        current_state = queue.popleft()  # 取出队列中的第一个状态
        if current_state == goal_state:
            return previous  # 如果当前状态是目标状态，返回前一个状态的字典

        empty_index = current_state.index(0)  # 找到0的位置

        for move in moves:
            if 0 <= empty_index + move < 9:  # 确保移动后仍在棋盘范围内
                if (move in [-1, 1] and empty_index // 3 == (empty_index + move) // 3) or \
                        (move in [-3, 3] and empty_index % 3 == (empty_index + move) % 3):   # 判断移动方向是否合法
                    new_board = get_new_state(current_state, empty_index, move)
                    if new_board not in visited:
                        visited.add(new_board)  # 标记为已访问
                        previous[new_board] = current_state  # 记录前一个状态
                        queue.append(new_board)  # 将新状态加入队列

    return None


# 调用bfs-2022150221
solution_path = bfs(initial_board, goal_board)

# 打印解路径
if solution_path:
    path = []
    state = goal_board
    while state:  # 反向寻找解路径
        path.append(state)
        state = solution_path[state]
    print(f"步数{len(path)-1}")
    for board in reversed(path):
        board_str = ""
        # 以3为步长遍历 board，每次取3个元素作为一个子列表
        for i in range(0, 9, 3):
            # 转换为字符串，用空格连接
            row_str = ' '.join(map(str, board[i:i + 3]))
            board_str += row_str + '\n'
        # 打印棋盘
        print(board_str)

else:
    print("No solution found")
