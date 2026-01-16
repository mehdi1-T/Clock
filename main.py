import tkinter as tk
from datetime import datetime
import platform

class transparent_clock:
    def __init__(self):
        # Create main hidden window for taskbar
        self.root = tk.Tk()
        self.root.title("Transparent Clock")
        self.root.withdraw()  # Hide the main window
        
        # Create the actual clock window
        self.clock_window = tk.Toplevel(self.root)
        self.clock_window.overrideredirect(True)
        self.clock_window.attributes('-topmost', True)
        self.clock_window.attributes('-alpha', 0.85)
        
        if platform.system() == 'Windows':
            self.clock_window.attributes('-transparentcolor', 'black')
        
        # Position in top-right corner
        screen_width = self.clock_window.winfo_screenwidth()
        window_width = 200
        window_height = 60
        x_position = screen_width - window_width - 20
        y_position = 20
        
        self.clock_window.geometry(f'{window_width}x{window_height}+{x_position}+{y_position}')
        self.clock_window.configure(bg='black')
        
        # Time label
        self.time_label = tk.Label(
            self.clock_window,
            font=('SF Pro Display', 28, 'bold'),
            bg='black',
            fg='white',
            padx=15,
            pady=10
        )
        self.time_label.pack(expand=True)
        
        # Date label
        self.date_label = tk.Label(
            self.clock_window,
            font=('SF Pro Display', 10, 'bold'),
            bg='black',
            fg='#999999',
            padx=15,
            pady=0
        )
        self.date_label.pack()
        
        # Make draggable
        self.time_label.bind('<Button-1>', self.start_move)
        self.time_label.bind('<B1-Motion>', self.on_move)
        self.date_label.bind('<Button-1>', self.start_move)
        self.date_label.bind('<B1-Motion>', self.on_move)
        
        # Right-click to close
        self.clock_window.bind('<Button-3>', self.close_app)
        
        self.update_time()
        
    def close_app(self, event):
        self.clock_window.destroy()
        self.root.destroy()
        
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
        
    def on_move(self, event):
        x = self.clock_window.winfo_x() + event.x - self.x
        y = self.clock_window.winfo_y() + event.y - self.y
        self.clock_window.geometry(f'+{x}+{y}')
        
    def update_time(self):
        now = datetime.now()
        time_string = now.strftime('%H:%M:%S')
        date_string = now.strftime('%a %d %b')
        
        self.time_label.config(text=time_string)
        self.date_label.config(text=date_string)
        
        self.root.after(1000, self.update_time)
        
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    clock = transparent_clock()
    clock.run()