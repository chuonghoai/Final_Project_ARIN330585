import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageFont, ImageTk, ImageFilter
import time

class effectObj:
    def __init__(self, canvas, item_id, pil_image=None):
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

class textObj:
    def __init__(self, canvas):
        self.canvas = canvas
        self.item_id = None
        
    def create_text(self, x, y, text="", font="Minecraft Ten", 
                    font_size=20, font_style="bold", text_color="white", anchor="center"):
        _font = (font, font_size, font_style)
        self.item_id = self.canvas.create_text(x, y, text=text, font=_font, fill=text_color, anchor=anchor)
        return self.item_id

class ImageObj:
    def __init__(self, canvas, delay=False):
        self.canvas = canvas
        self.item_id = None
        self.tk_img = None
        self.original = None  # giữ PIL image gốc
        self.delay = delay

    def create_image(self, x, y, path, w=None, h=None, anchor="center", hasEffect=True):
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
        
        if hasEffect:
            self.effect = effectObj(self.canvas, self.item_id, self.original)
        return self.item_id
    
    def create_gif(self, x, y, path, w=None, h=None, anchor="center", delay=100):
        gif = Image.open(path)
        frames = []
        try:
            while True:
                frame = gif.copy().convert("RGBA")
                if w and h:
                    frame = frame.resize((w, h), Image.LANCZOS)
                frames.append(ImageTk.PhotoImage(frame))
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass

        self.item_id = self.canvas.create_image(x, y, image=frames[0], anchor=anchor)
        self.canvas.image_refs.extend(frames)
        
        def animate(index=0):
            self.canvas.itemconfig(self.item_id, image=frames[index])
            self.canvas.after(delay, animate, (index + 1) % len(frames))

        animate()
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
           font="Minecraft Ten", font_size=30, font_style="bold",
           command=None,
           haveShadow=True,
           hasBorder=False):
        
        # size
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

        # Vẽ border nếu cần
        if hasBorder:
            border = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            border_draw = ImageDraw.Draw(border)
            border_draw.rounded_rectangle(
                (0, 0, w-1, h-1), radius=radius, outline="black", width=3
            )
            round_img = Image.alpha_composite(round_img, border)

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
        if font_style:
            _font = (font, font_size, font_style)
        else:
            _font = (font, font_size)
        self.text_id = self.canvas.create_text(x, y - h*1/7, text=text, font=_font, fill=text_color, anchor="center")

        # Shadow
        shadow_img = create_shadow(w, h, radius=radius)
        self.shadow_img = ImageTk.PhotoImage(shadow_img)
        self.canvas.image_refs.append(self.shadow_img)
        self.shadow_id = self.canvas.create_image(x+3, y+3, image=self.shadow_img, anchor="center")
        self.canvas.itemconfigure(self.shadow_id, state="hidden")

        # Hover effect
        if haveShadow:
            self.canvas.tag_bind(self.item_id, "<Enter>", lambda e: add_shadow(self.canvas, self.shadow_id, self.item_id, self.text_id)) 
            self.canvas.tag_bind(self.text_id, "<Enter>", lambda e: add_shadow(self.canvas, self.shadow_id, self.item_id, self.text_id)) 
            self.canvas.tag_bind(self.item_id, "<Leave>", lambda e: remove_shadow(self.canvas, self.shadow_id, self.text_id)) 
            self.canvas.tag_bind(self.text_id, "<Leave>", lambda e: remove_shadow(self.canvas, self.shadow_id, self.text_id))

        # Event binding
        if command:
            def action(e=None):
                press_effect()
                self.canvas.after(100, lambda: command()) 
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

