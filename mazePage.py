import tkinter as tk
from PIL import Image, ImageTk
from UiComponents import ButtonObj, ImageObj, ComboBoxObj, mazeObj, textObj
import tkextrafont
import algorithm

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
                "*	.	*	.	.	.	.	.	.	.	.	.	.	.	t	.	*",
                "*	.	*	.	*	*	*	.	*	.	*	.	*	*	*	.	*",
                "*	.	.	.	*	.	*	.	*	.	*	.	.	.	*	.	*",
                "*	.	*	*	*	t	*	.	*	.	*	*	*	.	*	.	*",
                "*	.	.	.	.	.	*	.	*	.	.	.	*	.	*	.	*",
                "*	*	*	.	*	*	*	.	*	*	*	.	*	.	*	*	*",
                "*	.	.	.	*	.	.	.	*	.	.	.	*	.	.	.	*",
                "*	.	*	*	*	.	*	*	*	.	*	*	*	*	*	.	*",
                "*	.	.	.	*	.	.	.	*	.	*	.	.	.	*	.	*",
                "*	*	*	.	*	*	*	.	*	.	*	.	*	.	*	.	*",
                "*	.	.	.	.	.	*	.	*	.	.	.	*	.	.	.	*",
                "*	*	*	*	*	*	*	.	*	*	*	*	*	*	*	.	*",
                "*	.	.	.	.	.	.	.	*	t	.	.	.	.	.	.	*",
                "*	A	*	*	*	*	*	*	*	*	*	*	*	*	*	B	*"
            ],
            [
                "*  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *",
                "*  .   *   .   .   .   .   .   .   .   .   .   *   .   .   .   *",
                "*  .   *   *   *   .   *   *   *   *   *   .   *   .   *   *   *",
                "*  .   .   .   .   .   *   .   *   .   .   .   *   .   .   .   *",
                "*  *   *   *   *   *   *   .   *   .   *   *   *   .   *   .   *",
                "*  .   .   .   .   .   *   .   *   .   .   .   *   .   *   .   *",
                "*  .   *   *   *   .   *   .   *   *   *   .   *   .   *   .   *",
                "A  .   .   .   *   .   .   .   .   .   *   .   *   .   *   .   B",
                "*  .   *   .   *   .   *   *   *   *   *   .   *   *   *   .   *",
                "*  .   *   .   *   .   *   .   .   .   *   .   .   .   *   .   *",
                "*  .   *   .   *   .   *   .   *   .   *   *   *   .   *   .   *",
                "*  .   *   .   *   .   *   .   *   .   .   .   *   .   *   .   *",
                "*  .   *   .   *   *   *   .   *   *   *   .   *   .   *   .   *",
                "*  .   *   .   .   .   .   .   .   .   *   .   .   .   .   t   *",
                "*  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *"
            ],
            [
                "*  *   *   *   *   *   *   *   A   *   *   *   *   *   *   *   *",
                "*  .   *   .   t   .   .   .   .   .   *   .   .   .   .   .   *",
                "*  .   *   *   *   .   *   *   *   .   *   .   *   *   *   .   *",
                "*  .   *   .   .   .   *   .   *   .   *   .   *   .   .   .   *",
                "*  .   *   .   *   *   *   .   *   .   *   .   *   .   *   *   *",
                "*  .   .   .   *   .   *   .   .   .   *   .   *   .   .   .   *",
                "*  *   *   *   *   .   *   .   *   *   *   .   *   *   *   .   *",
                "*  .   .   .   *   .   .   .   *   .   .   .   *   .   .   .   *",
                "*  .   *   *   *   .   *   *   *   .   *   .   *   .   *   *   *",
                "*  .   .   .   .   .   *   .   .   .   *   .   *   .   *   .   *",
                "*  .   *   *   *   *   *   *   *   *   *   .   *   .   *   .   *",
                "*  .   .   .   *   .   .   .   *   .   .   .   *   .   *   .   *",
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
            self.width - 200, self.height//2 - 100,
            w=200, h=50,
            text="START", text_color="white",
            font=self.fontMinecraft,
            command=lambda: self.startClick()
        )
        
    # Vẽ combo box chọn thuật toán
    def draw_cbbox(self):
        values = ["BFS", "DFS", "IDL", "IDS", "UCS"]
        self.algorithmCbb = ComboBoxObj(self.canvas)
        self.algorithmCbb.createComboBox(
            self.width - 200, self.height//2 - 200,
            values=values, 
            font=self.fontGluten,
            w = 270,
            startBtn=(self._stBtn, self._stTxt)
        )
        
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
        def hideWarning(e=None):
            """Ẩn warning ngay khi click"""
            self.canvas.itemconfigure(self.bg_warning_id, state="hidden")

            # Hủy after nếu còn tồn tại
            if hasattr(self, "warning_after"):
                self.root.after_cancel(self.warning_after)
                del self.warning_after
            self.root.unbind("<Button-1>")
            
        self.algorithmChoosed = self.algorithmCbb.getValue()
        
        if self.algorithmChoosed:
            if (self.enableStartBtn and not self.maze.is_reach_goal) or self.maze.is_reach_goal:
                if self.maze.is_reach_goal:
                    self.draw_maze(self.mazeArr[self.mazeIndex])
                self.enableStartBtn = False
                maze = self.processMazeStructure(self.mazeArr[self.mazeIndex])
                path, collected, total_treasure, explored_order = algorithm.chooseAlgorithm(self.algorithmChoosed, maze)

                print(f"Bạn đã chọn thuật toán {self.algorithmChoosed}")
                print(path)
                print(collected)
                print(total_treasure)
                print(explored_order)
                self.maze.draw_search_process(explored_order, path)
                def check_reach_goal():
                    if self.maze.is_reach_goal:
                        self.draw_congratulation_reachGoal(collected, total_treasure)
                        self.enableStartBtn = True
                    else:
                        after_id = self.root.after(100, check_reach_goal)
                        self._after_ids.append(after_id)
                check_reach_goal()
        else:
            print("Hãy chọn thuật toán trước bạn nhé")
            self.canvas.itemconfigure(self.bg_warning_id, state="normal")
            self.canvas.tag_raise(self.bg_warning_id)

            self.warning_after = self.root.after(3000, lambda: self.canvas.itemconfigure(self.bg_warning_id, state="hidden"))
            self.root.after(50, lambda: self.root.bind("<Button-1>", hideWarning))
        
    # Hàm thay đổi mê cung (nút reset)
    def draw_reset(self):
        def resetMaze():
            self.enableStartBtn = True
            # Hủy toàn bộ hoạt ảnh đang chạy
            if hasattr(self, "_after_ids"):
                for aid in self._after_ids:
                    try:
                        self.canvas.after_cancel(aid)
                    except:
                        pass
                self._after_ids.clear()

            self.animating = False

            self.mazeIndex = (self.mazeIndex + 1) % len(self.mazeArr)
            self.draw_maze(self.mazeArr[self.mazeIndex])

        self.resetBtn = ButtonObj(self.canvas)
        self.resetBtn.create_button(
            self.width//2 + 280, self.height - 35,
            w=150, h=40,
            text="RESET", font_size=15,
            font=self.fontMinecraft,
            font_style="normal",
            command=resetMaze
        )

    # Hàm vẽ mê cung
    def draw_maze(self, mazeArr):
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

    # Hàm tái cấu trúc lại mê cung về dạng chuẩn 2D list
    def processMazeStructure(self, mazeArr):
        processed = []
        for line in mazeArr:
            row = line.strip().split()
            processed.append(row)
        return processed

root = tk.Tk()
app = mazePage(root, "USAGI")
root.mainloop()