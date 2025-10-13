from collections import deque
from heapq import heappush, heappop
import random, math
import time
import heapq


stopRunning = lambda: False

# Chọn thuật toán
def chooseAlgorithm(name, maze, _stopRunning=lambda: False):
    global stopRunning
    stopRunning = _stopRunning
    result = None
    
    if name == "BFS":
        result = bfs_maze_collect_all_to_goal(maze)
    if name == "Greedy":
        result = greedy_maze_collect_all_to_goal(maze)
    if name == "A*":
        result = a_star_maze_collect_all_to_goal(maze)
    if name == "IDL":
        result = idl_pure_maze_collect_all_to_goal(maze, max_depth=100)
    if name == "Simulated Annealing":
        result = simulated_annealing_maze_collect_all_to_goal(maze)
    if name == "Forward Checking":
        result = forward_checking_multi_goal_maze(maze)
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
    if name == "DFS":
        result = dfs_maze_collect_all_to_goal(maze)
    if name == "UCS":
        result = ucs_maze_collect_all_to_goal(maze)
    if name == "Beam Search":
        result = beam_search_maze_collect_all_to_goal(maze)
    if name == "Backtracking":
        result = backtracking_maze_collect_all_to_goal(maze)
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

# 2. A* Search
def a_star_maze_collect_all_to_goal(maze):
    rows, cols = len(maze), len(maze[0])
    start = end = None
    treasures = []

    for r in range(rows):
        for c in range(cols):
            cell = maze[r][c]
            if cell == "A":
                start = (r, c)
            elif cell == "B":
                end = (r, c)
            elif cell == "t":
                treasures.append((r, c))

    total_treasures = len(treasures)
    if start is None or end is None:
        return None, 0, total_treasures, []

    explored_flat = []
    seen_explored = set()

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def astar_path(src, goal):
        pq = []
        heappush(pq, (heuristic(src, goal), 0, src))
        came_from = {src: None}
        gscore = {src: 0}
        explored = []

        while pq:
            f, g, current = heappop(pq)
            explored.append(current)
            if current == goal:
                path = []
                while current is not None:
                    path.append(current)
                    current = came_from[current]
                return path[::-1], explored, g
            r, c = current
            for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] != "*":
                    neighbor = (nr, nc)
                    g_new = g + 1
                    f_new = g_new + heuristic(neighbor, goal)
                    if g_new < gscore.get(neighbor, float("inf")):
                        came_from[neighbor] = current
                        gscore[neighbor] = g_new
                        heappush(pq, (f_new, g_new, neighbor))
        return None, explored, None

    current = start
    final_path = [start]
    final_collected = 0
    total_cost = 0

    while treasures:
        treasures.sort(key=lambda t: heuristic(current, t))
        target = treasures.pop(0)
        path_segment, explored, cost_segment = astar_path(current, target)
        explored_flat.extend(explored)
        if not path_segment:
            return None, final_collected, total_treasures, explored_flat
        final_path.extend(path_segment[1:])
        current = target
        final_collected += 1
        if cost_segment:
            total_cost += cost_segment

    path_to_end, explored, cost_to_end = astar_path(current, end)
    explored_flat.extend(explored)
    if not path_to_end:
        return None, final_collected, total_treasures, explored_flat
    final_path.extend(path_to_end[1:])
    if cost_to_end:
        total_cost += cost_to_end

    return final_path, final_collected, total_treasures, explored_flat