class ComboBoxObj:
    def __init__(self, canvas):
        self.canvas = canvas
        self.main_btn = None
        self.main_text = None
        self.option_buttons = []
        self.is_open = False
        self.selected_value = None
        self.startBtn = None

    def createComboBox(self, x, y,  values, defultText="Choose Algorithm", font="Minecraft Ten", w=250, h=60, startBtn=(None, None)):
        self.startBtn = startBtn
        hasbd = True
        cl1 = "#fdf0d3"
        # Tạo button chính
        btnObj = ButtonObj(self.canvas)
        self.main_btn, self.main_text = btnObj.create_button(
            x, y, w=w, h=h, text=defultText,
            color1=cl1, color2=cl1,
            text_color="black", font=font, font_size=18, font_style="bold",
            hasBorder=hasbd
        )

        # Tạo các button option (ẩn ngay dưới button chính)
        offset = h + 2
        for i, val in enumerate(values):
            option = ButtonObj(self.canvas)
            opt_btn, opt_text = option.create_button(
                x, y, w=w-20, h=h-10, text=val,
                color1=cl1, color2=cl1,
                text_color="black", font=font, font_size=17, font_style="normal",
                command=lambda v=val: self._select_value(v),
                hasBorder=hasbd
            )
            # Ẩn option (đặt chồng dưới main button)
            self.canvas.itemconfigure(opt_btn, state="hidden")
            self.canvas.itemconfigure(opt_text, state="hidden")
            self.option_buttons.append((option, opt_btn, opt_text, y + (i+1)*offset))

        # Gán sự kiện cho main button
        self.canvas.tag_bind(self.main_btn, "<Button-1>", lambda e: self.toggle())
        self.canvas.tag_bind(self.main_text, "<Button-1>", lambda e: self.toggle())

    def toggle(self):
        if self.is_open:
            self.close()
        else:
            self.open()

    # Xả danh sách con
    def open(self):
        if self.is_open:
            return
        self.is_open = True
        if self.startBtn:
            self.canvas.itemconfigure(self.startBtn[0], state="hidden")
            self.canvas.itemconfigure(self.startBtn[1], state="hidden")

        for option, opt_btn, opt_text, target_y in self.option_buttons:
            self.canvas.itemconfigure(opt_btn, state="normal")
            self.canvas.itemconfigure(opt_text, state="normal")
            option.btn_effect.slide_up(self.canvas.coords(opt_btn)[0], target_y, easing=0.3, delay=15, hasShadow=True)
            option.text_effect.slide_up(self.canvas.coords(opt_btn)[0], target_y, easing=0.3, delay=15)

    # Đóng danh sách con
    def close(self):
        if not self.is_open:
            return
        self.is_open = False
        main_x, main_y = self.canvas.coords(self.main_btn)
        for option, opt_btn, opt_text, _ in self.option_buttons:
            option.btn_effect.slide_up(main_x, main_y, easing=0.3, delay=15, hasShadow=True)
            option.text_effect.slide_up(main_x, main_y, easing=0.3, delay=15)
            self.canvas.itemconfigure(opt_btn, state="hidden"),
            self.canvas.itemconfigure(opt_text, state="hidden")
        
        if self.startBtn:
            self.canvas.itemconfigure(self.startBtn[0], state="normal")
            self.canvas.itemconfigure(self.startBtn[1], state="normal")

    # Gắn text con vào text chính
    def _select_value(self, value):
        self.selected_value = value
        self.canvas.itemconfigure(self.main_text, text=value)
        self.close()
        
    # Lấy text chính trả về chương trình đang chạy
    def getValue(self):
        _text = self.canvas.itemcget(self.main_text, "text")
        if _text == "Choose Algorithm":
            return None
        else: 
            return _text
    
