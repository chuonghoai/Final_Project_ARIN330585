from collections import deque

# Chọn thuật toán
def chooseAlgorithm(name, maze):
    if name == "BFS":
        return bfs_collect_treasures(maze)
    if name == "Greedy":
        return greedy_best_first_search(maze)
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

#-------------------
from heapq import heappush, heappop

def greedy_best_first_search(maze):
    rows, cols = len(maze), len(maze[0])

    # --- Tìm vị trí A, B và các kho báu ---
    start = end = None
    treasures = []
    for r in range(rows):
        for c in range(cols):
            if maze[r][c] == "A":
                start = (r, c)
            elif maze[r][c] == "B":
                end = (r, c)
            elif maze[r][c] == "t":
                treasures.append((r, c))

    if not start or not end:
        return None, 0, 0, []

    def heuristic(a, b):
        """Khoảng cách Manhattan"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def greedy_path(start, goal):
        """Tìm đường Greedy từ start → goal"""
        pq = []  # hàng đợi ưu tiên theo heuristic
        heappush(pq, (heuristic(start, goal), start))
        came_from = {start: None}
        visited = set()
        explored = []

        while pq:
            _, current = heappop(pq)
            explored.append(current)

            if current == goal:
                # Truy vết đường đi
                path = []
                while current:
                    path.append(current)
                    current = came_from[current]
                return path[::-1], explored

            visited.add(current)
            r, c = current
            for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                nr, nc = r + dr, c + dc
                neighbor = (nr, nc)
                if (
                    0 <= nr < rows and 0 <= nc < cols and
                    maze[nr][nc] != "*" and neighbor not in visited
                ):
                    if neighbor not in came_from:
                        came_from[neighbor] = current
                        heappush(pq, (heuristic(neighbor, goal), neighbor))

        return [], explored  # không tìm thấy

    # --- Tìm kho báu tuần tự ---
    full_path = []
    explored_order = []
    current = start
    collected = 0
    total_treasures = len(treasures)

    while treasures:
        # tìm kho báu gần nhất theo heuristic
        treasures.sort(key=lambda t: heuristic(current, t))
        next_treasure = treasures.pop(0)
        path, explored = greedy_path(current, next_treasure)
        if not path:
            break  # không tìm thấy
        full_path += path[1:]  # bỏ ô đầu trùng
        explored_order += explored
        current = next_treasure
        collected += 1

    # sau khi lấy hết kho báu, đi tới đích B
    path_to_end, explored = greedy_path(current, end)
    full_path += path_to_end[1:]
    explored_order += explored

    return full_path, collected, total_treasures, explored_order