# 3. Greedy Search
def greedy_maze_collect_all_to_goal(maze):
    rows, cols = len(maze), len(maze[0])
    start = end = None
    treasures = []

    for r in range(rows):
        for c in range(cols):
            cell = maze[r][c]
            if cell == "A":
                start = (r, c)
            elif cell == "B":
                end = (r, c)
            elif cell == "t":
                treasures.append((r, c))

    total_treasures = len(treasures)
    if start is None or end is None:
        return None, 0, total_treasures, []

    explored_flat = []
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def greedy_path(src, goal):
        pq = []
        heappush(pq, (heuristic(src, goal), src))
        came_from = {src: None}
        explored = []
        while pq:
            h, current = heappop(pq)
            explored.append(current)
            if current == goal:
                path = []
                while current is not None:
                    path.append(current)
                    current = came_from[current]
                return path[::-1], explored
            r, c = current
            for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] != "*":
                    neighbor = (nr, nc)
                    if neighbor not in came_from:
                        came_from[neighbor] = current
                        heappush(pq, (heuristic(neighbor, goal), neighbor))
        return None, explored

    current = start
    final_path = [start]
    final_collected = 0

    while treasures:
        treasures.sort(key=lambda t: heuristic(current, t))
        target = treasures.pop(0)
        path_segment, explored = greedy_path(current, target)
        explored_flat.extend(explored)
        if not path_segment:
            return None, final_collected, total_treasures, explored_flat
        final_path.extend(path_segment[1:])
        current = target
        final_collected += 1

    path_to_end, explored = greedy_path(current, end)
    explored_flat.extend(explored)
    if not path_to_end:
        return None, final_collected, total_treasures, explored_flat
    final_path.extend(path_to_end[1:])

    return final_path, final_collected, total_treasures, explored_flat

# 4. IDL Search
def idl_pure_maze_collect_all_to_goal(maze, max_depth=1000):
    rows, cols = len(maze), len(maze[0])
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

    total_treasures = len(treasures)
    if start is None or end is None:
        return None, 0, total_treasures, []

    explored_flat = []
    seen_explored = set()
    directions = [(1,0), (-1,0), (0,1), (0,-1)]

    def depth_limited_dfs(src, goal, limit):
        stack = [(src, [src], 0)]
        local_visited = set()
        while stack:
            pos, path, depth = stack.pop()
            if pos not in local_visited:
                local_visited.add(pos)
                if pos not in seen_explored:
                    seen_explored.add(pos)
                    explored_flat.append(pos)
            if pos == goal:
                return path
            if depth < limit:
                r, c = pos
                for dr, dc in directions:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] != "*":
                        nxt = (nr, nc)
                        if nxt not in path:
                            stack.append((nxt, path+[nxt], depth+1))
        return None

    def iterative_deepening(src, goal):
        for limit in range(1, max_depth+1):
            result = depth_limited_dfs(src, goal, limit)
            if result:
                return result
        return None

    current = start
    collected = 0
    final_path = [start]

    while treasures:
        target = treasures.pop(0)
        path = iterative_deepening(current, target)
        if not path:
            continue
        current = target
        collected += 1
        final_path.extend(path[1:])

    path_to_end = iterative_deepening(current, end)
    if path_to_end:
        final_path.extend(path_to_end[1:])

    return final_path, collected, total_treasures, explored_flat

# 4. Simulated Annealing
def simulated_annealing_maze_collect_all_to_goal(maze):
    rows, cols = len(maze), len(maze[0])
    start = end = None
    treasures = []

    for r in range(rows):
        for c in range(cols):
            cell = maze[r][c]
            if cell == "A":
                start = (r, c)
            elif cell == "B":
                end = (r, c)
            elif cell == "t":
                treasures.append((r, c))

    total_treasures = len(treasures)
    if start is None or end is None:
        return None, 0, total_treasures, []

    rng = random.Random()
    explored_flat = []

    # bfs để tìm đường đi giữa hai điểm
    def bfs_path(src, dst):
        q = deque([src])
        parent = {src: None}
        while q:
            u = q.popleft()
            if u == dst:
                break
            ur, uc = u
            for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                vr, vc = ur+dr, uc+dc
                if 0 <= vr < rows and 0 <= vc < cols and maze[vr][vc] != "*" and (vr,vc) not in parent:
                    parent[(vr,vc)] = u
                    q.append((vr,vc))
        if dst not in parent:
            return None
        path = []
        cur = dst
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        return path[::-1]
    #tính khoảng cách giữa các điểm
    nodes = [start] + treasures + [end]
    K = len(nodes)
    dist = [[math.inf]*K for _ in range(K)]
    path_cache = {}

    for i in range(K):
        for j in range(K):
            if i == j:
                dist[i][j] = 0
            else:
                p = bfs_path(nodes[i], nodes[j])
                if not p:
                    return None, 0, total_treasures, []
                dist[i][j] = len(p) - 1
                path_cache[(i,j)] = p

    m = len(treasures)
    treasure_idx = list(range(1, 1+m))

    def route_cost(order):
        if not order:
            return dist[0][m+1]
        c = dist[0][order[0]]
        for i in range(len(order)-1):
            c += dist[order[i]][order[i+1]]
        c += dist[order[-1]][m+1]
        return c
    #bđ chạy SA
    curr = treasure_idx[:]
    rng.shuffle(curr)
    curr_cost = route_cost(curr)
    best, best_cost = curr[:], curr_cost

    T = max(5.0, 0.25 * rows * cols)
    alpha = 0.995
    max_iters = 8000

    for _ in range(max_iters):
        if stopRunning():
            break
        cand = curr[:]
        if len(cand) >= 2:
            i, j = sorted(rng.sample(range(len(cand)), 2))
            if rng.random() < 0.5:
                cand[i], cand[j] = cand[j], cand[i]
            else:
                cand[i:j+1] = reversed(cand[i:j+1])

        cand_cost = route_cost(cand)
        delta = cand_cost - curr_cost
        if delta <= 0 or rng.random() < math.exp(-delta / T):
            curr, curr_cost = cand, cand_cost
            if curr_cost < best_cost:
                best, best_cost = curr[:], curr_cost

        T *= alpha
        if T < 1e-6:
            break

    order = best
    waypoints = [0] + order + [m+1]
    full_path = []

    for i in range(len(waypoints)-1):
        a, b = waypoints[i], waypoints[i+1]
        seg = path_cache[(a,b)]
        if i == 0:
            full_path.extend(seg)
        else:
            full_path.extend(seg[1:])
        explored_flat.extend(seg)

    collected = total_treasures
    return full_path, collected, total_treasures, explored_flat