class mazeObj:
    def __init__(self, canvas, animating, _after_id):
        self.canvas = canvas
        self.pathWall = "Gallery/mazeImg/wall.png"
        self.pathFloor = "Gallery/mazeImg/floor.png"
        self.pathTreasure = "Gallery/mazeImg/cachua.png"
        self.pathEnd = "Gallery/mazeImg/door.png"

        self.blocks = []       # lưu các item id của mê cung
        self.avatar_id = None  # lưu item id của nhân vật
        self.end_id = None     # lưu item id lối thoát
        self.border_id = None  # lưu item id khung viền
        self.treasure_id = []  # lưu item id các kho báu
        
        self.start_pos = None  # (i, j) vị trí 'A'
        self.end_pos = None    # (i, j) vị trí 'B'
        self.treasure_pos = [] # [(i, j)] vị trí treasure
        self.center_pos = None # vị trí trung tâm của mê cung

        self.maze = None        # Lưu lại mê cung
        self.animating = animating  # Lưu lại trạng thái hoạt ảnh
        self._after_id = _after_id     # Lưu lại hàng đợi after
        self.is_reach_goal = False      # kiểm tra đã đến đích chưa

    def createMaze(self, x, y, maze, 
                   pathAvt=None, pathWall=None, pathFloor=None, pathTreasure=None, pathEnd=None,
                   sizeOfBlock=(40, 40),
                   bd_color="gray", bd_width=3):

        # Đặt giá trị mặc định cho các biến
        pathWall = pathWall or self.pathWall
        pathFloor = pathFloor or self.pathFloor
        pathTreasure = pathTreasure or self.pathTreasure
        pathEnd = pathEnd or self.pathEnd
        self.center_pos = (x, y)

        self.maze = maze
        rows, cols = len(maze), len(maze[0])
        w, h = sizeOfBlock

        # Tính toạ độ góc trên trái để mê cung có tâm tại (x, y)
        start_x = x - (cols * w) / 2
        start_y = y - (rows * h) / 2

        # Load ảnh và lưu lại để tránh bị GC
        self.wall_img = ImageTk.PhotoImage(Image.open(pathWall).resize(sizeOfBlock))
        self.floor_img = ImageTk.PhotoImage(Image.open(pathFloor).resize(sizeOfBlock))
        self.avt_img = ImageTk.PhotoImage(Image.open(pathAvt).resize(sizeOfBlock))
        self.treasure_img = ImageTk.PhotoImage(Image.open(pathTreasure).resize(sizeOfBlock))
        self.end_img = ImageTk.PhotoImage(Image.open(pathEnd).resize(sizeOfBlock))

        # Xóa block và border cũ nếu có
        for b in self.blocks:
            self.canvas.delete(b)
        self.blocks.clear()

        # Xóa vị trí kho báu cũ
        for t in self.treasure_id:
            self.canvas.delete(t)
        self.treasure_id.clear()
        self.treasure_pos.clear()

        # Xóa nhân vật, đích và khung
        if self.avatar_id:
            self.canvas.delete(self.avatar_id)
            self.avatar_id = None
        if self.end_id:
            self.canvas.delete(self.end_id)
            self.end_id = None
        if self.border_id:
            self.canvas.delete(self.border_id)
            self.border_id = None

        self.start_pos = None
        self.end_pos = None

        # --- Vẽ mê cung ---
        for i in range(rows):
            for j in range(cols):
                cx = start_x + j * w
                cy = start_y + i * h
                cell = maze[i][j]

                if cell == "*":  # Tường
                    img_id = self.canvas.create_image(cx, cy, anchor="nw", image=self.wall_img)
                else:  # Đường đi hoặc A, B
                    img_id = self.canvas.create_image(cx, cy, anchor="nw", image=self.floor_img)

                    if cell == "A":
                        self.start_pos = (i, j)
                    elif cell == "B":
                        self.end_pos = (i, j)
                    elif cell == "t":
                        self.treasure_pos.append((i, j))

                self.blocks.append(img_id)

        # --- Vẽ nhân vật tại vị trí A ---
        if self.start_pos:
            i, j = self.start_pos
            cx = start_x + j * w
            cy = start_y + i * h
            self.avatar_id = self.canvas.create_image(cx, cy, anchor="nw", image=self.avt_img)
        
        # --- Vẽ lối thoát tại vị trí B ---
        if self.end_pos:
            i, j = self.end_pos
            cx = start_x + j * w
            cy = start_y + i * h
            self.end_id = self.canvas.create_image(cx, cy, anchor="nw", image=self.end_img)
        
        # --- Vẽ kho báu tại vị trí t ---
        self.treasure_map = {}
        if self.treasure_pos:
            for i, j in self.treasure_pos:
                cx = start_x + j * w
                cy = start_y + i * h
                tid = self.canvas.create_image(cx, cy, anchor="nw", image=self.treasure_img)
                self.treasure_id.append(tid)
                self.treasure_map[(i, j)] = tid
            
        # --- Vẽ khung viền quanh mê cung ---
        x1, y1 = start_x, start_y
        x2, y2 = start_x + cols * w, start_y + rows * h
        self.border_id = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=bd_color,
            width=bd_width
        )

    # Vẽ quá trình tìm kiếm của thuật toán
    def draw_search_process(self, explored_cells, path_coords,
                            sizeOfBlock=(40, 40),
                            color="#28549A", alpha=100,
                            delay=16, cells_per_frame=5):
        """
        Hiển thị quá trình BFS mở rộng (60 FPS) bằng overlay RGBA (trong suốt thật),
        sau đó tự động vẽ đường đi.
        cells_per_frame: số ô vẽ trong mỗi frame (tăng giá trị → nhanh hơn).
        """
        self.animating = True
        self.is_reach_goal = False
        
        if not explored_cells or not self.maze:
            self.draw_path(path_coords, sizeOfBlock=sizeOfBlock)
            return

        rows, cols = len(self.maze), len(self.maze[0])
        w, h = sizeOfBlock

        # Gốc mê cung
        x, y = self.center_pos
        start_x = x - (cols * w) / 2
        start_y = y - (rows * h) / 2

        # Chuẩn bị ảnh overlay RGBA
        overlay = Image.new("RGBA", (int(cols * w), int(rows * h)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Màu + alpha
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        fill_color = (r, g, b, alpha)

        # Ảnh ban đầu
        self.search_img = ImageTk.PhotoImage(overlay)
        self.search_id = self.canvas.create_image(start_x, start_y, anchor="nw", image=self.search_img)
        self.canvas.image_refs = getattr(self.canvas, "image_refs", [])
        self.canvas.image_refs.append(self.search_img)

        # Hiệu ứng từng bước
        def draw_step(index=0):
            if not self.animating:
                return
            if index >= len(explored_cells):
                self.animating = False
                self.draw_path(path_coords, sizeOfBlock=sizeOfBlock)
                return

            # Vẽ nhiều ô mỗi frame
            for k in range(cells_per_frame):
                if index + k >= len(explored_cells):
                    break
                i, j = explored_cells[index + k]
                x1, y1 = j * w, i * h
                x2, y2 = x1 + w, y1 + h
                draw.rectangle([x1, y1, x2, y2], fill=fill_color)

            # Cập nhật ảnh
            self.search_img = ImageTk.PhotoImage(overlay)
            self.canvas.itemconfig(self.search_id, image=self.search_img)
            self.canvas.image_refs.append(self.search_img)

            # Đảm bảo thứ tự lớp
            if self.treasure_id:
                for t in self.treasure_id:
                    self.canvas.tag_raise(t)
            if self.end_id:
                self.canvas.tag_raise(self.end_id)
            if self.avatar_id:
                self.canvas.tag_raise(self.avatar_id)

            after_id = self.canvas.after(delay, draw_step, index + cells_per_frame)
            self._after_id.append(after_id)

        draw_step(0)

    # Vẽ đường đi của nhân vật
    def draw_path(self, path_coords, sizeOfBlock=(40, 40), color="#50E671", 
                  alpha=100, delay=16, command=None, cells_per_frame=10):
        """
        Vẽ đường đi từ từ theo thứ tự path_coords (hiệu ứng 60 FPS).
        path_coords: danh sách [(i, j)] tọa độ đường đi.
        sizeOfBlock: kích thước mỗi ô.
        color: màu đường đi (hex).
        alpha: độ trong suốt (0–255).
        delay: thời gian giữa mỗi frame (ms) — 16ms ≈ 60 FPS.
        """
        self.animating = True
        
        if not path_coords or not self.maze:
            return

        rows, cols = len(self.maze), len(self.maze[0])
        w, h = sizeOfBlock

        # Gốc mê cung
        x, y = self.center_pos
        start_x = x - (cols * w) / 2
        start_y = y - (rows * h) / 2

        # Chuẩn bị ảnh overlay rỗng (RGBA)
        overlay = Image.new("RGBA", (int(cols * w), int(rows * h)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Chuyển màu hex → RGB + alpha
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        fill_color = (r, g, b, alpha)

        # ảnh ban đầu
        self.path_img = ImageTk.PhotoImage(overlay)
        self.path_id = self.canvas.create_image(start_x, start_y, anchor="nw", image=self.path_img)
        self.canvas.image_refs = getattr(self.canvas, "image_refs", [])
        self.canvas.image_refs.append(self.path_img)

        if self.treasure_id:
            for t in self.treasure_id:
                self.canvas.tag_raise(t)
        if self.end_id:
            self.canvas.tag_raise(self.end_id)
        if self.avatar_id:
            self.canvas.tag_raise(self.avatar_id)

        # --- Hiệu ứng vẽ từng ô ---
        def draw_step(index=0):
            if index >= len(path_coords):
                self.animating = False
                # Khi vẽ xong toàn bộ, đảm bảo thứ tự hiển thị
                if self.avatar_id:
                    self.canvas.tag_raise(self.avatar_id)
                if self.end_id:
                    self.canvas.tag_raise(self.end_id)
                if self.treasure_id:
                    for t in self.treasure_id:
                        self.canvas.tag_raise(t)

                # Hàm thực thi khi vẽ xong path
                self.animate_avatar_along_path(path_coords)
                return

            # Vẽ ô tiếp theo
            for k in range(cells_per_frame):
                if index + k >= len(path_coords):
                    break
                i, j = path_coords[index]
                x1, y1 = j * w, i * h
                x2, y2 = x1 + w, y1 + h
                draw.rectangle([x1, y1, x2, y2], fill=fill_color)

            # Cập nhật lại ảnh trên canvas
            self.path_img = ImageTk.PhotoImage(overlay)
            self.canvas.itemconfig(self.path_id, image=self.path_img)
            self.canvas.image_refs.append(self.path_img)

            # Lên frame tiếp theo (60 FPS)
            after_id = self.canvas.after(delay, draw_step, index + 1)
            self._after_id.append(after_id)
        draw_step(0)

    # Cho nhân vật di chuyển
    def animate_avatar_along_path(self, path_coords, sizeOfBlock=(40, 40), speed=6, delay=16):
        """
        Di chuyển nhân vật mượt mà theo path_coords.
        speed: số pixel di chuyển mỗi frame
        delay: thời gian giữa mỗi frame (ms) ~16ms tương đương ~60fps
        """
        self.animating = True
        
        if not path_coords or not hasattr(self, 'avatar_id'):
            return

        w, h = sizeOfBlock
        rows, cols = len(self.maze), len(self.maze[0])
        cx, cy = self.center_pos

        start_x = cx - (cols * w) / 2
        start_y = cy - (rows * h) / 2

        # Vị trí ban đầu (giữa ô)
        cur_x = start_x + path_coords[0][1] * w + w / 2
        cur_y = start_y + path_coords[0][0] * h + h / 2
        self.canvas.coords(self.avatar_id, cur_x, cur_y)
        self.canvas.tag_raise(self.avatar_id)

        def move_between(p1, p2, on_done):
            (i1, j1), (i2, j2) = p1, p2
            x1, y1 = start_x + j1 * w, start_y + i1 * h
            x2, y2 = start_x + j2 * w, start_y + i2 * h

            dx, dy = x2 - x1, y2 - y1
            dist = (dx ** 2 + dy ** 2) ** 0.5
            steps = max(int(dist // speed), 1)
            ux, uy = dx / steps, dy / steps

            def step(k=0):
                if k >= steps:
                    # tới ô kế → xử lý kho báu
                    self.canvas.coords(self.avatar_id, x2, y2)
                    self.canvas.tag_raise(self.avatar_id)
                    if (i2, j2) in self.treasure_map:
                        tid = self.treasure_map.pop((i2, j2))
                        self.canvas.delete(tid)
                    if on_done:
                        on_done()
                    return

                nx = x1 + ux * k
                ny = y1 + uy * k
                self.canvas.coords(self.avatar_id, nx, ny)
                self.canvas.tag_raise(self.avatar_id)
                after_id = self.canvas.after(delay, step, k + 1)
                self._after_id.append(after_id)
            step(0)

        def move_next(index=0):
            if index >= len(path_coords) - 1:
                self.animating = False
                self.is_reach_goal = True
                return
            move_between(
                path_coords[index],
                path_coords[index + 1],
                lambda: move_next(index + 1)
            )
        move_next(0)
        
# function create shadơw            
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