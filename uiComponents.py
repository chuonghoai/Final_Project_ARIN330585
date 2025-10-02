from PIL import Image, ImageDraw, ImageFont, ImageTk, ImageFilter

class effectObj:
    def __init__(self, canvas, item_id, pil_image):
        self.canvas = canvas
        if not isinstance(item_id, list):
            item_id = [item_id]
        self.item_id = item_id

        self.original = pil_image.convert("RGBA")  # giữ ảnh gốc
        self.tk_img = None
        self._after_id = None  # lưu id của after để cancel
        self._running = False

        # cho slide_up
        self.target_x = None
        self.target_y = None
        self.easing = 0.2
        self.delay = 20

    # Fade in
    def fade_in(self, func_on_complete=None, steps=20, delay=20):
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
                self.canvas.itemconfig(self.item_id[0], image=self.tk_img)
                self.canvas.image_refs.append(self.tk_img)

                self.canvas.after(delay, step, i + 1)
            else:
                # khi xong thì gán ảnh gốc rõ ràng nhất
                self.tk_img = ImageTk.PhotoImage(self.original)
                self.canvas.itemconfig(self.item_id[0], image=self.tk_img)
                self.canvas.image_refs.append(self.tk_img)

                if func_on_complete:
                    func_on_complete()
        step()

    # Fade out
    def fade_out(self, delete_after=False, func_on_complete=None, steps=17, delay=17):
        def step(i=0):
            if i <= steps:
                img = self.original.copy()
                alpha = img.split()[3]  # lấy kênh alpha gốc
                alpha = alpha.point(lambda p: p * (1 - i / steps))  # giảm dần alpha
                img.putalpha(alpha)

                self.tk_img = ImageTk.PhotoImage(img)
                self.canvas.itemconfig(self.item_id[0], image=self.tk_img)
                self.canvas.image_refs.append(self.tk_img)

                self.canvas.after(delay, step, i + 1)
            else:
                if delete_after:
                    self.canvas.delete(self.item_id[0])
                else:
                    # khi xong thì gán ảnh trong suốt hoàn toàn
                    img = self.original.copy()
                    img.putalpha(0)
                    self.tk_img = ImageTk.PhotoImage(img)
                    self.canvas.itemconfig(self.item_id[0], image=self.tk_img)
                    self.canvas.image_refs.append(self.tk_img)

                if func_on_complete:
                    func_on_complete()
        step()

    def cancel_after(self):
        self._running = False
        if self._after_id:
            self.canvas.after_cancel(self._after_id)
            self._after_id = None

    def show_immediately(self):
        self.tk_img = ImageTk.PhotoImage(self.original)
        self.canvas.itemconfig(self.item_id[0], image=self.tk_img)

    # Slide up effect
    def slide_up(self, target_x, target_y, easing=0.2, delay=30, hasShadow=False):
        """Bắt đầu hiệu ứng slide up"""
        self.target_x = target_x
        self.target_y = target_y
        self.easing = easing
        self.delay = delay
        self._running = True
        self.hasShadow = hasShadow

        if self._after_id:
            self.canvas.after_cancel(self._after_id)

        self._animate_slide()

    def _animate_slide(self):
        if not self._running:
            return

        # lấy item chính (không bóng)
        item0 = self.item_id[0]
        coords = self.canvas.coords(item0)
        if not coords:
            return

        x, y = coords[0], coords[1]

        # còn khoảng cách đủ lớn thì tiếp tục di chuyển
        if abs(y - self.target_y) > 1:
            step = (self.target_y - y) * self.easing  # tính step theo hướng
            if self.hasShadow:
                for item in self.item_id:
                    self.canvas.move(item, 0, step)
            else:
                self.canvas.move(item0, 0, step)
            self._after_id = self.canvas.after(self.delay, self._animate_slide)
        else:
            # căn chỉnh chính xác vị trí cuối
            dx = self.target_x - x
            dy = self.target_y - y
            if self.hasShadow:
                for item in self.item_id:
                    self.canvas.move(item, dx, dy)
            else:
                self.canvas.move(item0, dx, dy)
            self._running = False
            self._after_id = None


    def stop(self):
        """Dừng hiệu ứng"""
        if self._after_id:
            self.canvas.after_cancel(self._after_id)
            self._after_id = None
        self._running = False


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
        
        self.effect = effectObj(self.canvas, self.item_id, self.original)
        return self.item_id

class ButtonObj:
    def __init__(self, canvas, delay=False):
        self.canvas = canvas
        self.width = None
        self.height = None
        self.item_id = None
        self.text_id = None
        self.tk_img = None
        self.shadow_id = None
        self.shadow_img = None
        self.original_btn = None
        self.delay = delay
        
    def create_button(self, x, y, w=250, h=70, text="Button",
               color1="#7bdfff", color2="#b46bff",
               text_color="white", 
               font="Minecraft Ten", font_size=30,
               command=None):
        self.width = w
        self.height = h
        
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

        self.original_btn = round_img

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
        self.text_id = self.canvas.create_text(x, y - 10, text=text, font=(font, font_size), fill=text_color)

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
            def action(e=None):
                command()
                press_effect()
            self.canvas.tag_bind(self.item_id, "<Button-1>", lambda e: action())
            self.canvas.tag_bind(self.text_id, "<Button-1>", lambda e: action())
            self.canvas.tag_bind(self.item_id, "<Button-1>", lambda e: action())
            self.canvas.tag_bind(self.text_id, "<Button-1>", lambda e: action())
        
        # Hiệu ứng nhấn button
        def press_effect():
            x, y = self.canvas.coords(self.text_id)
            self.canvas.coords(self.text_id, x, y + 2)
            self.canvas.after(100, lambda: self.canvas.coords(self.text_id, x, y))
        
        # fade controller
        self.btn_effect = effectObj(self.canvas, [self.item_id, self.shadow_id], self.original_btn)
        self.text_effect = effectObj(self.canvas, self.text_id, self.original_btn)
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
