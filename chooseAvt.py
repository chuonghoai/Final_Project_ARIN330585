import tkinter as tk
from PIL import Image, ImageTk
from UiComponents import ButtonObj, ImageObj
from tkinter import font as tkFont

class chooseAvt:
    def __init__(self, root, width=1100, height=700):
        self.root = root
        # Kích thước giao diện
        self.width = width
        self.height = height
        
        # Nạp font chữ
        self.font = "Minecraft Ten"

        # Kích thước avarta
        self.frameAvtWidth = 270
        self.frameAvtHeight = 270

        # Canvas chung cho cả giao diện
        self.canvas = tk.Canvas(root, width=width, height=height, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.image_refs = []

        #Kích thước nút
        self.frameBtnHeight = 75
        
        # Canvas chứa tiêu đề chữ CHOOSE và CHARACTER
        # Container chứa tiêu đề
        self.title_height = 100
        frame_title = tk.Frame(
            self.canvas,
            width=self.width,
            height=self.title_height * 2 + 50,  # đủ chứa 2 dòng
            bg="white", bd=0, highlightthickness=0
        )
        frame_title.place(x=0, y=30)  # cách top 50px

        # Canvas dòng "CHOOSE"
        self.canvas_CHOOSE = tk.Canvas(
            frame_title,
            width=self.width, height=self.title_height + 20,
            bg="white", bd=0, highlightthickness=0
        )
        self.canvas_CHOOSE.pack(fill="both")
        self.canvas_CHOOSE.image_refs = []

        # Canvas dòng "CHARACTER"
        self.canvas_CHARACTER = tk.Canvas(
            frame_title,
            width=self.width, height=self.title_height + 20,
            bg="white", bd=0, highlightthickness=0
        )
        self.canvas_CHARACTER.pack(fill="both")
        self.canvas_CHARACTER.image_refs = []
                
        # Vẽ nền trắng và tiêu đề
        self.draw_bgAndtitle()
        
        # Canvas chứa 3 hình ảnh avarta
        frame_avt = tk.Frame(
            self.canvas, 
            width=self.width, height=self.frameAvtHeight,
            bg="white", bd=0, highlightthickness=0
        )
        frame_avt.place(x=0, y=self.height//2 - self.frameAvtHeight//2 + 50)

        self.canvas_avt = tk.Canvas(
            frame_avt,
            width=self.width, height=self.frameAvtHeight,
            bg="white", bd=0, highlightthickness=0
        )
        self.canvas_avt.pack(fill="both", expand=True)
        self.canvas_avt.image_refs = []
        
        # Canvas chứa 3 button
        frame_btn = tk.Frame(
            self.canvas,
            width=self.width,
            height=self.frameBtnHeight + 2,
            bg="white", bd=0, highlightthickness=0
        )
        frame_btn.place(x=0, y=self.height//2 + 200)
        
        self.canvas_btn = tk.Canvas(
            frame_btn,
            width=self.width,
            height=self.frameBtnHeight + 2,
            bg="white", bd=0, highlightthickness=0
        )
        self.canvas_btn.pack(fill="both", expand=True)
        self.canvas_btn.image_refs = []
                
        # Vẽ 3 nhân vật Chikawa, Hachi, Usagi
        self.draw_Hachi_avt()
        self.draw_Chikawa_avt()
        self.draw_Usagi_avt()
        
        # # Vẽ 3 nút chọn avarta
        self.draw_Hachi_btn()
        self.draw_Chikawa_btn()
        self.draw_Usagi_btn()
        
    # Vẽ nền trắng và tiêu đề
    def draw_bgAndtitle(self):
        self.title_CHOOSE = ImageObj(self.canvas_CHOOSE)
        self.title_CHARACTER = ImageObj(self.canvas_CHARACTER)

        self.title_CHOOSE.create_image(
            self.width//2, self.title_height//2 + self.title_height*3,
            "Gallery/chooseAvt_title_CHOOSE.png",
            550, 90,
            "center"
        )
        self.title_CHARACTER.create_image(
            self.width//2, self.title_height//2 + self.title_height*3,
            "Gallery/chooseAvt_title_CHARACTER.png",
            600, 90,
            "center"
        )
        self.title_CHOOSE.effect.slide_up(self.width//2, self.title_height//2)
        self.canvas.after(200, lambda: self.title_CHARACTER.effect.slide_up(self.width//2, self.title_height//2))

    # Vẽ 3 nhân vận Chikawa, Hachi và Usagi
    def draw_Hachi_avt(self):
        self.hachiAvt = ImageObj(self.canvas_avt)
        self.hachiAvt.create_image(
            self.width//2 - 270, self.frameAvtHeight*2,
            "Gallery/Hachi_Avt.png",
            self.frameAvtWidth, self.frameAvtHeight,
            "center"
        )
        self.canvas.after(200, lambda: self.hachiAvt.effect.slide_up(self.width//2 - 270, self.frameAvtHeight//2))
        
    def draw_Chikawa_avt(self):
        self.chikawaAvt = ImageObj(self.canvas_avt)
        self.chikawaAvt.create_image(
            self.width//2, self.frameAvtHeight*2,
            "Gallery/Chikawa_Avt.png",
            self.frameAvtWidth, self.frameAvtHeight,
            "center"
        )
        self.canvas.after(350, lambda: self.chikawaAvt.effect.slide_up(self.width//2, self.frameAvtHeight//2))
        
    def draw_Usagi_avt(self):
        self.usagiAvt = ImageObj(self.canvas_avt)
        self.usagiAvt.create_image(
            self.width//2 + 270, self.frameAvtHeight*2,
            "Gallery/Usagi_Avt.png",
            self.frameAvtWidth, self.frameAvtHeight,
            "center"
        )
        self.canvas.after(200, lambda: self.usagiAvt.effect.slide_up(self.width//2 + 270, self.frameAvtHeight//2))
        
    #Vẽ 3 nút chọn avarta
    def draw_Hachi_btn(self):
        self.hachi_btn = ButtonObj(self.canvas_btn)
        self.hachi_btn.create_button(
            self.width//2 - 270, 140,  # button bên trái
            text="HACHI", text_color="#1a1a1a",
            font=self.font,
            command=lambda: self.choose("HACHI")
        )
        self.canvas.after(200, lambda: self.hachi_btn.btn_effect.slide_up(self.width//2 - 270, 70//2, hasShadow=True))
        self.canvas.after(250, lambda: self.hachi_btn.text_effect.slide_up(self.width//2 - 270, 70//2 - 10))

    def draw_Chikawa_btn(self):
        self.chikawa_btn = ButtonObj(self.canvas_btn)
        self.chikawa_btn.create_button(
            self.width//2, 140,  # button giữa
            text="CHIKAWA", text_color="#1a1a1a",
            font=self.font,
            command=lambda: self.choose("CHIKAWA")
        )
        self.canvas.after(400, lambda: self.chikawa_btn.btn_effect.slide_up(self.width//2, 70//2, hasShadow=True))
        self.canvas.after(450, lambda: self.chikawa_btn.text_effect.slide_up(self.width//2, 70//2 - 10))
        
    def draw_Usagi_btn(self):
        self.usagi_btn = ButtonObj(self.canvas_btn)
        self.usagi_btn.create_button(
            self.width//2 + 270, 140,  # button bên phải
            text="USAGI", text_color="#1a1a1a",
            font=self.font,
            command=lambda: self.choose("USAGI")
        )
        self.canvas.after(300, lambda: self.usagi_btn.btn_effect.slide_up(self.width//2 + 270, 70//2, hasShadow=True))
        self.canvas.after(350, lambda: self.usagi_btn.text_effect.slide_up(self.width//2 + 270, 70//2 - 10))

    # Trả về nhân vật đã chọn
    def choose(self, name_avt):
        self.avtChoosed = name_avt
        print(f"Bạn đã chọn {name_avt}")
        
        # Xử lý hậu cần
        self.usagiAvt.effect.slide_up(self.width//2 + 270, -150)
        self.canvas.after(100, lambda: self.hachiAvt.effect.slide_up(self.width//2 - 270, -150))
        self.canvas.after(200, lambda: self.chikawaAvt.effect.slide_up(self.width//2, -150))

        self.canvas.after(300, lambda: self.usagi_btn.btn_effect.slide_up(self.width//2 + 270, -150, hasShadow=True))
        self.canvas.after(300, lambda: self.usagi_btn.text_effect.slide_up(self.width//2 + 270, -150))
        self.canvas.after(400, lambda: self.chikawa_btn.btn_effect.slide_up(self.width//2, -150, hasShadow=True))
        
        self.canvas.after(400, lambda: self.chikawa_btn.text_effect.slide_up(self.width//2, -150))
        self.canvas.after(500, lambda: self.hachi_btn.btn_effect.slide_up(self.width//2 - 270, -150, hasShadow=True))
        self.canvas.after(500, lambda: self.hachi_btn.text_effect.slide_up(self.width//2 - 270, -150))
        
        self.canvas.after(360, lambda: self.title_CHOOSE.effect.slide_up(self.width//2, 170, delay=25))
        self.canvas.after(320, lambda: self.title_CHARACTER.effect.slide_up(self.width//2, 170, delay=25))
        
        self.canvas.after(700, self.run_mazePage)
        
    def run_mazePage(self):
        self.canvas.destroy()
        from mazePage import mazePage
        mazePage(self.root, self.avtChoosed, self.width, self.height)