# 5. Forward Checking
def forward_checking_multi_goal_maze(maze):

    rows, cols = len(maze), len(maze[0])
    start = end = None
    treasures = []

    for r in range(rows):
        for c in range(cols):
            cell = maze[r][c]
            if cell == "A":
                start = (r, c)
            elif cell == "B":
                end = (r, c)
            elif cell == "t":
                treasures.append((r, c))

    total_treasures = len(treasures)
    if start is None or end is None:
        return None, 0, total_treasures, []

    explored_flat = []
    collected = 0
    current = start
    full_path = [start]
    start_time = time.time()
    time_limit = 6.0

    def heuristic(a, b): 
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    #dfs với forward checking
    def forward_checking_path(src, dst):
        best_path = None

        def reachable(p):
            "Kiểm tra xem node có còn khả năng đi tiếp (pruning)."
            q = deque([p])
            vis = {p}
            while q:
                r, c = q.popleft()
                if maze[r][c] in (".", "t", "B"):
                    return True
                for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] != "*" and (nr,nc) not in vis:
                        vis.add((nr,nc))
                        q.append((nr,nc))
            return False

        def dfs(pos, path):
            nonlocal best_path
            if time.time() - start_time > time_limit or stopRunning():
                return
            if pos not in explored_flat:
                explored_flat.append(pos)
            if pos == dst:
                best_path = path[:]
                return
            for dr, dc in sorted([(1,0),(-1,0),(0,1),(0,-1)],
                                 key=lambda d: heuristic((pos[0]+d[0],pos[1]+d[1]), dst)):
                nr, nc = pos[0]+dr, pos[1]+dc
                nxt = (nr, nc)
                if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] != "*" and nxt not in path:
                    if reachable(nxt):
                        dfs(nxt, path + [nxt])
                    if best_path is not None:
                        return

        dfs(src, [src])
        return best_path
    # Lặp qua từng kho báu
    while treasures and time.time() - start_time < time_limit:
        treasures.sort(key=lambda t: heuristic(current, t))
        target = treasures.pop(0)

        seg = forward_checking_path(current, target)
        if not seg:
            return None, collected, total_treasures, explored_flat
        full_path.extend(seg[1:])
        collected += 1
        current = target
        maze[current[0]][current[1]] = "."  # ăn kho báu
    # Cuối cùng đi đến B
    seg = forward_checking_path(current, end)
    if seg:
        full_path.extend(seg[1:])
    else:
        return None, collected, total_treasures, explored_flat

    return full_path, collected, total_treasures, explored_flat

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
    """
    BFS belief state từ các vị trí '?' hoặc 'A', nhặt tối đa kho báu rồi đi đến B.
    Trả về:
        - path: list of (r,c) coordinates
        - collected: số kho báu nhặt được
        - total_treasures: tổng kho báu trong maze
        - explored_flat: list of (r,c) đã mở rộng (flatten)
    """
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


