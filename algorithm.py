from collections import deque

# Chọn thuật toán
def chooseAlgorithm(name, maze):
    if name == "BFS":
        return bfs_collect_treasures(maze)

# 1. BFS
from collections import deque

def bfs_collect_treasures(maze):
    rows, cols = len(maze), len(maze[0])

    start = end = None
    treasures = []
    for i in range(rows):
        for j in range(cols):
            if maze[i][j] == "A":
                start = (i, j)
            elif maze[i][j] == "B":
                end = (i, j)
            elif maze[i][j] == "t":
                treasures.append((i, j))

    if not start or not end:
        return None, 0, len(treasures), []

    treasure_index = {pos: idx for idx, pos in enumerate(treasures)}
    total_treasures = len(treasures)
    ALL = (1 << total_treasures) - 1  # bitmask của tất cả kho báu

    queue = deque([(start[0], start[1], 0, [start])])  # (r, c, mask, path)
    visited = set()
    best_path = None
    best_mask = 0
    explored_order = []  # lưu thứ tự mở rộng

    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    while queue:
        r, c, mask, path = queue.popleft()
        explored_order.append((r, c))  # lưu vị trí đang mở rộng

        # Nếu đang đứng trên kho báu thì cập nhật mask
        if (r, c) in treasure_index:
            mask |= (1 << treasure_index[(r, c)])

        # Nếu đến đích
        if (r, c) == end:
            if mask > best_mask or (mask == best_mask and (not best_path or len(path) < len(best_path))):
                best_path = path
                best_mask = mask
            if mask == ALL:  # Đã nhặt đủ tất cả kho báu → dừng luôn
                break

        state = (r, c, mask)
        if state in visited:
            continue
        visited.add(state)

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] != "*":
                queue.append((nr, nc, mask, path + [(nr, nc)]))

    collected = bin(best_mask).count("1")
    return best_path, collected, total_treasures, explored_order
