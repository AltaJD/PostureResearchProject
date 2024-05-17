import tkinter as tk
from typing import Callable
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation


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
        self.title(title)
        self.attributes("-fullscreen", True)
        self.sensor_values = dict()
        self.button_num = 0
        # Tk object handler
        self.alarm_num_label = None  # save the label to update
        self.graph_canvas = None
        self.graph_ax = None
        # Create tk objects
        self.graph_frame = tk.Frame(self)
        self.graph_frame.pack(fill=tk.BOTH, expand=False)
        self.is_stopped = False
        self.func_ani = None
        self.graph_lines = []
        self.create_graph()

    def close(self, event=None) -> None:
        self.is_stopped = True

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

    def create_graph(self) -> None:
        sensor_names = ["Sensor 1", "Sensor 2", "Sensor 3"]
        fig = Figure(figsize=(6, 4), dpi=100)
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

        # Position the canvas using the grid geometry manager
        canvas.get_tk_widget().grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Allow the graph_frame to resize with the window
        self.graph_frame.grid_rowconfigure(0, weight=1)
        self.graph_frame.grid_columnconfigure(0, weight=1)

        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.func_ani = FuncAnimation(fig, self.update_graph, interval=50, blit=True)
        self.graph_canvas = canvas

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

    def add_alarms_label(self, txt_frame: str, txt: str) -> None:
        labelframe = tk.LabelFrame(self, text=txt_frame)
        labelframe.pack(side="left", fill="y", expand=False)
        label = tk.Label(labelframe, text=txt)
        label.pack()
        self.alarm_num_label = label

    def add_button(self, text: str, func: Callable, side=None, fill=None, expand=False) -> None:
        self.button_num += 1
        button = tk.Button(self, text=text, command=func)
        button.pack(side=side, fill=fill, expand=expand)

    def do_nothing(self):
        # Function to visualize
        pass
