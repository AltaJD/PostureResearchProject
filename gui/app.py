import tkinter as tk
from typing import Callable
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from datetime import datetime
from datetime import timedelta
from PIL import Image, ImageTk
import ui_config
from database_manager import DatabaseManager


class TkCustomImage:
    """ Store 3 type of images:
    1. Original image as np.array
    2. Scaled image as np.array
    3. Tk image of scaled image
    """
    def __init__(self, file_path: str, w: int, h: int):
        self.original_image = Image.open(file_path)
        self.scaled_image = self.original_image.resize((w, h), resample=Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(image=self.scaled_image)


class Clock(tk.Frame):
    """ The clock widget to show the time elapsed """
    def __init__(self, parent):
        super().__init__(parent)
        self.start_time = datetime.now()
        self.time_label = tk.Label(self, font=("Helvetica", 48))
        self.time_label.pack(pady=20)
        self.update_time()

    def update_time(self):
        elapsed_time = datetime.now() - self.start_time
        time_str = str(timedelta(seconds=int(elapsed_time.total_seconds())))
        self.time_label.configure(text=time_str)
        self.after(1000, self.update_time)


class App(tk.Tk):
    """ GUI to show Data Storage
    sensor_values is a dict of list of the values from the sensors:
    {"Sensor #:
        [1, 2, 3],
    }
    data_thread is a side thread to read data async
    """
    def __init__(self, title: str):
        super().__init__()
        # Standard variables
        self.sensor_values = dict()
        self.button_num = 0
        self.menu_button_num = 0
        self.is_stopped = False
        self.is_paused = False
        self.graph_size = (12, 4)
        self.info_panel_wnum = 0
        # Structure of each frame
        self.header_row = 0
        self.header_frame = tk.Frame(self)
        self.body_row = 1
        self.body_frame = tk.Frame(self)
        self.footer_row = 2
        self.footer_frame = tk.Frame(self)
        # Set tk objects to remember
        self.info_panel = tk.Frame(self.body_frame)
        self.info_panel.grid(row=self.body_row, column=0, padx=10, pady=5)
        self.alarm_num_label = None
        self.graph_frame = None
        self.control_frame = None
        self.graph_canvas = None
        self.graph_ax = None
        self.func_ani = None
        self.graph_lines = list()  # list of lines
        self.control_buttons = dict()
        # Set up frames and objects
        self.create_major_frames()
        self.add_header_elements(title=ui_config.ElementNames.app_title.value)
        self.add_body_elements()
        # Update app attributes
        self.title(title)
        self.attributes("-fullscreen", True)
        self.db_manager = DatabaseManager()

    def create_major_frames(self):
        self.header_frame.pack(fill='both', expand=False)
        self.body_frame.pack(fill='both', expand=True)
        self.footer_frame.pack(fill='both', expand=False)
        self.header_frame.config(bg='red', height=ui_config.Measurements.header_h.value)
        self.body_frame.config(bg='white')
        self.footer_frame.config(bg='green', height=ui_config.Measurements.footer_h.value)

    def add_header_elements(self, title: str):
        self.create_header_title(title)
        self.create_default_user_icon()
        self.add_menu_button(text="Sign in", func=self.do_nothing)
        self.add_menu_button(text="Register", func=self.do_nothing)

    def create_header_title(self, title: str):
        # Create header components
        title_label = tk.Label(self.header_frame, text=title, font=("Helvetica", 24))
        title_label.grid(row=self.header_row, column=0, padx=10, pady=10)

    def create_default_user_icon(self):
        # Add user photo
        user_photo_path: str = ui_config.FilePaths.user_photo.value
        user_photo = TkCustomImage(file_path=user_photo_path, w=50, h=50).tk_image
        user_photo_label = tk.Label(self.header_frame, image=user_photo)
        user_photo_label.grid(row=self.body_row, column=0, padx=10, pady=10)

    def add_menu_button(self, text: str, func: Callable):
        # Add sign in button
        sign_in_button = tk.Button(self.header_frame, text=text, command=func)
        sign_in_button.grid(row=self.body_row, column=self.menu_button_num+1, padx=0, pady=10)
        self.menu_button_num += 1

    def add_body_elements(self):
        self.create_graph()
        self.create_control_frame()

    def run_app(self) -> None:
        self.mainloop()

    def update_graph(self, frame=None) -> list:
        lines = []
        for i, sens_name in enumerate(self.sensor_values.keys()):
            x, y = self.get_axes_values(sens_name)
            self.graph_lines[i].set_data(x, y)
            self.graph_ax.set_xlim(0, len(x) - 1)
            lines.append(self.graph_lines[i])
        if self.sensor_values:
            y_min = min(min(y) for y in self.sensor_values.values())
            y_max = max(max(y) for y in self.sensor_values.values())
            self.graph_ax.set_ylim(y_min, y_max)
        return lines

    def update_sensor_values(self, new_data: dict) -> None:
        """ The new data should have the format:
        {"Sensor #:
        [1, 2, 3],
        }
        """
        self.sensor_values = new_data
        self.func_ani.event_source.start()

    def update_alarm_num(self, num: int) -> None:
        if self.alarm_num_label:
            self.alarm_num_label.config(text=str(num))

    def create_control_frame(self):
        frame = tk.Frame(self.body_frame)
        frame.grid(row=self.body_row, column=2, padx=10, pady=5)
        self.control_frame = frame  # save the frame

    def create_graph(self) -> None:
        gf = tk.Frame(self.body_frame)
        gf.grid(row=self.body_row, column=1, padx=10, pady=5)
        self.graph_frame = gf  # remember the object
        sensor_names = ["Sensor 1", "Sensor 2", "Sensor 3"]
        fig = Figure(figsize=self.graph_size, dpi=100)
        self.graph_ax = fig.add_subplot(111)
        self.graph_ax.set_xlabel("Num of Data")
        self.graph_ax.set_ylabel("Distance")
        self.graph_ax.set_title("Sensors Data")
        for sensor_name in sensor_names:
            x, y = self.get_axes_values(sensor_name)
            line, = self.graph_ax.plot(x, y, label=sensor_name)
            self.graph_lines.append(line)
        self.graph_ax.legend()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.func_ani = FuncAnimation(fig, self.update_graph, interval=50, blit=True)  # remember the object
        self.graph_canvas = canvas  # remember the object

    def get_axes_values(self, sensor: str):
        if self.sensor_values.get(sensor):
            x = list(range(len(self.sensor_values[sensor])))
            y = self.sensor_values[sensor]
        else:
            x = [0]
            y = [0]
        return x, y

    def get_subplot_title(self):
        if self.graph_ax:
            title = self.graph_ax.get_title()
            return title
        else:
            return None

    def create_alarms_label(self, txt_frame: str, txt: str) -> None:
        labelframe = tk.LabelFrame(self.info_panel, text=txt_frame)
        labelframe.grid(row=self.info_panel_wnum, column=0, padx=10, pady=5)
        label = tk.Label(labelframe, text=txt, font=("Helvetica", 48))
        label.pack()
        self.alarm_num_label = label
        self.info_panel_wnum += 1

    def create_clock_label(self, txt_frame: str) -> None:
        labelframe = tk.LabelFrame(self.info_panel, text=txt_frame)
        labelframe.grid(row=self.info_panel_wnum, column=0, padx=10, pady=5)
        clock = Clock(labelframe)
        clock.pack(fill="both", expand=True)
        self.info_panel_wnum += 1

    def add_control_button(self, text: str, func: Callable, side=None, fill=None, expand=False) -> None:
        button = tk.Button(self.control_frame, text=text, command=func)
        button.grid(row=self.button_num, column=0, padx=10, pady=10)
        self.button_num += 1
        # Remember the button
        self.control_buttons[text] = button

    """ Control functions """
    def do_nothing(self):
        # Function to visualize
        pass

    def close(self, event=None) -> None:
        self.is_stopped = True

    def save_data(self):
        self.db_manager.save_data(data=self.sensor_values, user_id=0)
