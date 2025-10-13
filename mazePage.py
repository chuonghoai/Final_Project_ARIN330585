import tkinter as tk
from PIL import Image, ImageTk
from uiComponents import ButtonObj, ImageObj, ComboBoxObj, mazeObj, textObj, TimerObj, AudioControl
import tkextrafont
import algorithm
import time
import threading
import random

class mazePage:
    def __init__(self, root, avtChoosed, width=1100, height=700):
        self.root = root
        
        # Kích thước giao diện
        self.width = width
        self.height = height

        # Kiểm soát nút start
        self.enableStartBtn = True

        # Avarta đã chọn từ trang trước
        self.avtChoosed = avtChoosed
        
        # Thuật toán đã chọn từ combo box
        self.algorithmChoosed = None
        
        # Nạp font chữ
        self.fontMinecraft = "Minecraft Ten"
        self.fontGluten = "Gluten"
        
        # Canvas chung cho cả giao diện
        self.canvas = tk.Canvas(root, width=width, height=height, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.image_refs = []
        
        # Hàng đợi của các hoạt ảnh hiệu ứng
        self.animating = False
        self._after_ids = []
        
        # Cờ của thread chạy algorithm
        self.stopAlgorithm = False
        
        # Vẽ bộ đếm thời gian        
        self.timer = TimerObj(self.canvas)
        
        # Vẽ background
        self.draw_background()

        # Vẽ nút start
        self.draw_startbtn()

        # Vẽ combo box chọn thuật toán
        self.draw_cbbox()
        
        # Thêm nút back
        self.draw_back()
        
        # Mê cung thiết kế sẵn
        self.mazeArr = [
            [
                "*	*	*	*	*	*	*	*	*	*	*	*	*	*	*	*	*",
                "*	.	*	.	.	.	.	.	.	?	.	.	.	.	.	t	*",
                "*	.	*	.	*	*	*	.	*	.	*	.	*	*	*	.	*",
                "*	.	.	.	*	t	*	.	*	.	*	.	.	.	*	.	*",
                "*	.	*	*	*	.	*	.	*	.	*	*	*	.	*	.	*",
                "*	.	.	.	.	.	*	.	*	.	?	.	*	.	*	.	*",
                "*	*	*	.	*	*	*	.	*	*	*	.	*	.	*	*	*",
                "*	.	.	.	*	.	.	.	*	t	.	.	*	.	.	.	*",
                "*	.	*	*	*	.	*	*	*	.	*	*	*	*	*	.	*",
                "*	.	.	.	*	.	.	.	*	.	*	.	.	.	*	.	*",
                "*	*	*	.	*	*	*	.	*	.	*	.	*	.	*	.	*",
                "*	.	.	.	.	.	*	.	*	.	.	.	*	.	.	.	*",
                "*	*	*	*	*	*	*	.	*	*	*	*	*	*	*	.	*",
                "*	.	.	.	t	.	.	.	*	.	.	.	.	.	.	?	*",
                "*	A	*	*	*	*	*	*	*	*	*	*	*	*	*	B	*"
            ],
            [
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
                "*  .   .   .   .   .   .   .   .   .   *   .   .   .   .   t   *",
                "*  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *"
            ],
            [
                "*  *   *   *   *   *   *   *   A   *   *   *   *   *   *   *   *",
                "*  .   *   .   t   .   .   .   .   .   *   .   .   .   .   .   *",
                "*  .   *   *   *   .   *   *   *   ?   *   .   *   *   *   .   *",
                "*  .   *   .   .   .   *   .   *   .   *   .   *   .   .   .   *",
                "*  .   *   .   *   *   *   .   *   .   *   .   *   .   *   *   *",
                "*  ?   .   .   *   .   *   .   .   .   *   .   *   .   .   .   *",
                "*  *   *   *   *   .   *   .   *   *   *   .   *   *   *   .   *",
                "*  .   .   .   *   ?   .   .   *   .   .   .   *   .   .   .   *",
                "*  .   *   *   *   .   *   *   *   .   *   .   *   .   *   *   *",
                "*  .   .   .   .   .   *   .   .   .   *   .   *   .   *   .   *",
                "*  .   *   *   *   *   *   *   *   *   *   .   *   .   *   .   *",
                "*  .   .   .   *   .   .   .   *   .   .   .   .   .   *   .   *",
                "*  *   *   .   *   .   *   .   *   .   *   *   *   .   *   .   *",
                "*  .   .   .   .   .   *   .   .   .   *   .   .   .   .   t   *",
                "*  *   *   *   *   *   *   *   B   *   *   *   *   *   *   *   *"
            ]
        ]
        
        self.goal_gif_click_id = None
        self.goal_gif_after = None
        self.text1_click_id = None
        self.text1_after = None
        self.text2_click_id = None
        self.text2_after = None
        
        # Vẽ mê cung
        self.maze = mazeObj(self.canvas, self.animating, self._after_ids)
        self.mazeIndex = 0
        self.draw_maze(self.mazeArr[self.mazeIndex])
        
        # Vẽ nút reset mê cung
        self.draw_reset()
        
        # Vẽ nút âm thanh
        self.audio = AudioControl(self.canvas, x=220, y=35)
        
    # Vẽ background
    def draw_background(self):
        # Load ảnh từ gallery
        avtPath = ""
        avtWarning = ""
        if self.avtChoosed == "HACHI":
            avtPath = "Gallery/HachiBackground.png"
        elif self.avtChoosed == "CHIKAWA":
            avtPath = "Gallery/ChikawaBackground.png"
        elif self.avtChoosed == "USAGI":
            avtPath = "Gallery/UsagiBackground.png"
        avtWarning = "Gallery/warning.png"
        cantFindPathImg = "Gallery/cantFindPath.png"
        
        # Vẽ ảnh nền
        self.bg_img = ImageObj(self.canvas)
        self.bg_img_id = self.bg_img.create_image(
            self.width//2, self.height//2,
            avtPath,
            w=self.width, h=self.height
        )
        
        # Vẽ trước ảnh cảnh báo chưa chọn thuật toán
        self.bg_warning = ImageObj(self.canvas)
        self.bg_warning_id = self.bg_warning.create_image(
            self.width//2, self.height//2,
            avtWarning,
            w=self.width, h=self.height
        )
        self.canvas.itemconfigure(self.bg_warning_id, state="hidden")

        # Vẽ trước ảnh thông báo ko tìm thấy đường đi
        self.bgCantFindPath = ImageObj(self.canvas)
        self.bgCantFindPath_id = self.bgCantFindPath.create_image(
            self.width//2, self.height//2,
            cantFindPathImg,
            w=self.width, h=self.height
        )
        self.canvas.itemconfigure(self.bgCantFindPath_id, state="hidden")

    def draw_congratulation_reachGoal(self, collected, total_treasure):
        # Vẽ gif
        goalPath = "Gallery/goal.gif"
        self.goal_gif = ImageObj(self.canvas)
        self.goal_gif.create_gif(self.width//2, self.height//2, goalPath, w=self.width, h=self.height)

        # Thêm text
        self.text1 = textObj(self.canvas)
        self.text2 = textObj(self.canvas)
        self.text1.create_text(
            self.width//2, 80,
            text="Chúc mừng bạn đã đến đích",   
            font=self.fontGluten, font_size=50, font_style="normal",
            text_color="#262a30"
        )
        self.text2.create_text(
            self.width//2, self.height - 80,
            text=f"Bạn đã ăn đc {collected}/{total_treasure} cà chua",
            font=self.fontGluten, font_size=50, font_style="normal",
            text_color="#262a30"
        )
        
        # Hàm xóa gif nếu click chuột vào màn hình
        def hide_gif(e=None):
            # Xóa gif
            if hasattr(self, "goal_gif"):
                self.canvas.delete(self.goal_gif.item_id)
                del self.goal_gif
            if hasattr(self, "goal_gif_after"):
                self.root.after_cancel(self.goal_gif_after)
                del self.goal_gif_after

            # Xóa text
            for attr in ["text1", "text2"]:
                if hasattr(self, attr):
                    self.canvas.delete(getattr(self, attr).item_id)
                    delattr(self, attr)
            for attr in ["text1_after", "text2_after"]:
                if hasattr(self, attr):
                    self.root.after_cancel(getattr(self, attr))
                    delattr(self, attr)

        # Bind 1 lần cho cả màn hình
        self.goal_gif_click_id = self.root.bind("<Button-1>", hide_gif)
        # Tự động xóa sau 4s
        self.goal_gif_after = self.root.after(4000, hide_gif)
        self.text1_after = self.root.after(4000, hide_gif)
        self.text2_after = self.root.after(4000, hide_gif)
        
    # Vẽ nút start: 
    def draw_startbtn(self):
        self.startBtn = ButtonObj(self.canvas)
        self._stBtn, self._stTxt = self.startBtn.create_button(
            self.width - 185, self.height//2 - 100,
            w=200, h=50,
            text="START", text_color="white",
            font=self.fontMinecraft,
            command=lambda: self.startClick()
        )
        
    # Vẽ combo box chọn thuật toán
    def draw_cbbox(self):
        values = ["BFS", "And-Or Tree", "Belief state", "Partially observable", "AC-3", "Hill Climbing"]
        self.algorithmCbb = ComboBoxObj(self.canvas)
        self.algorithmCbb.createComboBox(
            self.width - 185, self.height//2 - 200,
            values=values, 
            font=self.fontGluten,
            w = 270,
            startBtn=(self._stBtn, self._stTxt),
            onSelect=self.on_algorithm_change
        )
    
    # Che đi phần lớn mê cung để truyền cho thuật toán Partially observable
    def blindMaze(self, maze):
        # Sao chép mê cung
        maze_copy = [list(row) for row in maze]
        height = len(maze_copy)
        width = len(maze_copy[0])

        treasure_positions = [(i, j) for i in range(height) for j in range(width) if maze_copy[i][j] == 't']

        for i in range(height):
            for j in range(width):
                if (maze_copy[i][j] == "*" or maze_copy[i][j] == "?" or maze_copy[i][j] == "t") \
                    and i != 0 and i != height-1 and j != 0 and j != width-1:
                    maze_copy[i][j] = "."

        if treasure_positions:
            n_treasures = random.randint(1, len(treasure_positions))
            chosen = random.sample(treasure_positions, n_treasures)
            for (i, j) in chosen:
                maze_copy[i][j] = "t"

        maze_copy = ["\t".join(row) for row in maze_copy]
        return maze_copy

    
    # Kiểm tra khi thay đổi thuật toán
    def on_algorithm_change(self, value):
        self.resetMaze(changeMaze=False)
        if not (hasattr(self, "maze") and self.maze.avatar_id):
            return

        if value == "Belief state":
            self.maze.hide_avatar()
            return

        if value == "Partially observable":
            self.maze.show_avatar()
            self.mazeCoverWall = self.blindMaze(self.mazeArr[self.mazeIndex])
            self.draw_maze(self.mazeCoverWall)
            return

        self.maze.show_avatar()
        self.draw_maze(self.mazeArr[self.mazeIndex])
    
    # Thêm nút quay lui
    def draw_back(self):
        self.backBtn = ButtonObj(self.canvas)
        self.backBtn.create_button(
            125, 50,
            w=150, h=45,
            text="Back", font_size=23, 
            font=self.fontMinecraft,
            text_color="white",
            command=self.run_chooseAvt
        )
    
    # Hàm quay lui
    def run_chooseAvt(self):
        from chooseAvt import chooseAvt
        chooseAvt(self.root, self.width, self.height)
        self.canvas.pack_forget()
        
    # Hàm kích hoạt của nút start
    def startClick(self):
        self.resetMaze(changeMaze=False, resetBindMaze=False)
        
        def hideWarning(e=None):
            """Ẩn warning ngay khi click"""
            self.canvas.itemconfigure(self.bg_warning_id, state="hidden")
            self.canvas.itemconfigure(self.bgCantFindPath_id, state="hidden")

            # Hủy after nếu còn tồn tại
            if hasattr(self, "warning_after"):
                self.root.after_cancel(self.warning_after)
                del self.warning_after
            if hasattr(self, "cantFindPath_after"):
                self.root.after_cancel(self.cantFindPath_after)
                del self.cantFindPath_after
            self.root.unbind("<Button-1>")
            
        self.algorithmChoosed = self.algorithmCbb.getValue()
        
        if self.algorithmChoosed:
            if (self.enableStartBtn and not self.maze.is_reach_goal) or self.maze.is_reach_goal:
                # if self.maze.is_reach_goal:
                #     self.draw_maze(self.mazeArr[self.mazeIndex])
                self.enableStartBtn = False
                
                # Kiểm tra thuật toán đang chọn có phải là POS ko
                mazeCover = None
                if self.algorithmChoosed == "Partially observable":
                    mazeCover = self.processMazeStructure(self.mazeCoverWall)
                
                # lấy dữ liệu mê cung truyền vào thuật toán
                maze = self.processMazeStructure(self.mazeArr[self.mazeIndex])

                # Vẽ bộ đếm thời gian
                self.timer.draw(350, 50)

                def ProcessDone():
                    self.timer.stop()
                    
                    if self.maze.processDone and hasattr(self, "maze"):
                        self.maze.processDone = False
                        self.maze.show_avatar()

                    # Kiểm tra nhân vật đã đến đích chưa
                    def check_reach_goal():
                        if self.maze.is_reach_goal:
                            if not reachedGoal and self.algorithmCbb.getValue() == "Hill Climbing" and path:
                                print("Không tìm được đường đi")
                                self.canvas.itemconfigure(self.bgCantFindPath_id, state="normal")
                                self.canvas.tag_raise(self.bgCantFindPath_id)
                                self.cantFindPath_after = self.root.after(
                                    3000, lambda: self.canvas.itemconfigure(self.bgCantFindPath_id, state="hidden"))
                                self.root.after(50, lambda: self.root.bind("<Button-1>", hideWarning))
                                return
                            else:
                                self.draw_congratulation_reachGoal(collected, total_treasure)
                            self.enableStartBtn = True
                        else:
                            after_id = self.root.after(100, check_reach_goal)
                            self._after_ids.append(after_id)
                    check_reach_goal()

                def run_algorithm():
                    nonlocal path, collected, total_treasure, process, all_process_by_limit, maze, reachedGoal
                    self.stopAlgorithm = False

                    if mazeCover:
                        _maze = (maze, mazeCover)
                    else:
                        _maze = maze
                        
                    result = algorithm.chooseAlgorithm(
                        self.algorithmChoosed, _maze, _stopRunning=lambda: self.stopAlgorithm)
                    
                    if not result:
                        print("Thuật toán chưa hỗ trợ")
                        self.timer.reset()
                        return
                    if self.algorithmCbb.getValue() == "Hill Climbing":
                        path, collected, total_treasure, process, reachedGoal = result
                    else:
                        path, collected, total_treasure, process = result
                    
                    self.root.after(0, lambda: on_algorithm_done())

                def on_algorithm_done():
                    if self.algorithmCbb.getValue() == "Belief state":
                        self.maze.processDone = False
                    print(f"Bạn đã chọn thuật toán {self.algorithmChoosed}")
                    
                    if self.algorithmCbb.getValue() == "Partially observable":
                        self.maze.draw_path_POS(maze, path, onFinish=ProcessDone)
                    else:    
                        self.maze.draw_search_process(process, path, onFinish=ProcessDone)

                # Chạy thread
                path = collected = total_treasure = process = all_process_by_limit = None
                reachedGoal = None
                self.thread = threading.Thread(target=run_algorithm)
                self.thread.start()
        else:
            print("Hãy chọn thuật toán trước bạn nhé")
            self.canvas.itemconfigure(self.bg_warning_id, state="normal")
            self.canvas.tag_raise(self.bg_warning_id)
            self.warning_after = self.root.after(3000, lambda: self.canvas.itemconfigure(self.bg_warning_id, state="hidden"))
            self.root.after(50, lambda: self.root.bind("<Button-1>", hideWarning))
        
    # Hàm reset và thay đối mê cung (nếu có)
    def resetMaze(self, changeMaze=True, resetBindMaze=True):
        self.enableStartBtn = True
        self.stopAlgorithm = True
        self.maze.processDone = False
        self.maze.is_reach_goal = False
        self.timer.reset()
        
        if hasattr(self, "thread") and self.thread.is_alive():
            self.thread.join(timeout=0.2)
        
        # Hủy toàn bộ hoạt ảnh đang chạy
        if hasattr(self, "_after_ids"):
            for aid in self._after_ids:
                try:
                    self.canvas.after_cancel(aid)
                except:
                    pass
            self._after_ids.clear()

        self.animating = False

        if changeMaze:
            self.mazeIndex = (self.mazeIndex + 1) % len(self.mazeArr)
        _maze = self.mazeArr[self.mazeIndex]
        hideAvt = False
        
        # Kiểm tra nếu thuật toán đang chọn là belief thì ẩn avarta
        if hasattr(self, "algorithmCbb"):
            value = self.algorithmCbb.getValue()
            if value and value == "Belief state":
                hideAvt = True
                self.maze.hide_avatar()
                self.maze.processDone = False
            elif value and value == "Partially observable":
                if resetBindMaze:
                    self.mazeCoverWall = self.blindMaze(self.mazeArr[self.mazeIndex])
                _maze = self.mazeCoverWall
                self.maze.processDone = False

        self.draw_maze(_maze, hideAvt=hideAvt)
    
    # Nút reset
    def draw_reset(self):
        self.resetBtn = ButtonObj(self.canvas)
        self.resetBtn.create_button(
            self.width//2 + 280, self.height - 35,
            w=150, h=40,
            text="RESET", font_size=15,
            font=self.fontMinecraft,
            font_style="normal",
            command=self.resetMaze
        )

    # Hàm vẽ mê cung
    def draw_maze(self, mazeArr, hideAvt=False):
        if self.avtChoosed == "HACHI":
            avt = "Gallery/Hachi_Avt.png"
        elif self.avtChoosed == "CHIKAWA":
            avt = "Gallery/Chikawa_Avt.png"
        elif self.avtChoosed == "USAGI":
            avt = "Gallery/Usagi_Avt.png"
        
        maze = self.processMazeStructure(mazeArr)
        self.maze.createMaze(
            self.width//2 - 160, self.height//2 + 35,
            maze,
            pathAvt=avt
        )
        
        if hideAvt:
            self.maze.hide_avatar()

    # Hàm tái cấu trúc lại mê cung về dạng chuẩn 2D list
    def processMazeStructure(self, mazeArr):
        processed = []
        for line in mazeArr:
            row = line.strip().split()
            processed.append(row)
        return processed

if __name__=="__main__":
    root = tk.Tk()
    app = mazePage(root, "USAGI")
    root.mainloop()