# 7. DFS
def dfs_maze_collect_all_to_goal(maze):
    rows, cols = len(maze), len(maze[0])
    start = end = None
    treasures = set()

    for r in range(rows):
        for c in range(cols):
            cell = maze[r][c]
            if cell == "A":
                start = (r, c)
            elif cell == "B":
                end = (r, c)
            elif cell == "t":
                treasures.add((r, c))

    total_treasures = len(treasures)
    if start is None or end is None:
        return None, 0, total_treasures, []

    treasure_index = {pos: idx for idx, pos in enumerate(treasures)}
    ALL_MASK = (1 << total_treasures) - 1

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    explored_flat = []
    seen_explored = set()

    stack = [(start, [start], 0)]  # (vị trí, đường đi, mask kho báu)
    visited = set([(start, 0)])

    final_path = None
    final_collected = 0

    while stack:
        if stopRunning():
            return None, 0, total_treasures, explored_flat

        pos, path_coords, mask = stack.pop()
        r, c = pos

        if pos not in seen_explored:
            seen_explored.add(pos)
            explored_flat.append(pos)

        # Cập nhật mask khi nhặt kho báu
        if pos in treasure_index:
            mask |= 1 << treasure_index[pos]

        # Điều kiện kết thúc
        if pos == end and mask == ALL_MASK:
            final_path = path_coords
            final_collected = total_treasures
            break

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] != "*":
                new_pos = (nr, nc)
                new_mask = mask
                if new_pos in treasure_index:
                    new_mask |= 1 << treasure_index[new_pos]
                key = (new_pos, new_mask)
                if key not in visited:
                    visited.add(key)
                    stack.append((new_pos, path_coords + [new_pos], new_mask))

    if final_path is None:
        return None, 0, total_treasures, explored_flat

    return final_path, final_collected, total_treasures, explored_flat


