import tkinter as tk
from datetime import datetime
import platform

class TransparentClock:
    def __init__(self):
        # hidden main window for taskbar
        self.root = tk.Tk()
        self.root.withdraw()

        # clock window
        self.clock_window = tk.Toplevel(self.root)
        self.clock_window.overrideredirect(True)  # remove title bar
        self.clock_window.attributes('-topmost', True)

        # background color & transparency
        self.bg_color = '#000001'
        system = platform.system()
        if system == 'Darwin':  # macOS
            self.clock_window.attributes('-transparent', True)
            self.bg_color = 'systemTransparent'
        elif system == 'Windows':
            self.clock_window.attributes('-transparentcolor', self.bg_color)
            self.clock_window.attributes('-alpha', 0.7)

        self.clock_window.config(bg=self.bg_color)

        # position top-right
        screen_width = self.clock_window.winfo_screenwidth()
        window_width = 160  # wider to fit seconds
        window_height = 60
        x_pos = screen_width - window_width - 20
        y_pos = 20
        self.clock_window.geometry(f'{window_width}x{window_height}+{x_pos}+{y_pos}')

        # time label
        self.time_label = tk.Label(
            self.clock_window,
            font=('Helvetica Neue', 26, 'bold'),
            bg=self.bg_color,
            fg='#FFFFFF',
            padx=10,
            pady=5
        )
        self.time_label.pack()

        # draggable
        self.time_label.bind('<Button-1>', self.start_move)
        self.time_label.bind('<B1-Motion>', self.on_move)

        # right-click to close
        self.clock_window.bind('<Button-3>', self.close_app)

        # start updating
        self.update_time()

    # close app
    def close_app(self, event):
        self.clock_window.destroy()
        self.root.destroy()

    # drag logic
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        x = self.clock_window.winfo_x() + event.x - self.x
        y = self.clock_window.winfo_y() + event.y - self.y
        self.clock_window.geometry(f'+{x}+{y}')

    # update time with proper leading zeros
    def update_time(self):
        now = datetime.now()
        # use strftime with %H:%M:%S for proper zero padding
        time_string = now.strftime('%H:%M:%S')
        self.time_label.config(text=time_string)
        self.root.after(1000, self.update_time)

    # run app
    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    clock = TransparentClock()
    clock.run()
