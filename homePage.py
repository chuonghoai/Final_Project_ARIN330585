import tkinter as tk
from PIL import Image, ImageTk
from uiComponents import ButtonObj, ImageObj
import uiComponents

class homePage:
    def __init__(self, root, width=1100, height=700):
        self.root = root
        self.width = width
        self.height = height
        root.title("Maze game")

        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height - 100) // 2

        root.geometry(f"{width}x{height}+{x}+{y}")
        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=width, height=height, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.image_refs = []

        # Vẽ nền background
        self.draw_background()

        # Vẽ nút Play
        self.draw_playBtn()

        #Vẽ title
        self.draw_title()

    # Vẽ nền background
    def draw_background(self):
        self.homePage_bg = ImageObj(self.canvas)
        self.homePage_bg.create_image(
            self.width//2, self.height//2,
            "Gallery/Home.png",
            w=self.width, h=self.height
        )

    # Vẽ nút Play
    def draw_playBtn(self):
        self.playBtn = ButtonObj(self.canvas, True)
        self.playTxt = ImageObj(self.canvas, True)

        self.playBtn.create_button(
            self.width//2, self.height//2 + 290,
            text="", 
            color1="cyan", color2="violet",
            text_color="white",
            font="Minecraft Ten", font_size=20,
            command=lambda: self.click_playBtn()
        )
        self.variable_playTxt = self.playTxt.create_image(
            self.width//2, self.height//2 + 290,
            "Gallery/PLAY_txt.png",
            110, 40,
            "center"
        )
        
        self.canvas.tag_bind(self.variable_playTxt, "<Button-1>", lambda e: self.click_playBtn())
        
        def hoverEnter_playtxt(e=None):
            uiComponents.add_shadow(self.playBtn.canvas, self.playBtn.shadow_id, self.playBtn.item_id, self.playBtn.text_id)
            x, y = self.canvas.coords(self.variable_playTxt)
            self.canvas.coords(self.variable_playTxt, x, y - 2)
            
        def hoverLeave_playtxt(e=None):
            uiComponents.remove_shadow(self.playBtn.canvas, self.playBtn.shadow_id, self.playBtn.text_id)
            x, y = self.canvas.coords(self.variable_playTxt)
            self.canvas.coords(self.variable_playTxt, x, y + 2)
            
        for tag in (self.playBtn.item_id, self.playBtn.text_id, self.variable_playTxt):
            self.canvas.tag_bind(tag, "<Enter>", hoverEnter_playtxt)
            self.canvas.tag_bind(tag, "<Leave>", hoverLeave_playtxt)
        
        self.canvas.after(200, lambda: self.playBtn.btn_effect.fade_in())
        self.canvas.after(200, lambda: self.playTxt.effect.fade_in())

    # Vẽ title
    def draw_title(self):
        self.title_label = ImageObj(self.canvas, True)
        self.title_label.create_image(
            self.width//2, 150,
            "./Gallery/title.png",
            400, 250,
            "center"
        )
        self.canvas.after(200, lambda: self.title_label.effect.fade_in())

    def click_playBtn(self):
        # Tạo hiệu ứng nhấn nút
        x, y = self.canvas.coords(self.variable_playTxt)
        self.canvas.coords(self.variable_playTxt, x, y + 2)
        self.root.after(100, lambda: self.canvas.coords(self.variable_playTxt, x, y))

        # Kết thúc hiệu ứng home page
        self.title_label.effect.cancel_after()
        self.playBtn.btn_effect.cancel_after()
        self.playTxt.effect.cancel_after()
        
        self.title_label.effect.show_immediately()
        self.playBtn.btn_effect.show_immediately()
        self.playTxt.effect.show_immediately()
        
        self.title_label.effect.fade_out(True)
        self.playBtn.btn_effect.fade_out(True)
        self.playTxt.effect.fade_out(True)
        self.homePage_bg.effect.fade_out(True)
        
        self.root.after(700, self.run_chooseAvt)
            
    # Vẽ màn hình choose avt
    def run_chooseAvt(self):
        self.canvas.destroy()
        from chooseAvt import chooseAvt
        chooseAvt(self.root, self.width, self.height)

def runApp():
    root = tk.Tk()
    app = homePage(root)
    root.mainloop()