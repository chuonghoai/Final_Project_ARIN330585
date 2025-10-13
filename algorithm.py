from collections import deque
import time
import random

stopRunning = lambda: False

# Chọn thuật toán
def chooseAlgorithm(name, maze, _stopRunning=lambda: False):
    global stopRunning
    stopRunning = _stopRunning
    result = None
    
    if name == "BFS":
        result = bfs_maze_collect_all_to_goal(maze)
    if name == "And-Or Tree":
        result = and_or_tree_search(maze)
    if name == "Belief state":
        result = belief_state_search_bfs_to_goal(maze)
    if name == "Partially observable":
        result = POS_algorithm(maze)
        path, collected = result
        total_treasure = countAllTreasure(maze[0])
        return path, collected, total_treasure, None
    if name == "AC-3":
        result = ac3_greedy_collect_treasures(maze)
    if name == "Hill Climbing":
        result = hill_climbing_maze_real_v4(maze)
        return result
    return result

def countAllTreasure(maze):
    cnt = 0
    # for _ in maze:
        # print(_)
    for i in range(len(maze)):
        for j in range(len(maze[0])):
            if maze[i][j] == "t":
                cnt += 1
    return cnt

# 1. BFS
def bfs_maze_collect_all_to_goal(maze):
    rows, cols = len(maze), len(maze[0])
    
    start = None
    end = None
    treasures = set()
    
    for r in range(rows):
        for c in range(cols):
            cell = maze[r][c]
            if cell == "A":
                start = (r,c)
            elif cell == "B":
                end = (r,c)
            elif cell == "t":
                treasures.add((r,c))
    
    total_treasures = len(treasures)
    if start is None or end is None:
        return None, 0, total_treasures, []

    ALL_MASK = (1 << total_treasures) - 1
    treasure_index = {pos: idx for idx, pos in enumerate(treasures)}
    
    directions = [(1,0),(-1,0),(0,1),(0,-1)]
    explored_flat = []
    seen_explored = set()
    
    # BFS queue: (pos, path_so_far, mask_collected)
    start_mask = 0
    if start in treasure_index:
        start_mask |= 1 << treasure_index[start]
    
    queue = deque([(start, [start], start_mask)])
    visited = set([(start, start_mask)])
    
    final_path = None
    final_collected = 0
    
    while queue:
        if stopRunning():
            return None, 0, total_treasures, explored_flat
        
        pos, path_coords, mask = queue.popleft()
        r, c = pos
        
        if pos not in seen_explored:
            seen_explored.add(pos)
            explored_flat.append(pos)
        
        # cập nhật mask nếu nhặt treasure
        if pos in treasure_index:
            mask |= 1 << treasure_index[pos]
        
        # chỉ cho phép về đích khi đã nhặt hết kho báu
        if pos == end and mask == ALL_MASK:
            final_path = path_coords
            final_collected = total_treasures
            break
        
        for dr, dc in directions:
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] != "*":
                new_pos = (nr,nc)
                new_mask = mask
                if new_pos in treasure_index:
                    new_mask |= 1 << treasure_index[new_pos]
                key = (new_pos, new_mask)
                if key not in visited:
                    visited.add(key)
                    queue.append((new_pos, path_coords + [new_pos], new_mask))
    
    if final_path is None:
        # không tìm được đường đi
        return None, 0, total_treasures, explored_flat
    
    return final_path, final_collected, total_treasures, explored_flat

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
def belief_state_search_bfs_to_goal(maze):
    rows, cols = len(maze), len(maze[0])
    
    start_positions = []
    end = None
    treasures = set()
    for i in range(rows):
        for j in range(cols):
            cell = maze[i][j]
            if cell == "A":
                # start_positions.append((i,j))
                maze[i][j] = "."
            elif cell == "?":
                start_positions.append((i,j))
            elif cell == "B":
                end = (i,j)
            elif cell == "t":
                treasures.add((i,j))
    
    total_treasures = len(treasures)
    if not start_positions or end is None:
        return None, 0, total_treasures, []
    
    treasure_index = {pos: idx for idx, pos in enumerate(treasures)}
    ALL_MASK = (1 << total_treasures) - 1
    
    directions = [(1,0),(-1,0),(0,1),(0,-1)]
    explored_flat = []
    seen_explored = set()
    
    queue = deque()
    visited = dict()  # key: (pos, mask) -> parent_key
    
    # Khởi tạo queue từ tất cả start positions
    for sp in start_positions:
        mask = 0
        if sp in treasure_index:
            mask |= 1 << treasure_index[sp]
        queue.append((sp, mask))
        visited[(sp, mask)] = None
    
    final_key = None
    while queue:
        if stopRunning():
            return None, 0, total_treasures, explored_flat
        
        pos, mask = queue.popleft()
        r, c = pos
        
        # Lưu explored
        if pos not in seen_explored:
            seen_explored.add(pos)
            explored_flat.append(pos)
        
        # cập nhật mask nếu nhặt treasure
        if pos in treasure_index:
            mask |= 1 << treasure_index[pos]
        
        # kiểm tra đã nhặt hết kho báu và đến B
        if mask == ALL_MASK and pos == end:
            final_key = (pos, mask)
            break
        
        for dr, dc in directions:
            nr, nc = r+dr, c+dc
            if 0<=nr<rows and 0<=nc<cols and maze[nr][nc] != "*":
                new_pos = (nr,nc)
                new_mask = mask
                if new_pos in treasure_index:
                    new_mask |= 1 << treasure_index[new_pos]
                key = (new_pos, new_mask)
                if key not in visited:
                    visited[key] = (pos, mask)
                    queue.append((new_pos, new_mask))
    
    if final_key is None:
        # Không tìm được đường đi
        return None, 0, total_treasures, explored_flat
    
    # Tái tạo path từ parent dictionary
    path = []
    key = final_key
    while key:
        pos, mask = key
        path.append(pos)
        key = visited[key]
    path.reverse()
    
    return path, total_treasures, total_treasures, explored_flat

