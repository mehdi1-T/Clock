import tkinter as tk
from tkinter import colorchooser
from datetime import datetime
import platform
from PIL import Image, ImageDraw, ImageTk
import pystray
from pystray import MenuItem as item
import threading
import json
import os

class SimpleContextMenu(tk.Menu):
    """Simple working context menu"""
    def __init__(self, parent):
        super().__init__(parent, tearoff=0, 
                        bg='#ffffff',
                        fg='#000000',
                        activebackground='#0078d7',
                        activeforeground='#ffffff',
                        font=('Segoe UI', 10),
                        relief=tk.FLAT,
                        borderwidth=1)


class TransparentClock:
    def __init__(self):
        # Hidden main window
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Configuration file path
        self.config_file = os.path.join(os.path.expanduser('~'), '.transparent_clock_config.json')
        self.load_config()
        
        # Clock window
        self.clock_window = tk.Toplevel(self.root)
        self.clock_window.overrideredirect(True)
        self.clock_window.attributes('-topmost', True)
        
        # Platform-specific transparency
        self.bg_color = '#000001'
        system = platform.system()
        
        if system == 'Darwin':
            self.clock_window.attributes('-transparent', True)
            self.bg_color = 'systemTransparent'
        elif system == 'Windows':
            self.clock_window.attributes('-transparentcolor', self.bg_color)
            self.clock_window.attributes('-alpha', 0.95)
        
        self.clock_window.config(bg=self.bg_color)
        
        # Position window
        self.window_width = max(160, int(self.font_size * 6.5))
        self.window_height = max(60, int(self.font_size * 2.8))
        self.clock_window.geometry(
            f'{self.window_width}x{self.window_height}+{self.x_position}+{self.y_position}'
        )
        
        # Time label
        self.time_label = tk.Label(
            self.clock_window,
            font=('SF Pro Display', self.font_size, 'bold') if system == 'Darwin' else ('Segoe UI', self.font_size, 'bold'),
            bg=self.bg_color,
            fg=self.text_color,
            padx=10,
            pady=5
        )
        self.time_label.pack()
        
        # Draggable
        self.time_label.bind('<Button-1>', self.start_move)
        self.time_label.bind('<B1-Motion>', self.on_move)
        self.time_label.bind('<ButtonRelease-1>', self.end_move)
        
        # Context menu
        self.clock_window.bind('<Button-3>', self.show_context_menu)
        self.time_label.bind('<Button-3>', self.show_context_menu)
        
        # Popup window reference
        self.popup_window = None
        
        # Start updating
        self.update_time()
        
        # Create system tray icon
        self.create_tray_icon()
    
    def load_config(self):
        """Load saved configuration or use defaults"""
        default_config = {
            'font_size': 26,
            'text_color': '#000000',
            'time_format': '24h',
            'show_seconds': True,
            'show_date': False,
            'x_position': None,
            'y_position': 20,
            'opacity': 0.95
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    default_config.update(config)
        except Exception as e:
            print(f"Error loading config: {e}")
        
        self.font_size = default_config['font_size']
        self.text_color = default_config['text_color']
        self.time_format = default_config['time_format']
        self.show_seconds = default_config['show_seconds']
        self.show_date = default_config['show_date']
        self.opacity = default_config['opacity']
        
        # Calculate x_position if not saved
        if default_config['x_position'] is None:
            screen_width = self.root.winfo_screenwidth()
            self.x_position = screen_width - 180
        else:
            self.x_position = default_config['x_position']
        
        self.y_position = default_config['y_position']
    
    def save_config(self):
        """Save current configuration"""
        config = {
            'font_size': self.font_size,
            'text_color': self.text_color,
            'time_format': self.time_format,
            'show_seconds': self.show_seconds,
            'show_date': self.show_date,
            'x_position': self.clock_window.winfo_x(),
            'y_position': self.clock_window.winfo_y(),
            'opacity': self.opacity
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def show_context_menu(self, event):
        """Show context menu with all options"""
        menu = SimpleContextMenu(self.root)
        
        menu.add_command(label="Customize Appearance", command=self.show_appearance_popup)
        menu.add_separator()
        menu.add_command(label="Exit", command=self.close_app)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def toggle_always_on_top(self):
        """Toggle always on top attribute"""
        current = self.clock_window.attributes('-topmost')
        self.clock_window.attributes('-topmost', not current)
    
    def show_format_popup(self):
        """Show time format selection popup"""
        if self.popup_window is not None:
            try:
                if self.popup_window.winfo_exists():
                    self.popup_window.destroy()
                    return
            except:
                pass
        
        self.popup_window = tk.Toplevel(self.root)
        self.popup_window.overrideredirect(True)
        self.popup_window.attributes('-topmost', True)
        
        bg_color = '#f7f7f7'
        border_color = '#c7c7cc'
        
        # Position
        screen_width = self.popup_window.winfo_screenwidth()
        screen_height = self.popup_window.winfo_screenheight()
        popup_width = 320
        popup_height = 260
        x_pos = screen_width - popup_width - 20
        y_pos = screen_height - popup_height - 60
        
        self.popup_window.geometry(f'{popup_width}x{popup_height}+{x_pos}+{y_pos}')
        
        # Shadow and container
        shadow_frame = tk.Frame(self.popup_window, bg='#d0d0d0')
        shadow_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        main_container = tk.Frame(
            self.popup_window,
            bg=bg_color,
            highlightthickness=1,
            highlightbackground=border_color
        )
        main_container.place(x=0, y=0, relwidth=1, relheight=1)
        
        content = tk.Frame(main_container, bg=bg_color)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(
            content,
            text="Time Format",
            font=('SF Pro Display', 15, 'bold') if platform.system() == 'Darwin' else ('Segoe UI', 12, 'bold'),
            bg=bg_color,
            fg='#1d1d1f'
        )
        title.pack(anchor='w', pady=(0, 20))
        
        # 12/24 hour toggle
        format_var = tk.StringVar(value=self.time_format)
        
        for fmt, label in [('12h', '12-Hour Format (3:45 PM)'), ('24h', '24-Hour Format (15:45)')]:
            rb_frame = tk.Frame(content, bg=bg_color)
            rb_frame.pack(fill=tk.X, pady=5)
            
            rb = tk.Radiobutton(
                rb_frame,
                text=label,
                variable=format_var,
                value=fmt,
                font=('SF Pro Text', 12) if platform.system() == 'Darwin' else ('Segoe UI', 10),
                bg=bg_color,
                fg='#1d1d1f',
                selectcolor=bg_color,
                activebackground=bg_color,
                command=lambda f=fmt: self.set_time_format(f)
            )
            rb.pack(anchor='w')
        
        # Show seconds toggle
        seconds_var = tk.BooleanVar(value=self.show_seconds)
        
        tk.Frame(content, bg='#d1d1d6', height=1).pack(fill=tk.X, pady=15)
        
        cb_frame = tk.Frame(content, bg=bg_color)
        cb_frame.pack(fill=tk.X, pady=5)
        
        cb_seconds = tk.Checkbutton(
            cb_frame,
            text="Show Seconds",
            variable=seconds_var,
            font=('SF Pro Text', 12) if platform.system() == 'Darwin' else ('Segoe UI', 10),
            bg=bg_color,
            fg='#1d1d1f',
            selectcolor=bg_color,
            activebackground=bg_color,
            command=lambda: self.toggle_seconds(seconds_var.get())
        )
        cb_seconds.pack(anchor='w')
        
        # Show date toggle
        date_var = tk.BooleanVar(value=self.show_date)
        
        cb_date = tk.Checkbutton(
            cb_frame,
            text="Show Date",
            variable=date_var,
            font=('SF Pro Text', 12) if platform.system() == 'Darwin' else ('Segoe UI', 10),
            bg=bg_color,
            fg='#1d1d1f',
            selectcolor=bg_color,
            activebackground=bg_color,
            command=lambda: self.toggle_date(date_var.get())
        )
        cb_date.pack(anchor='w', pady=(5, 0))
        
        # Done button
        self.create_done_button(content)
        
        self.popup_window.bind('<FocusOut>', lambda e: self.close_popup())
        self.popup_window.after(10, lambda: self.popup_window.focus_force())
    
    def set_time_format(self, fmt):
        """Set time format (12h or 24h)"""
        self.time_format = fmt
        self.save_config()
    
    def toggle_seconds(self, show):
        """Toggle seconds display"""
        self.show_seconds = show
        self.save_config()
    
    def toggle_date(self, show):
        """Toggle date display"""
        self.show_date = show
        self.save_config()
    
    def show_appearance_popup(self):
        """Show appearance customization popup"""
        if self.popup_window is not None:
            try:
                if self.popup_window.winfo_exists():
                    self.popup_window.destroy()
                    return
            except:
                pass
        
        self.popup_window = tk.Toplevel(self.root)
        self.popup_window.overrideredirect(True)
        self.popup_window.attributes('-topmost', True)
        
        bg_color = '#f7f7f7'
        border_color = '#c7c7cc'
        
        # Position
        screen_width = self.popup_window.winfo_screenwidth()
        screen_height = self.popup_window.winfo_screenheight()
        popup_width = 320
        popup_height = 340
        x_pos = screen_width - popup_width - 20
        y_pos = screen_height - popup_height - 60
        
        self.popup_window.geometry(f'{popup_width}x{popup_height}+{x_pos}+{y_pos}')
        
        # Shadow and container
        shadow_frame = tk.Frame(self.popup_window, bg='#d0d0d0')
        shadow_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        main_container = tk.Frame(
            self.popup_window,
            bg=bg_color,
            highlightthickness=1,
            highlightbackground=border_color
        )
        main_container.place(x=0, y=0, relwidth=1, relheight=1)
        
        content = tk.Frame(main_container, bg=bg_color)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(
            content,
            text="Customize Appearance",
            font=('SF Pro Display', 15, 'bold') if platform.system() == 'Darwin' else ('Segoe UI', 12, 'bold'),
            bg=bg_color,
            fg='#1d1d1f'
        )
        title.pack(anchor='w', pady=(0, 20))
        
        # Font size section
        self.create_size_slider(content, bg_color)
        
        tk.Frame(content, bg='#d1d1d6', height=1).pack(fill=tk.X, pady=15)
        
        # Color picker
        color_frame = tk.Frame(content, bg=bg_color)
        color_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            color_frame,
            text="Text Color",
            font=('SF Pro Text', 12) if platform.system() == 'Darwin' else ('Segoe UI', 10),
            bg=bg_color,
            fg='#1d1d1f'
        ).pack(side=tk.LEFT)
        
        color_btn = tk.Label(
            color_frame,
            text="  Choose  ",
            font=('SF Pro Text', 11) if platform.system() == 'Darwin' else ('Segoe UI', 9),
            bg='#0066ff',
            fg='#ffffff',
            padx=15,
            pady=5,
            cursor='hand2'
        )
        color_btn.pack(side=tk.RIGHT)
        
        def choose_color(e):
            color = colorchooser.askcolor(initialcolor=self.text_color)
            if color[1]:
                self.text_color = color[1]
                self.time_label.config(fg=self.text_color)
                self.save_config()
        
        color_btn.bind('<Button-1>', choose_color)
        
        # Done button
        self.create_done_button(content)
        
        self.popup_window.bind('<FocusOut>', lambda e: self.close_popup())
        self.popup_window.after(10, lambda: self.popup_window.focus_force())
    
    def create_size_slider(self, parent, bg_color):
        """Create size adjustment slider"""
        slider_section = tk.Frame(parent, bg=bg_color)
        slider_section.pack(fill=tk.X, pady=(0, 10))
        
        # Label
        tk.Label(
            slider_section,
            text="Font Size",
            font=('SF Pro Text', 12) if platform.system() == 'Darwin' else ('Segoe UI', 10),
            bg=bg_color,
            fg='#1d1d1f'
        ).pack(anchor='w', pady=(0, 10))
        
        # Size indicators
        size_labels_frame = tk.Frame(slider_section, bg=bg_color)
        size_labels_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(
            size_labels_frame,
            text="A",
            font=('SF Pro Text', 11) if platform.system() == 'Darwin' else ('Segoe UI', 9),
            bg=bg_color,
            fg='#86868b'
        ).pack(side=tk.LEFT)
        
        tk.Label(
            size_labels_frame,
            text="A",
            font=('SF Pro Text', 18, 'bold') if platform.system() == 'Darwin' else ('Segoe UI', 14, 'bold'),
            bg=bg_color,
            fg='#86868b'
        ).pack(side=tk.RIGHT)
        
        # Current size display
        size_display_frame = tk.Frame(slider_section, bg=bg_color)
        size_display_frame.pack(pady=(0, 10))
        
        size_value = tk.Label(
            size_display_frame,
            text=str(self.font_size),
            font=('SF Pro Display', 24, 'bold') if platform.system() == 'Darwin' else ('Segoe UI', 18, 'bold'),
            bg=bg_color,
            fg='#1d1d1f'
        )
        size_value.pack(side=tk.LEFT)
        
        size_unit = tk.Label(
            size_display_frame,
            text="pt",
            font=('SF Pro Text', 14) if platform.system() == 'Darwin' else ('Segoe UI', 10),
            bg=bg_color,
            fg='#86868b'
        )
        size_unit.pack(side=tk.LEFT, padx=(4, 0))
        
        def update_display(value):
            size_value.config(text=str(int(float(value))))
            self.update_font_size(value)
        
        # Slider
        slider = tk.Scale(
            slider_section,
            from_=12,
            to=72,
            orient=tk.HORIZONTAL,
            command=update_display,
            bg=bg_color,
            fg='#000000',
            highlightthickness=0,
            troughcolor='#e5e5e5',
            activebackground='#0066ff',
            sliderrelief=tk.FLAT,
            length=280,
            showvalue=False,
            borderwidth=0,
            width=12
        )
        slider.set(self.font_size)
        slider.pack()
    
    def create_done_button(self, parent):
        """Create done button"""
        button_frame = tk.Frame(parent, bg='#f7f7f7')
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        done_btn = tk.Label(
            button_frame,
            text="Done",
            font=('SF Pro Text', 14, 'bold') if platform.system() == 'Darwin' else ('Segoe UI', 11, 'bold'),
            bg='#0066ff',
            fg='#ffffff',
            padx=40,
            pady=10,
            cursor='hand2'
        )
        done_btn.pack()
        
        def on_btn_enter(e):
            done_btn.config(bg='#0052cc')
        
        def on_btn_leave(e):
            done_btn.config(bg='#0066ff')
        
        def on_btn_click(e):
            self.close_popup()
        
        done_btn.bind('<Enter>', on_btn_enter)
        done_btn.bind('<Leave>', on_btn_leave)
        done_btn.bind('<Button-1>', on_btn_click)
    
    def close_popup(self):
        """Safely close popup window"""
        if self.popup_window is not None:
            try:
                self.popup_window.destroy()
            except:
                pass
            self.popup_window = None
    
    def update_font_size(self, value):
        """Update clock font size"""
        self.font_size = int(float(value))
        system = platform.system()
        font_family = 'SF Pro Display' if system == 'Darwin' else 'Segoe UI'
        self.time_label.config(font=(font_family, self.font_size, 'bold'))
        
        # Adjust window size
        self.window_width = max(160, int(self.font_size * 6.5))
        self.window_height = max(60, int(self.font_size * 2.8))
        
        x_pos = self.clock_window.winfo_x()
        y_pos = self.clock_window.winfo_y()
        self.clock_window.geometry(f'{self.window_width}x{self.window_height}+{x_pos}+{y_pos}')
        
        self.save_config()
    
    def create_tray_icon(self):
        """Create system tray icon"""
        icon_image = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(icon_image)
        
        # Clock circle
        draw.ellipse([12, 12, 52, 52], fill='#0066ff', outline='#0066ff')
        draw.ellipse([16, 16, 48, 48], fill='white', outline='white')
        
        # Clock hands
        draw.rectangle([30, 18, 34, 32], fill='#0066ff')
        draw.rectangle([30, 32, 42, 34], fill='#0066ff')
        
        # Center dot
        draw.ellipse([30, 30, 34, 34], fill='#0066ff')
        
        menu = pystray.Menu(
            item('Customize Appearance', self.tray_customize),
            item('Time Format', self.tray_format),
            pystray.Menu.SEPARATOR,
            item('Show Clock', self.show_clock),
            item('Hide Clock', self.hide_clock),
            pystray.Menu.SEPARATOR,
            item('Exit', self.tray_exit)
        )
        
        self.tray_icon = pystray.Icon("clock", icon_image, "Transparent Clock", menu)
        tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        tray_thread.start()
    
    def tray_customize(self):
        self.root.after(0, self.show_appearance_popup)
    
    def tray_format(self):
        self.root.after(0, self.show_format_popup)
    
    def show_clock(self):
        self.root.after(0, self.clock_window.deiconify)
    
    def hide_clock(self):
        self.root.after(0, self.clock_window.withdraw)
    
    def tray_exit(self):
        self.root.after(0, self.close_app)
    
    def close_app(self, event=None):
        self.save_config()
        if self.tray_icon:
            self.tray_icon.stop()
        self.clock_window.destroy()
        self.root.destroy()
    
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    
    def on_move(self, event):
        x = self.clock_window.winfo_x() + event.x - self.x
        y = self.clock_window.winfo_y() + event.y - self.y
        self.clock_window.geometry(f'+{x}+{y}')
    
    def end_move(self, event):
        """Save position when drag ends"""
        self.save_config()
    
    def update_time(self):
        """Update time display"""
        now = datetime.now()
        
        # Format time based on settings
        if self.time_format == '12h':
            if self.show_seconds:
                time_string = now.strftime('%I:%M:%S %p')
            else:
                time_string = now.strftime('%I:%M %p')
        else:
            if self.show_seconds:
                time_string = now.strftime('%H:%M:%S')
            else:
                time_string = now.strftime('%H:%M')
        
        # Add date if enabled
        if self.show_date:
            date_string = now.strftime('%a, %b %d')
            time_string = f'{date_string}\n{time_string}'
        
        self.time_label.config(text=time_string)
        self.root.after(1000, self.update_time)
    
    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    clock = TransparentClock()
    clock.run()