# BEAM SEARCH
def beam_search_maze_collect_all_to_goal(maze, beam_width=5):
    rows, cols = len(maze), len(maze[0])
    start = end = None
    treasures = []

    for i in range(rows):
        for j in range(cols):
            v = maze[i][j]
            if v == "A": start = (i, j)
            elif v == "B": end = (i, j)
            elif v == "t": treasures.append((i, j))

    total_treasures = len(treasures)
    if not start or not end:
        return None, 0, total_treasures, []

    treasure_index = {pos: idx for idx, pos in enumerate(treasures)}
    ALL_MASK = (1 << total_treasures) - 1

    def manhattan(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    def in_bounds(x, y): return 0 <= x < rows and 0 <= y < cols

    # heuristic cho một state
    def score_state(pos, mask):
        # nếu còn kho báu: lấy khoảng cách đến kho báu gần nhất
        remaining = []
        for idx, tpos in enumerate(treasures):
            if not (mask & (1 << idx)):
                remaining.append(tpos)
        rem_cnt = len(remaining)
        if rem_cnt > 0:
            dmin = min(manhattan(pos, t) for t in remaining)
        else:
            dmin = manhattan(pos, end)
        # cộng thêm "áp lực" còn bao nhiêu kho báu
        return dmin + 2 * rem_cnt

    directions = [(-1,0),(1,0),(0,-1),(0,1)]

    # explored theo yêu cầu UI (flatten theo toạ độ duy nhất)
    explored_flat = []
    seen_explored_pos = set()

    # visited lưu best depth đã biết của một (pos,mask) để tránh vòng lặp
    best_depth = {}

    # parent để reconstruct path: parent[(pos, mask)] = (prev_pos, prev_mask)
    parent = {}

    # Khởi tạo mask ở start
    start_mask = 0
    if start in treasure_index:
        start_mask |= 1 << treasure_index[start]

    depth = 0
    cur_beam = [(start, start_mask)]
    best_depth[(start, start_mask)] = 0
    parent[(start, start_mask)] = None

    # Đánh dấu explored
    if start not in seen_explored_pos:
        seen_explored_pos.add(start)
        explored_flat.append(start)

    # Nếu đã start ở B và đã đủ kho báu
    if start == end and start_mask == ALL_MASK:
        return [start], total_treasures, total_treasures, explored_flat

    while cur_beam:
        if stopRunning():
            return None, 0, total_treasures, explored_flat

        depth += 1
        candidates = []

        # Mở rộng toàn bộ node trong beam hiện tại
        for pos, mask in cur_beam:
            if pos == end and mask == ALL_MASK:
                # reconstruct
                goal_key = (pos, mask)
                path = []
                k = goal_key
                while k is not None:
                    path.append(k[0])
                    k = parent[k]
                path.reverse()
                collected = total_treasures
                return path, collected, total_treasures, explored_flat

            r, c = pos
            for dr, dc in directions:
                nr, nc = r+dr, c+dc
                if not (in_bounds(nr, nc) and maze[nr][nc] != "*"):
                    continue
                npos = (nr, nc)
                nmask = mask
                if npos in treasure_index:
                    nmask |= 1 << treasure_index[npos]

                # đánh dấu explored pos (không cần theo mask)
                if npos not in seen_explored_pos:
                    seen_explored_pos.add(npos)
                    explored_flat.append(npos)

                key = (npos, nmask)
                # chỉ nhận nếu chưa có depth tốt hơn cho state này
                old = best_depth.get(key)
                if old is None or depth < old:
                    best_depth[key] = depth
                    parent[key] = (pos, mask)
                    candidates.append(key)

        if not candidates:
            break

        # Chọn beam_width tốt nhất theo heuristic
        # (Loại trùng lặp key nếu phát sinh)
        # Sắp xếp theo score tăng dần
        uniq = {}
        for k in candidates:
            if k not in uniq:
                uniq[k] = score_state(k[0], k[1])

        # giữ top-k
        sorted_keys = sorted(uniq.items(), key=lambda x: x[1])
        cur_beam = [k for k, _ in sorted_keys[:beam_width]]

        # Kiểm tra goal trong top-k ngay sau cắt tỉa
        for pos, mask in cur_beam:
            if pos == end and mask == ALL_MASK:
                # reconstruct
                goal_key = (pos, mask)
                path = []
                k = goal_key
                while k is not None:
                    path.append(k[0])
                    k = parent[k]
                path.reverse()
                collected = total_treasures
                return path, collected, total_treasures, explored_flat

    # Không tìm được đường đi thoả mãn
    return None, 0, total_treasures, explored_flat


# UCS 
def ucs_maze_collect_all_to_goal(maze):
    rows, cols = len(maze), len(maze[0])

    start = end = None
    treasures = []

    for r in range(rows):
        for c in range(cols):
            v = maze[r][c]
            if v == "A":
                start = (r, c)
            elif v == "B":
                end = (r, c)
            elif v == "t":
                treasures.append((r, c))

    total_treasures = len(treasures)
    if start is None or end is None:
        return None, 0, total_treasures, []

    treasure_index = {pos: idx for idx, pos in enumerate(treasures)}
    ALL_MASK = (1 << total_treasures) - 1

    # --- cost mỗi bước (bạn có thể chỉnh nếu có loại địa hình khác) ---
    def step_cost(from_pos, to_pos):
        return 1  # mặc định mỗi bước = 1

    def in_bounds(x, y): return 0 <= x < rows and 0 <= y < cols

    directions = [(-1,0), (1,0), (0,-1), (0,1)]

    # Để hiển thị quá trình mở rộng trên UI (flatten theo toạ độ duy nhất)
    explored_flat = []
    seen_explored_pos = set()

    # Priority queue: (g_cost, pos, mask)
    # parent để dựng path: parent[(pos, mask)] = (prev_pos, prev_mask)
    pq = []
    start_mask = 0
    if start in treasure_index:
        start_mask |= 1 << treasure_index[start]

    heapq.heappush(pq, (0, start, start_mask))
    parent = {(start, start_mask): None}

    # best_g lưu chi phí nhỏ nhất đã biết cho mỗi state
    best_g = {(start, start_mask): 0}

    # đánh dấu explored pos lần đầu (cho UI)
    if start not in seen_explored_pos:
        seen_explored_pos.add(start)
        explored_flat.append(start)

    # Trường hợp start đã là goal và có đủ kho báu (hiếm khi xảy ra)
    if start == end and start_mask == ALL_MASK:
        return [start], total_treasures, total_treasures, explored_flat

    while pq:
        if stopRunning():
            return None, 0, total_treasures, explored_flat

        g, pos, mask = heapq.heappop(pq)
        # Nếu đây không còn là chi phí tốt nhất cho state này, bỏ qua
        if best_g.get((pos, mask), float("inf")) < g:
            continue

        # Cập nhật mask khi nhặt kho báu tại pos
        if pos in treasure_index:
            new_mask_here = mask | (1 << treasure_index[pos])
            if new_mask_here != mask:
                mask = new_mask_here  # cập nhật ngay tại nút đang xét

        # Điều kiện kết thúc
        if pos == end and mask == ALL_MASK:
            # reconstruct path
            path = []
            key = (pos, mask)
            while key is not None:
                path.append(key[0])
                key = parent[key]
            path.reverse()
            return path, total_treasures, total_treasures, explored_flat

        r, c = pos
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if not (in_bounds(nr, nc) and maze[nr][nc] != "*"):
                continue

            npos = (nr, nc)
            nmask = mask
            if npos in treasure_index:
                nmask |= 1 << treasure_index[npos]

            # đánh dấu explored pos cho UI
            if npos not in seen_explored_pos:
                seen_explored_pos.add(npos)
                explored_flat.append(npos)

            new_g = g + step_cost(pos, npos)
            state = (npos, nmask)
            if new_g < best_g.get(state, float("inf")):
                best_g[state] = new_g
                parent[state] = (pos, mask)
                heapq.heappush(pq, (new_g, npos, nmask))

    # Không tìm thấy đường hợp lệ (nhặt hết kho báu rồi tới B)
    return None, 0, total_treasures, explored_flat


# BACKTRACKING
def backtracking_maze_collect_all_to_goal(maze, max_depth=100000, time_limit=3.0):
    rows, cols = len(maze), len(maze[0])

    # ---- Tìm A, B, kho báu ----
    start = end = None
    treasures = []
    for i in range(rows):
        for j in range(cols):
            v = maze[i][j]
            if v == "A": start = (i, j)
            elif v == "B": end = (i, j)
            elif v == "t": treasures.append((i, j))

    total_treasures = len(treasures)
    if start is None or end is None:
        return None, 0, total_treasures, []

    treasure_index = {pos: idx for idx, pos in enumerate(treasures)}
    ALL_MASK = (1 << total_treasures) - 1

    def in_bounds(x, y): 
        return 0 <= x < rows and 0 <= y < cols

    def manhattan(a, b): 
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Heuristic: target gần nhất + áp lực số kho báu còn lại
    def heuristic(pos, mask):
        remaining = []
        for idx, tpos in enumerate(treasures):
            if not (mask & (1 << idx)):
                remaining.append(tpos)
        rem_cnt = len(remaining)
        if rem_cnt > 0:
            dmin = min(manhattan(pos, t) for t in remaining)
        else:
            dmin = manhattan(pos, end)
        return dmin + 2 * rem_cnt

    directions = [(-1,0),(1,0),(0,-1),(0,1)]

    # Theo dõi cho UI
    explored_flat = []
    seen_explored_pos = set()

    # best cho branch-and-bound
    best_path = None
    best_len = float("inf")

    # Lưu độ sâu tốt nhất đã thấy cho mỗi state để tránh lặp kém
    best_depth = {}  # key: (pos, mask) -> depth (path_len - 1)

    # Khởi tạo
    start_mask = 0
    if start in treasure_index:
        start_mask |= 1 << treasure_index[start]

    start_time = time.time()

    # Đánh dấu explored tại start
    if start not in seen_explored_pos:
        seen_explored_pos.add(start)
        explored_flat.append(start)

    # Nếu ngay từ đầu đã xong
    if start == end and start_mask == ALL_MASK:
        return [start], total_treasures, total_treasures, explored_flat

    # Sắp xếp hướng đi theo heuristic để dẫn đường tốt hơn
    def ordered_neighbors(pos, mask):
        r, c = pos
        cand = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if in_bounds(nr, nc) and maze[nr][nc] != "*":
                npos = (nr, nc)
                nmask = mask
                if npos in treasure_index:
                    nmask |= 1 << treasure_index[npos]
                h = heuristic(npos, nmask)
                cand.append((h, npos, nmask))
                # đánh dấu explored pos cho UI (chỉ 1 lần)
                if npos not in seen_explored_pos:
                    seen_explored_pos.add(npos)
                    explored_flat.append(npos)
        # Ưu tiên h nhỏ
        cand.sort(key=lambda x: x[0])
        return [(npos, nmask) for _, npos, nmask in cand]

    # DFS đệ quy
    def dfs(pos, mask, path):
        nonlocal best_path, best_len

        # Ngắt an toàn
        if stopRunning():
            return
        if time.time() - start_time > time_limit:
            return
        if len(path) > max_depth:
            return

        # Đã đủ kho báu và tới B
        if pos == end and mask == ALL_MASK:
            if len(path) < best_len:
                best_len = len(path)
                best_path = path[:]
            return

        # Bound: nếu đường ngắn nhất có thể (ước lượng) vẫn không thắng best hiện tại → cắt
        if best_len < float("inf"):
            if len(path) + heuristic(pos, mask) >= best_len:
                return

        # Tránh mở rộng state kém hơn
        cur_depth = len(path) - 1
        key = (pos, mask)
        if key in best_depth and cur_depth >= best_depth[key]:
            return
        best_depth[key] = cur_depth

        # Mở rộng theo thứ tự ưu tiên
        for npos, nmask in ordered_neighbors(pos, mask):
            path.append(npos)
            dfs(npos, nmask, path)
            path.pop()

    dfs(start, start_mask, [start])

    if best_path is None:
        # Không tìm được lộ trình ăn hết kho báu rồi tới B
        return None, 0, total_treasures, explored_flat

    # Đếm lại số kho báu trên best_path (nên = total_treasures)
    collected_mask = 0
    for p in best_path:
        if p in treasure_index:
            collected_mask |= 1 << treasure_index[p]
    collected = bin(collected_mask).count("1")

    return best_path, collected, total_treasures, explored_flat

if __name__ == "__main__":
    maze = [
                "*  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *",
                "*  .   *   ?   .   .   .   .   .   .   .   .   *   .   .   .   *",
                "*  .   *   *   *   .   *   *   *   *   *   .   *   .   *   *   *",
                "*  .   .   .   .   .   *   .   *   .   .   .   *   .   .   .   *",
                "*  *   *   *   *   *   *   .   *   .   *   *   *   .   *   .   *",
                "*  .   .   .   .   .   *   .   *   .   .   .   *   .   *   .   *",
                "*  .   *   *   *   .   *   .   *   *   *   .   *   .   *   .   *",
                "A  ?   .   .   *   .   .   .   .   .   *   .   *   .   *   .   B",
                "*  .   *   .   *   .   *   *   *   *   *   .   *   *   *   .   *",
                "*  .   *   .   *   .   *   .   .   .   *   .   .   .   *   .   *",
                "*  .   *   .   *   .   *   .   *   .   *   *   *   .   *   .   *",
                "*  .   *   .   *   .   *   .   *   .   .   .   *   .   *   .   *",
                "*  .   *   .   *   *   *   .   *   *   *   .   *   .   *   .   *",
                "*  .   *   .   .   .   .   .   .   .   *   .   .   .   .   t   *",
                "*  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *"
    ]
    
    def coverWall_inMaze(maze):
        maze_copy = [list(row) for row in maze]  # mỗi dòng thành list để có thể sửa
        height = len(maze_copy)
        width = len(maze_copy[0])
        for i in range(height):
            for j in range(width):
                if (maze_copy[i][j] == "*" or maze_copy[i][j] == "?") and i != 0 and i != height-1 and j != 0 and j != width-1:
                    maze_copy[i][j] = "."
        maze_copy = ["\t".join(row) for row in maze_copy]
        return maze_copy
    
    def processMazeStructure(mazeArr):
        processed = []
        for line in mazeArr:
            row = line.strip().split()
            processed.append(row)
        return processed
    
    mz = processMazeStructure(coverWall_inMaze(maze))
    mx = processMazeStructure(maze)
    # for i in processMazeStructure(maze):
    for i in mx:
        print(i)
    
    a, b = POS_algorithm((mx, mz))
    print(a)
    print(countAllTreasure(mx))