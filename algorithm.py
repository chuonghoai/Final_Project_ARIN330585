from collections import deque
from heapq import heappush, heappop
import time

# Chọn thuật toán
def chooseAlgorithm(name, maze):
    result = None
    if name == "BFS":
        result = bfs_collect_treasures(maze)
    if name == "And-Or Tree":
        result = and_or_tree_search(maze)
    if name == "Belief state":
        result = belief_state_search(maze)
    if name == "Partially observable deterministic":
        result = partial_observable_search(maze)
    if name == "AC-3":
        result = ac3_greedy_collect_treasures(maze)
                
    return result

# 1. BFS
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

# 3. AND-OR tree search
def and_or_tree_search(maze):
    rows, cols = len(maze), len(maze[0])

    # ----------------------------
    # Xác định vị trí A, B, t
    # ----------------------------
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

    total_treasure = len(treasures)
    treasure_index = {pos: idx for idx, pos in enumerate(treasures)}
    ALL_TREASURE = (1 << total_treasure) - 1

    if not start or not end:
        return None, 0, total_treasure, []

    # ----------------------------
    # Các hàm tiện ích
    # ----------------------------
    def is_goal(state):
        pos, collected_mask = state
        return pos == end and collected_mask == ALL_TREASURE

    def successors(pos):
        x, y = pos
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] != "*":
                yield (nx, ny)

    # ----------------------------
    # AND–OR Search
    # ----------------------------
    process = []
    visited = set()
    added_to_process = set()  # tránh thêm trùng lặp

    def record_state(pos):
        """Thêm vào process nếu chưa có để tránh danh sách quá dài"""
        if pos not in added_to_process:
            process.append(pos)
            added_to_process.add(pos)

    def or_search(state, path):
        pos, collected = state
        record_state(pos)

        if is_goal(state):
            return path + [pos]

        if state in visited:
            return None
        visited.add(state)

        for nxt in successors(pos):
            new_mask = collected
            if maze[nxt[0]][nxt[1]] == "t":
                new_mask |= 1 << treasure_index[(nxt[0], nxt[1])]

            plan = and_search((nxt, new_mask), path + [pos])
            if plan:
                return plan  # chọn kế hoạch hợp lệ đầu tiên

        return None

    def and_search(state, path):
        pos, _ = state
        record_state(pos)

        if is_goal(state):
            return path + [pos]
        return or_search(state, path)

    # ----------------------------
    # Bắt đầu tìm kế hoạch
    # ----------------------------
    plan = or_search((start, 0), [])

    if plan is None:
        collected = 0
        return None, collected, total_treasure, process

    # Đếm số kho báu đã nhặt được
    collected_mask = 0
    for (x, y) in plan:
        if maze[x][y] == "t":
            collected_mask |= 1 << treasure_index[(x, y)]
    collected = bin(collected_mask).count("1")

    return plan, collected, total_treasure, process


