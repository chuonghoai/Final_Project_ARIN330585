import tkinter as tk
from tkinter import ttk

class ComboBoxObj:
    def __init__(self, canvas):
        """
        canvas: cái Canvas bạn dùng (combo sẽ được gắn bằng canvas.create_window)
        """
        self.canvas = canvas
        self.widget = None
        self.win_id = None
        self._after_id = None
        self._running = False
        self.style = ttk.Style()

        # Tuỳ chọn: thử đổi sang theme 'clam' (thường hỗ trợ style tốt hơn).
        # Nếu không muốn đổi theme toàn cục, comment dòng dưới.
        try:
            self.style.theme_use('clam')
        except Exception:
            pass

    def createComboBox(self, x, y, values, width=15, default_index=0, center_text=True):
        """
        Tạo combobox (gắn lên canvas tại (x,y)).
        Trả về widget ttk.Combobox để bạn có thể .get(), .set(), .bind(),...
        """
        # Tạo combobox (parent = canvas.master, tức root hoặc frame chứa canvas)
        self.widget = ttk.Combobox(self.canvas.master, values=values, state="readonly", width=width)

        # set mặc định
        if 0 <= default_index < len(values):
            self.widget.current(default_index)

        # --- NHIỀU CÁCH THỬ để căn giữa text ---
        if center_text:
            # 1) Cách đơn giản (thường hoạt động)
            try:
                self.widget.configure(justify='center')
            except tk.TclError:
                pass

            # 2) Một số theme/readonly bỏ qua justify — tạm đổi state để ép apply rồi đổi lại
            try:
                cur_state = self.widget.cget('state')
                # tạm chuyển về normal, set justify, rồi trả lại state cũ
                self.widget.configure(state='normal')
                self.widget.configure(justify='center')
                self.widget.configure(state=cur_state)
            except tk.TclError:
                pass

            # 3) Áp style riêng (nếu theme chấp nhận)
            try:
                self.style.configure('Center.TCombobox', justify='center')
                self.widget.configure(style='Center.TCombobox')
            except Exception:
                pass

            # 4) Đảm bảo mỗi khi chọn lại item, text vẫn giữ center (re-apply)
            self.widget.bind('<<ComboboxSelected>>', lambda e: self._ensure_center())

        # Gắn combobox vào canvas
        self.win_id = self.canvas.create_window(x, y, window=self.widget, anchor='center')

        # Re-apply lần cuối sau 50ms (đôi khi cấu trúc widget hoàn tất sau khi vẽ)
        self.canvas.after(50, lambda: self._ensure_center())

        return self.widget

    def _ensure_center(self):
        """Thực hiện lại một lần nữa các thao táng để cố định justify = center."""
        if not self.widget:
            return
        try:
            self.widget.configure(justify='center')
        except tk.TclError:
            pass
        # nếu muốn, có thể tạm chuyển state như trên để ép hiệu lực
        try:
            s = self.widget.cget('state')
            self.widget.configure(state='normal')
            self.widget.configure(justify='center')
            self.widget.configure(state=s)
        except tk.TclError:
            pass

    def place_at(self, x, y):
        """Di chuyển vị trí combobox (nếu cần)."""
        if self.win_id:
            self.canvas.coords(self.win_id, x, y)

    def remove(self):
        """Xoá combobox khỏi canvas."""
        if self.win_id:
            self.canvas.delete(self.win_id)
            self.win_id = None
        if self.widget:
            try:
                self.widget.destroy()
            except Exception:
                pass
            self.widget = None
