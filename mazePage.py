import tkinter as tk
from PIL import Image, ImageTk
from uiComponents import ButtonObj, ImageObj, ComboBoxObj

class mazePage:
    def __init__(self, root, width=1100, height=700):
        self.root = root
        # Kích thước giao diện
        self.width = width
        self.height = height
        
        # Canvas chung cho cả giao diện
        self.canvas = tk.Canvas(root, width=width, height=height, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.image_refs = []
        
        # Vẽ background
        self.draw_background()
        
        # Lặp background
        self.bg_idx = 0
        self.loop_background()

        # Vẽ nút start
        self.draw_startbtn()
        
        # Vẽ combo box chọn thuật toán
        self.draw_cbbox()
        
    # Vẽ background thay đổi liên tục
    def draw_background(self):
        self.chikawa_bg = ImageObj(self.canvas)
        self.bg_id = self.chikawa_bg.create_image(
            self.width//2, self.height//2,
            "Gallery/ChikawaBackground.png",
            w=self.width, h=self.height
        )

    # Lặp liên tục background
    def loop_background(self):
        self.list_bg = [
            "Gallery/UsagiBackground.png",
            "Gallery/ChikawaBackground.png",
            "Gallery/HachiBackground.png"
        ]
        
        self.bg_image = [ImageTk.PhotoImage(Image.open(f).resize((self.width, self.height))) for f in self.list_bg]
        self.bg_idx = (self.bg_idx + 1) % len(self.bg_image)
        self.canvas.itemconfigure(self.bg_id, image=self.bg_image[self.bg_idx])
        
        self.root.after(1000, self.loop_background)
        
    # Vẽ nút start: 
    def draw_startbtn(self):
        self.startBtn = ButtonObj(self.canvas)
        self._stBtn, self._stTxt = self.startBtn.create_button(
            self.width - 200, self.height//2 - 100,
            w=200, h=50,
            text="START", text_color="white",
            command=lambda: print("play game")
        )
        
    # Vẽ combo box chọn thuật toán
    def draw_cbbox(self):
        values = ["BFS", "DFS", "IDL", "IDS", "UCS"]
        self.cbbox = ComboBoxObj(self.canvas)
        self.cbbox.createComboBox(
            self.width -200, self.height//2 - 200,
            values=values, startBtn=(self._stBtn, self._stTxt)
        )

def runApp():
    root = tk.Tk()
    app = mazePage(root)
    root.mainloop()
    
runApp()