# 4. Belief state search
def belief_state_search(maze):
    rows, cols = len(maze), len(maze[0])

    uncertain_positions, end, treasures = [], None, []

    # Quét mê cung để tìm vị trí quan trọng
    for i in range(rows):
        for j in range(cols):
            c = maze[i][j]
            if c == "?":
                uncertain_positions.append((i, j))
            elif c == "B":
                end = (i, j)
            elif c == "t":
                treasures.append((i, j))
            elif c == "A":
                # Xem A như là đường trống
                maze[i][j] = "."

    total_treasure = len(treasures)
    treasure_index = {p: i for i, p in enumerate(treasures)}
    ALL_TREASURE = (1 << total_treasure) - 1

    # ✅ Belief khởi đầu — tập hợp tất cả vị trí nghi ngờ
    if not uncertain_positions:
        return None, 0, total_treasure, []  # không có vị trí khởi đầu
    if not end:
        return None, 0, total_treasure, []

    start_belief = frozenset(uncertain_positions)
    start_state = (start_belief, 0)
    queue = deque([(start_state, [])])
    visited = set([start_state])
    process, added = [], set()

    def move_belief(belief, dx, dy):
        """Di chuyển toàn bộ belief theo hướng (dx, dy)."""
        new_belief = set()
        for (x, y) in belief:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < rows and 0 <= ny < cols) or maze[nx][ny] == "*":
                nx, ny = x, y  # đụng tường → đứng lại
            new_belief.add((nx, ny))
        return frozenset(new_belief)

    def record_belief(belief):
        """Lưu các vị trí từng được agent tin là có thể đang ở."""
        for pos in belief:
            if pos not in added:
                process.append(pos)
                added.add(pos)

    best_path = None
    best_mask = 0

    # BFS trên không gian belief
    while queue:
        (belief, mask), path = queue.popleft()
        record_belief(belief)

        # Nếu tất cả belief đều nằm tại B (đích)
        if all(pos == end for pos in belief):
            if bin(mask).count("1") > bin(best_mask).count("1"):
                best_mask = mask
                best_path = [p for step in path for p in step] + list(belief)
            if mask == ALL_TREASURE:
                break  # ăn hết kho báu thì dừng

        # Di chuyển theo 4 hướng
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            new_belief = move_belief(belief, dx, dy)
            new_mask = mask

            # Kiểm tra ăn kho báu
            for (x, y) in new_belief:
                if maze[x][y] == "t":
                    new_mask |= 1 << treasure_index[(x, y)]

            new_state = (new_belief, new_mask)
            if new_state == (belief, mask):
                continue
            if new_state not in visited:
                visited.add(new_state)
                queue.append((new_state, path[:] + [list(belief)]))

    # ✅ Nếu không đạt kết quả hoàn hảo → trả kết quả tốt nhất
    if best_path:
        collected = bin(best_mask).count("1")
        return best_path, collected, total_treasure, process

    return None, 0, total_treasure, process

# 5. nhìn thấy 1 phần
def partial_observable_search(maze, vision_range=1):
    rows, cols = len(maze), len(maze[0])
    start = end = None
    treasures = []

    # --- Xác định vị trí ---
    for i in range(rows):
        for j in range(cols):
            c = maze[i][j]
            if c == "A": start = (i, j)
            elif c == "B": end = (i, j)
            elif c == "t": treasures.append((i, j))

    total_treasure = len(treasures)
    treasure_index = {pos: idx for idx, pos in enumerate(treasures)}
    ALL_TREASURE = (1 << total_treasure) - 1

    UNKNOWN = "?"
    internal_map = [[UNKNOWN for _ in range(cols)] for _ in range(rows)]

    def in_bounds(x, y): return 0 <= x < rows and 0 <= y < cols
    def is_free(c): return c in (".", "A", "B", "t")

    def reveal(x, y):
        """Mở vùng tầm nhìn quanh vị trí hiện tại"""
        for dx in range(-vision_range, vision_range + 1):
            for dy in range(-vision_range, vision_range + 1):
                nx, ny = x + dx, y + dy
                if in_bounds(nx, ny):
                    internal_map[nx][ny] = maze[nx][ny]

    def neighbors_free(x, y):
        """Chỉ sinh ra ô ĐÃ BIẾT và có thể đi được"""
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and is_free(internal_map[nx][ny]):
                yield (nx, ny)

    def is_frontier(pos):
        """Ô free, đã biết, nhưng kề với UNKNOWN → frontier thật sự"""
        x, y = pos
        if not is_free(internal_map[x][y]): return False
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and internal_map[nx][ny] == UNKNOWN:
                return True
        return False

    def bfs_path(src, cond):
        """BFS chỉ đi qua vùng đã biết và free."""
        q = deque([(src, [])])
        seen = {src}
        while q:
            (x, y), path = q.popleft()
            if cond((x, y)):
                return path + [(x, y)]
            for nx, ny in neighbors_free(x, y):
                if (nx, ny) not in seen:
                    seen.add((nx, ny))
                    q.append(((nx, ny), path + [(x, y)]))
        return None

    # --- Vòng lặp khám phá ---
    process = []
    path = [start]
    collected_mask = 0
    current = start
    reveal(*current)

    max_steps = rows * cols * 20
    steps = 0

    while steps < max_steps:
        steps += 1
        process.append(current)

        # Thu kho báu
        if maze[current[0]][current[1]] == "t":
            collected_mask |= 1 << treasure_index[(current[0], current[1])]

        # Kết thúc khi đã đến đích và đủ kho báu
        if current == end and collected_mask == ALL_TREASURE:
            break

        # Cập nhật tầm nhìn
        reveal(*current)

        # Nếu thấy B và đã đủ kho báu → đi tới B
        if internal_map[end[0]][end[1]] != UNKNOWN and collected_mask == ALL_TREASURE:
            to_goal = bfs_path(current, lambda p: p == end)
            if to_goal:
                path.extend(to_goal[1:])
                current = to_goal[-1]
                continue

        # Nếu thấy kho báu chưa nhặt → BFS tới kho báu gần nhất
        known_t = [
            t for t in treasures
            if internal_map[t[0]][t[1]] != UNKNOWN and not (collected_mask & (1 << treasure_index[t]))
        ]
        if known_t:
            for t in known_t:
                to_t = bfs_path(current, lambda p, t=t: p == t)
                if to_t:
                    path.extend(to_t[1:])
                    current = to_t[-1]
                    break
            continue

        # Nếu chưa thấy B, chưa hết treasure → tìm frontier gần nhất
        to_frontier = bfs_path(current, is_frontier)
        if to_frontier:
            path.extend(to_frontier[1:])
            current = to_frontier[-1]
            continue

        # Không còn gì để khám phá
        break

    collected = bin(collected_mask).count("1")
    if current != end or collected_mask != ALL_TREASURE:
        print("⚠️ Không thể tìm được đường hợp lệ tới B.")
        return None, collected, total_treasure, process

    return path, collected, total_treasure, process

