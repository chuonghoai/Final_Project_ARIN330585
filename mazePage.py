import tkinter as tk
from PIL import Image, ImageTk
from UiComponents import ButtonObj, ImageObj, ComboBoxObj
import tkextrafont

class mazePage:
    def __init__(self, root, avtChoosed, width=1100, height=700):
        self.root = root
        
        # Kích thước giao diện
        self.width = width
        self.height = height

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
        
        # Vẽ background
        self.draw_background()

        # Vẽ nút start
        self.draw_startbtn()

        # Vẽ combo box chọn thuật toán
        self.draw_cbbox()
        
        # Thêm nút back
        self.draw_back()
        
    # Vẽ background
    def draw_background(self):
        avtPath = ""
        avtWarning = ""
        if self.avtChoosed == "HACHI":
            avtPath = "Gallery/HachiBackground.png"
        elif self.avtChoosed == "CHIKAWA":
            avtPath = "Gallery/ChikawaBackground.png"
        elif self.avtChoosed == "USAGI":
            avtPath = "Gallery/UsagiBackground.png"
        avtWarning = "Gallery/warning.png"
            
        self.bg_img = ImageObj(self.canvas)
        self.bg_img_id = self.bg_img.create_image(
            self.width//2, self.height//2,
            avtPath,
            w=self.width, h=self.height
        )
        
        self.bg_warning = ImageObj(self.canvas)
        self.bg_warning_id = self.bg_warning.create_image(
            self.width//2, self.height//2,
            avtWarning,
            w=self.width, h=self.height
        )
        self.canvas.itemconfigure(self.bg_warning_id, state="hidden")
        
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
            110, 50,
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
        self.algorithmChoosed = self.algorithmCbb.getValue()
        if self.algorithmChoosed:
            print(f"Bạn đã chọn thuật toán {self.algorithmChoosed}")
        else:
            print("Hãy chọn thuật toán trước bạn nhé")
            self.canvas.itemconfigure(self.bg_warning_id, state="normal")
            self.canvas.tag_raise(self.bg_warning_id)

            self.warning_after = self.root.after(3000, lambda: self.canvas.itemconfigure(self.bg_warning_id, state="hidden"))
            self.root.after(50, lambda: self.root.bind("<Button-1>", self.hideWarning))
        
    def hideWarning(self, e=None):
        """Ẩn warning ngay khi click"""
        self.canvas.itemconfigure(self.bg_warning_id, state="hidden")

        # Hủy after nếu còn tồn tại
        if hasattr(self, "warning_after"):
            self.root.after_cancel(self.warning_after)
            del self.warning_after
        self.root.unbind("<Button-1>")
            
def runApp():
    root = tk.Tk()
    app = mazePage(root, "USAGI")
    root.mainloop()
    
runApp()