# 5. nhìn thấy 1 phần
def POS_algorithm(_maze):
    # Giải nén maze gốc và maze bị làm mù
    maze = [row[:] for row in _maze[0]]        # Mê cung thật
    mazeCover = [row[:] for row in _maze[1]]   # Mê cung mà agent nhìn thấy
    row, col = len(maze), len(maze[0])
    
    def find_positions(symbol, grid):
        return [(i, j) for i in range(row) for j in range(col) if grid[i][j] == symbol]

    start = find_positions("A", maze)[0]
    goal = find_positions("B", maze)[0]
    treasures_cover = find_positions("t", mazeCover)

    collected = 0
    path = [start]
    current = start

    # === HÀM PHỤ ===
    def neighbors(i, j):
        for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < row and 0 <= nj < col:
                yield ni, nj

    def bfs_path(start, goal):
        """BFS trong mazeCover, nhưng kiểm tra tường thật trong maze."""
        q = deque([start])
        came = {start: None}
        while q:
            if stopRunning():
                return None
            cur = q.popleft()
            if cur == goal:
                break
            for ni, nj in neighbors(*cur):
                # Chỉ thêm vào hàng đợi nếu không phải tường thật
                if (ni, nj) not in came and maze[ni][nj] != "*":
                    came[(ni, nj)] = cur
                    q.append((ni, nj))
        if goal not in came:
            return None

        # reconstruct path
        path = []
        cur = goal
        while cur:
            path.append(cur)
            cur = came[cur]
        return path[::-1]

    # === BẮT ĐẦU ===
    while not stopRunning():
        # Nếu còn kho báu nhìn thấy thì tìm tới gần nhất
        if treasures_cover:
            target = min(treasures_cover, key=lambda t: abs(t[0]-current[0]) + abs(t[1]-current[1]))
        else:
            target = goal

        segment = bfs_path(current, target)
        if not segment:
            break

        # Di chuyển từng bước
        for pos in segment[1:]:
            if stopRunning():
                return path, collected

            if maze[pos[0]][pos[1]] == "*":  # Gặp tường thật
                break

            path.append(pos)
            current = pos

            # Quan sát 4 hướng quanh
            for ni, nj in neighbors(*pos):
                if maze[ni][nj] == "t" and mazeCover[ni][nj] != "t":
                    # Phát hiện kho báu mới
                    mazeCover[ni][nj] = "t"
                    treasures_cover.append((ni, nj))

            # Nhặt kho báu nếu gặp
            if maze[pos[0]][pos[1]] == "t":
                collected += 1
                maze[pos[0]][pos[1]] = "."
                if pos in treasures_cover:
                    treasures_cover.remove(pos)
                mazeCover[pos[0]][pos[1]] = "."

            if pos == goal:
                return path, collected

        # Nếu đã đến đích và không còn kho báu thấy được
        if not treasures_cover and current == goal:
            break

    return path, collected

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