# 6. AC-3
def ac3_greedy_collect_treasures(maze, timeout=1.0):
    rows, cols = len(maze), len(maze[0])
    start = end = None
    treasures = []

    for i in range(rows):
        for j in range(cols):
            c = maze[i][j]
            if c == "A":
                start = (i, j)
            elif c == "B":
                end = (i, j)
            elif c == "t":
                treasures.append((i, j))

    total_treasure = len(treasures)
    if not start or not end:
        return None, 0, total_treasure, []

    def in_bounds(x, y): return 0 <= x < rows and 0 <= y < cols
    def is_free(x, y): return maze[x][y] != "*"
    directions = [(-1,0),(1,0),(0,-1),(0,1)]

    # AC-3 filtering (hợp lệ = không xuyên tường)
    domains = {}
    for i in range(rows):
        for j in range(cols):
            if is_free(i, j):
                domains[(i, j)] = [
                    (i+dx, j+dy)
                    for dx, dy in directions
                    if in_bounds(i+dx, j+dy) and is_free(i+dx, j+dy)
                ]

    def bfs_path(start, goal):
        """BFS đơn giản tìm đường từ start đến goal"""
        q = deque([(start, [start])])
        visited = {start}
        while q:
            pos, path = q.popleft()
            if pos == goal:
                return path
            for nxt in domains.get(pos, []):
                if nxt not in visited:
                    visited.add(nxt)
                    q.append((nxt, path + [nxt]))
        return None

    start_time = time.time()
    current = start
    collected = 0
    collected_positions = set()
    full_path = [start]
    process = []

    # Giai đoạn 1: ăn kho báu
    while treasures and time.time() - start_time < timeout:
        # Tìm kho báu gần nhất
        best_t = None
        best_path = None
        min_len = 999999

        for t in treasures:
            path = bfs_path(current, t)
            if path and len(path) < min_len:
                min_len = len(path)
                best_t = t
                best_path = path

        if not best_t:
            break  # không còn kho báu nào có thể đến

        # Ăn kho báu gần nhất
        full_path.extend(best_path[1:])
        process.extend(best_path)
        current = best_t
        collected += 1
        collected_positions.add(best_t)
        treasures.remove(best_t)

    # Giai đoạn 2: đi đến B
    path_to_B = bfs_path(current, end)
    if path_to_B:
        full_path.extend(path_to_B[1:])
        process.extend(path_to_B)
    else:
        # không đến được B → trả về phần đã đi
        pass

    return full_path, collected, total_treasure, process