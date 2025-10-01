from PIL import Image, ImageDraw, ImageFont, ImageTk, ImageFilter

class FadeObj:
    def __init__(self, canvas, item_id, pil_image):
        self.canvas = canvas
        self.item_id = item_id
        self.original = pil_image.convert("RGBA")  # giữ ảnh gốc
        self.tk_img = None
        self._after_id = None  # lưu id của after để cancel
        self._running = False
        
    def fade_in(self, func_on_complete=None, steps=25, delay=40):
        self._running = True
        def step(i=0):
            if not self._running:
                return
            if i <= steps:
                img = self.original.copy()
                alpha = img.split()[3]  # lấy kênh alpha gốc
                alpha = alpha.point(lambda p: p * i / steps)
                img.putalpha(alpha)

                self.tk_img = ImageTk.PhotoImage(img)
                self.canvas.itemconfig(self.item_id, image=self.tk_img)
                self.canvas.image_refs.append(self.tk_img)

                self.canvas.after(delay, step, i + 1)
            else:
                # khi xong thì gán ảnh gốc rõ ràng nhất
                self.tk_img = ImageTk.PhotoImage(self.original)
                self.canvas.itemconfig(self.item_id, image=self.tk_img)
                self.canvas.image_refs.append(self.tk_img)

                if func_on_complete:
                    func_on_complete()
        step()

    def fade_out(self, delete_after=False, func_on_complete=None,steps=20, delay=20):
        def step(i=0):
            if i <= steps:
                img = self.original.copy()
                alpha = img.split()[3]  # lấy kênh alpha gốc
                alpha = alpha.point(lambda p: p * (1 - i / steps))  # giảm dần alpha
                img.putalpha(alpha)

                self.tk_img = ImageTk.PhotoImage(img)
                self.canvas.itemconfig(self.item_id, image=self.tk_img)
                self.canvas.image_refs.append(self.tk_img)

                self.canvas.after(delay, step, i + 1)
            else:
                if delete_after:
                    self.canvas.delete(self.item_id)
                else:
                    # khi xong thì gán ảnh trong suốt hoàn toàn
                    img = self.original.copy()
                    img.putalpha(0)
                    self.tk_img = ImageTk.PhotoImage(img)
                    self.canvas.itemconfig(self.item_id, image=self.tk_img)
                    self.canvas.image_refs.append(self.tk_img)

                if func_on_complete:
                    func_on_complete()
        step()

    def cancel(self):
        self._running = False
        if self._after_id:
            self.canvas.after_cancel(self._after_id)
            self._after_id = None
    
    def show_immediately(self):
        self.tk_img = ImageTk.PhotoImage(self.original)
        self.canvas.itemconfig(self.item_id, image=self.tk_img)

class ImageObj:
    def __init__(self, canvas, delay=False):
        self.canvas = canvas
        self.item_id = None
        self.tk_img = None
        self.original = None  # giữ PIL image gốc
        self.delay = delay

    def create_image(self, x, y, path, w=None, h=None, anchor="center"):
        img = Image.open(path).convert("RGBA")
        if w and h:
            img = img.resize((w, h), Image.LANCZOS)
        self.original = img

        if self.delay:
            _ = img.copy()
            _.putalpha(0)
        else:
            _ = img.copy()
            
        self.tk_img = ImageTk.PhotoImage(_)
        self.canvas.image_refs.append(self.tk_img)
        self.item_id = self.canvas.create_image(x, y, image=self.tk_img, anchor=anchor)
        
        self.fade = FadeObj(self.canvas, self.item_id, self.original)
        return self.item_id

class ButtonObj:
    def __init__(self, canvas, delay=False):
        self.canvas = canvas
        self.item_id = None
        self.text_id = None
        self.tk_img = None
        self.shadow_id = None
        self.shadow_img = None
        self.original = None  # giữ PIL image gốc
        self.delay = delay
        
    def create_button(self, x, y, w=250, h=70, text="Button",
               color1="#7bdfff", color2="#b46bff",
               text_color="white", font=None,
               command=None):
        # Gradient
        cl1 = Image.new("RGB", (w, h), color1)
        cl2 = Image.new("RGB", (w, h), color2)
        format_bg = Image.linear_gradient("L").resize((w, h))
        gradient = Image.composite(cl2, cl1, format_bg)

        # Rounded background
        radius = h // 2
        round_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        mask = Image.new("L", (w, h), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
        round_img.paste(gradient, (0, 0), mask=mask)

        self.original = round_img

        if self.delay:
            _ = round_img.copy()
            _.putalpha(0)
        else:
            _ = round_img

        # Add background
        self.tk_img = ImageTk.PhotoImage(_)
        self.canvas.image_refs.append(self.tk_img)
        self.item_id = self.canvas.create_image(x, y, image=self.tk_img, anchor="center")

        # Add text
        self.text_id = self.canvas.create_text(x, y, text=text, font=font, fill=text_color)

        # Shadow
        shadow_img = create_shadow(w, h, radius=radius)
        self.shadow_img = ImageTk.PhotoImage(shadow_img)
        self.canvas.image_refs.append(self.shadow_img)
        self.shadow_id = self.canvas.create_image(x+3, y+3, image=self.shadow_img, anchor="center")
        self.canvas.itemconfigure(self.shadow_id, state="hidden")

        # Hover effect
        self.canvas.tag_bind(self.item_id, "<Enter>", lambda e: add_shadow(self.canvas, self.shadow_id, self.item_id, self.text_id)) 
        self.canvas.tag_bind(self.text_id, "<Enter>", lambda e: add_shadow(self.canvas, self.shadow_id, self.item_id, self.text_id)) 
        self.canvas.tag_bind(self.item_id, "<Leave>", lambda e: remove_shadow(self.canvas, self.shadow_id, self.text_id)) 
        self.canvas.tag_bind(self.text_id, "<Leave>", lambda e: remove_shadow(self.canvas, self.shadow_id, self.text_id))

        # Event binding
        if command:
            self.canvas.tag_bind(self.item_id, "<Button-1>", lambda e: command())
            self.canvas.tag_bind(self.text_id, "<Button-1>", lambda e: command())
            
        # fade controller
        self.fade = FadeObj(self.canvas, self.item_id, self.original)
        return self.item_id, self.text_id

def create_shadow(w, h, color="gray", radius=35):

    pad = 20
    big_w, big_h = w + pad * 2, h + pad * 2

    mask = Image.new("L", (big_w, big_h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((pad, pad, pad + w, pad + h), radius=radius, fill=255)

    shadow = Image.new("RGBA", (big_w, big_h), color)
    shadow.putalpha(mask)
    shadow = shadow.filter(ImageFilter.GaussianBlur(5))
    return shadow
    
def add_shadow(canvas, shadow_id, item_id, text_id=None):
    canvas.itemconfigure(shadow_id, state="normal")
    canvas.tag_lower(shadow_id, item_id)
    x, y = canvas.coords(text_id)
    canvas.coords(text_id, x, y - 2)

def remove_shadow(canvas, shadow_id, text_id=None):
    canvas.itemconfigure(shadow_id, state="hidden")
    x, y = canvas.coords(text_id)
    canvas.coords(text_id, x, y + 2)