# 7. hill climbing
def hill_climbing_maze_real_v4(maze, max_steps=10000):
    directions = [(-1,0),(1,0),(0,-1),(0,1)]
    n, m = len(maze), len(maze[0])

    def in_bounds(r, c):
        return 0 <= r < n and 0 <= c < m and maze[r][c] != '*'

    # --- Xác định vị trí ---
    start, goal, treasures = None, None, []
    total_treasures = 0
    for i in range(n):
        for j in range(m):
            cell = maze[i][j]
            if cell == 'A': start = (i, j)
            elif cell == 'B': goal = (i, j)
            elif cell.lower() == 't': 
                treasures.append((i, j))
                total_treasures += 1

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # --- Hill Climbing đơn pha ---
    def hill_climb_path(start, target):
        current = start
        path = [current]
        explored = [current]
        steps = 0

        while steps < max_steps:
            steps += 1
            r, c = current
            neighbors = []

            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if in_bounds(nr, nc):
                    h = heuristic((nr, nc), target)
                    neighbors.append((h, (nr, nc)))

            if not neighbors:
                break

            best_h = min(h for h, _ in neighbors)
            best_moves = [(h, pos) for h, pos in neighbors if h == best_h]
            curr_h = heuristic(current, target)

            if best_h < curr_h:
                moved = False
                for _, best_pos in best_moves:
                    if best_pos not in path:  # tránh vòng lặp
                        current = best_pos
                        path.append(current)
                        explored.append(current)
                        moved = True
                        break
                if not moved:
                    return path, explored, False

                if current == target:
                    return path, explored, True
            else:
                return path, explored, False

        return path, explored, False

    # --- Hill Climbing đa pha linh hoạt ---
    full_path = [start]
    process = [start]
    collected = []
    current = start
    remaining = treasures[:]
    reachedGoal = False

    while True:
        targets = list(remaining)
        if goal not in targets:
            targets.append(goal)

        best_sub_path = []
        best_explored = []
        best_target = None
        found_path = False

        # --- thử đến từng target ---
        for target in targets:
            if stopRunning():
                return None, 0, total_treasures, process, False
            
            sub_path, explored, reached = hill_climb_path(current, target)
            process += explored[1:]

            # Nếu đi được xa hơn path cũ thì lưu lại
            if len(sub_path) > len(best_sub_path):
                best_sub_path = sub_path
                best_explored = explored
                best_target = target

            if reached:
                # đạt đích target này
                full_path += sub_path[1:]
                current = target
                found_path = True

                if target in remaining:
                    remaining.remove(target)
                    collected.append(target)

                if target == goal:
                    reachedGoal = True
                break  # sang vòng while tiếp theo

        # --- nếu không có target nào tới được ---
        if not found_path:
            if best_sub_path and len(best_sub_path) > 1:
                # chỉ nối path dài nhất trong các đường bị kẹt
                full_path += best_sub_path[1:]
                current = best_sub_path[-1]
                print(f"🧱 Tất cả target bị kẹt, chọn path dài nhất ({len(best_sub_path)} bước) tới {current}")
            else:
                print(f"🧱 Hoàn toàn không thể tiến thêm từ {current}")
            break

        if reachedGoal:
            break

    print("🗺️ Path:", full_path)
    print(f"💎 Collected {len(collected)}/{total_treasures} treasures")
    print(f"🚪 Reached goal: {reachedGoal}")
    print(f"🔍 Processed: {len(process)} cells")

    return full_path, collected, total_treasures, process, reachedGoal