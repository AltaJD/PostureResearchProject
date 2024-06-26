import tkinter as tk
from tkinter import filedialog
from typing import Callable, Union
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.animation import FuncAnimation
import datetime
import ui_config
from database_manager import DatabaseManager, UserDetails
from custom_widgets import (Clock,
                            TkCustomImage,
                            UserDetailsWindow,
                            FileUploadWindow,
                            UserRegistrationWindow,
                            NotesEntryFrame,
                            GraphScrollBar)
from tensorflow.keras.models import load_model
import numpy as np
import os
import pandas as pd
from matplotlib.widgets import SpanSelector
from matplotlib.patches import Rectangle
import sys


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
        # Update app attributes
        self.title(title)
        # self.attributes("-fullscreen", True)
        self.db_manager = DatabaseManager()
        # Standard variables
        self.sensor_values = dict()
        self.sensor_time = list()  # list[str]
        self.alarm_num = 0
        self.button_num = 0
        self.menu_button_num = 0
        self.is_stopped = False
        self.is_paused = False
        self.graph_size = (12, 4)
        self.info_panel_wnum = 0
        self.prev_alarm_pos = 0
        self.user_data = None
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
        self.alarm_text_label = None
        # Graph
        self.selected_span = None
        self.span_rect = None
        self.span_selector = None
        self.graph_frame = None
        self.graph_canvas = None
        self.graph_ax = None
        self.figure = None
        self.func_ani = None
        # Graph Scroll Bar elements
        self.graph_scroll_bar = None
        self.scroll_bar_frame = None

        self.note_frame = None
        self.control_frame = None

        self.user_photo = None
        self.user_name = None

        self.sign_in_popup = None
        self.registration_popup = None
        self.edit_photo_popup = None

        self.graph_lines = list()  # list of lines
        self.control_buttons = dict()
        # Set up frames and object instances
        self.create_major_frames()
        self.add_header_elements(title=ui_config.ElementNames.app_title.value)
        self.add_body_elements()

        # self.model = load_model('model_all.h5')
        self.current_user_id = None
        self.current_user_features = None
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.csv_path = os.path.join(base_path, 'data', 'users', 'logins.csv')

    def detect_anomaly(self, data: dict):
        # print("detect_anomaly called with data:", data) do not need to print out. only for debugging.
        sensor_2, sensor_4 = "Sensor 2", "Sensor 4"
        if sensor_2 in data and sensor_4 in data and data[sensor_2] and data[sensor_4]:
            recent_data = np.array([[data[sensor_2][-1], data[sensor_4][-1]]])
            print("recent_data:", recent_data)

            if self.current_user_features is None:
                print("No user features available.")
                return

            print(f"User features: {self.current_user_features}")

            sensor4_2_diff = data[sensor_4][-1] - data[sensor_2][-1]
            length = data[sensor_4][-1] * np.cos(np.radians(20)) - data[sensor_2][-1]
            ratio = length / self.current_user_features[4]  # flexibility
            cos_20 = np.cos(np.radians(20))
            sin_20 = np.sin(np.radians(20))
            tangent_d = (data[sensor_4][-1] * cos_20 - data[sensor_2][-1]) / (data[sensor_4][-1] * sin_20)
            degree = np.degrees(np.arctan(tangent_d))

            dynamic_features = np.array(
                [length, degree, sensor4_2_diff, recent_data[0, 0], recent_data[0, 1], self.current_user_features[4],
                 ratio])
            input_data = np.hstack((self.current_user_features[:4], dynamic_features))
            print("input_data:", input_data)

            prediction = self.model.predict(input_data.reshape(1, -1))
            print("prediction:", prediction)
            if prediction[0][0] == 0:
                self.update_alarm_num(pos=len(data[sensor_2]) - 1)
                print("Alarm raised.")

    def create_major_frames(self):
        self.header_frame.pack(fill='both', expand=False)
        self.body_frame.pack(fill='both', expand=True)
        self.footer_frame.pack(fill='both', expand=False)
        # Set frame configurations
        hf_color: str = ui_config.FrameColors.header.value
        bf_color: str = ui_config.FrameColors.body.value
        ff_color: str = ui_config.FrameColors.footer.value
        self.header_frame.config(bg=hf_color, height=ui_config.Measurements.header_h.value)
        self.body_frame.config(bg=bf_color)
        self.footer_frame.config(bg=ff_color, height=ui_config.Measurements.footer_h.value)

    def add_header_elements(self, title: str):
        self.create_header_title(title)
        self.create_default_user_icon()

    def create_header_title(self, title: str):
        # Create header components
        title_label = tk.Label(self.header_frame, text=title, font=("Helvetica", 24))
        title_label.grid(row=self.header_row, column=0, padx=10, pady=10)

    def create_default_user_icon(self):
        image_path: str = ui_config.FilePaths.user_photo_icon.value
        photo_w: int = ui_config.Measurements.photo_w.value
        photo_h: int = ui_config.Measurements.photo_h.value
        user_photo = TkCustomImage(file_path=image_path,
                                   w=photo_w,
                                   h=photo_h)
        img_label: tk.Label = user_photo.attach_image(master=self.header_frame,
                                                      row=self.body_row,
                                                      col=0)
        self.user_photo = img_label

    def add_user_name_label(self, name: str, master: tk.Frame, row: int, col: int):
        label = tk.Label(master, text=name)
        label.grid(row=row, column=col, padx=5, pady=5)
        self.user_name = label

    def add_body_elements(self):
        self.create_graph()
        self.create_control_frame()

    def run_app(self) -> None:
        self.mainloop()

    def update_graph(self, event=None, lower_range=None, upper_range=None) -> list:
        # Param event is essential for correct update of the graph
        lines = []
        if upper_range is None:
            upper_range: int = ui_config.Measurements.graph_x_limit.value
        if self.sensor_values and not self.is_paused:
            for i, sens_name in enumerate(self.sensor_values.keys()):
                x, y = self.get_axes_values(sens_name, upper_limit=upper_range,
                                            lower_limit=lower_range)
                self.graph_lines[i].set_data(x, y)
                if x[0] != x[-1]:
                    self.graph_ax.set_xlim(x[0], x[-1])
                lines.append(self.graph_lines[i])
            y_min = min((min(y) for y in self.sensor_values.values() if y), default=0)
            y_max = max((max(y) for y in self.sensor_values.values() if y), default=1)
            self.graph_ax.set_ylim(y_min, y_max)
            self.detect_anomaly(self.sensor_values)
        if lower_range and upper_range:
            lines = []
            for i, sens_name in enumerate(self.sensor_values.keys()):
                x, y = self.get_axes_values(sens_name, upper_limit=upper_range,
                                            lower_limit=lower_range)
                self.graph_lines[i].set_data(x, y)
                self.graph_ax.set_xlim(x[0], x[-1])
                lines.append(self.graph_lines[i])
            self.detect_anomaly(self.sensor_values)
        return lines

    def update_sensor_values(self, new_data: dict) -> None:
        """ The new data should have the format:
        {"Sensor #:
        [1, 2, 3],
        }
        Remember the timestamp per receipt of the sensor reading
        """
        # Remember the timestamp
        current_time = datetime.datetime.now().strftime(ui_config.Measurements.time_format.value)
        self.sensor_time.append(current_time)
        # Update values
        self.sensor_values = new_data
        self.func_ani.event_source.start()

    def update_alarm_num(self, pos: int) -> None:
        if not self.alarm_num_label or not self.graph_ax or pos == self.prev_alarm_pos:
            return None
        self.alarm_num += 1
        self.alarm_num_label.config(text=str(self.alarm_num))
        self.draw_vert_span(x=pos)
        self.prev_alarm_pos = pos
        self.add_alarm_text()
        this_time = datetime.datetime.now().strftime(ui_config.Measurements.time_format.value)  # 确保 time_format 是字符串
        self.db_manager.session.alarm_times.append(this_time)

    def draw_vert_span(self, x: int, width=1):
        # Add a vertical span to the background
        self.graph_ax.axvspan(x-width/2, x+width/2, facecolor='red', alpha=0.2, zorder=1)

    def draw_graph_arrow(self, x: int, height: int):
        # Draw the arrow
        y_min = min(min(y) for y in self.sensor_values.values())
        self.graph_ax.annotate('',
                               xy=(x, y_min),
                               xytext=(x, y_min + height),
                               arrowprops=dict(arrowstyle='->',
                                               color='r',
                                               linewidth=2))

    def add_alarm_text(self) -> None:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alarm_text = f"Alarm {self.alarm_num} at {current_time}"
        self.alarm_text_label.config(text=alarm_text)
        self.alarm_num += 1

    def create_control_frame(self):
        frame = tk.Frame(self.body_frame)
        frame.grid(row=self.body_row, column=2, padx=10, pady=5)
        self.control_frame = frame  # save the frame

    def create_graph(self) -> None:
        gf = tk.Frame(self.body_frame)
        gf.grid(row=self.body_row, column=1, padx=10, pady=5)
        self.graph_frame = gf  # remember the object
        sensor_names: list[str] = ui_config.ElementNames.sensor_names.value
        fig = Figure(figsize=self.graph_size, dpi=100)
        ax = fig.add_subplot(111)
        ax.set_xlabel("Num of Data")
        ax.set_ylabel("Distance")
        ax.set_title("Sensors Data")
        lim: int = ui_config.Measurements.graph_x_limit.value
        for sensor_name in sensor_names:
            x, y = self.get_axes_values(sensor_name, upper_limit=lim, lower_limit=None)
            line, = ax.plot(x, y, label=sensor_name)
            self.graph_lines.append(line)
        ax.legend()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.graph_canvas = canvas
        self.figure = fig
        self.graph_ax = ax

        self.func_ani = FuncAnimation(self.figure,
                                      func=self.update_graph,
                                      interval=100,
                                      blit=False,
                                      repeat=False)  # remember the object

        alarm_frame = tk.LabelFrame(self.graph_frame, text="Alarm Time", font=("Helvetica", 12))
        alarm_frame.pack(side=tk.BOTTOM, fill="x", pady=10)
        self.alarm_text_label = tk.Label(alarm_frame, text="", font=("Helvetica", 12), fg="red")
        self.alarm_text_label.pack(side=tk.LEFT, padx=10)

        def on_select_span(vmin: int, vmax: int):
            self.selected_span = (vmin, vmax)
            if self.span_rect:
                self.span_rect.remove()
            self.span_rect = ax.add_patch(
                Rectangle((vmin, ax.get_ylim()[0]), vmax - vmin, ax.get_ylim()[1] - ax.get_ylim()[0],
                          color='red', alpha=0.3))
            self.graph_canvas.draw()

        self.span_selector = SpanSelector(
            ax, on_select_span, "horizontal", useblit=True, minspan=0.1
        )

    def save_selected_data(self):
        if self.selected_span is None:
            print("No data selected", file=sys.stderr)
            return

        start, end = self.selected_span
        print(f"Selected span: {start} to {end}")

        data_dict = {'Time': []}
        max_length = 0
        for line in self.graph_lines:
            sensor_name = line.get_label()
            x = line.get_xdata()
            y = line.get_ydata()
            mask = (x >= start) & (x <= end)
            mask_indices = np.where(mask)[0]
            sensor_data = [y[i] for i in mask_indices if i < len(y)]
            time_data = [self.sensor_time[i] for i in mask_indices if i < len(self.sensor_time)]
            if len(sensor_data) > max_length:
                max_length = len(sensor_data)
            data_dict[sensor_name] = sensor_data
            data_dict['Time'] = time_data

        # Add Notes to all values
        notes: str = self.note_frame.get_notes()
        data_dict["Notes"] = [notes for _ in range(max_length)]

        # Ensure all lists in data_dict are of the same length by padding with NaN
        for key in data_dict:
            while len(data_dict[key]) < max_length:
                data_dict[key].append(np.nan)

        result_df = pd.DataFrame(data_dict)
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            result_df.to_csv(file_path, index=False)
            print(f"Data saved to {file_path}")

        # Remove notes frame
        self.note_frame.destroy()

    def get_axes_values(self, sensor: str, upper_limit: Union[None, int], lower_limit=None) -> tuple:
        """
        Retrieves the x and y values for the specified sensor, with optional upper and lower limits.

        Args:
            sensor (str): The name of the sensor.
            upper_limit (Union[None, int]): The upper limit for the number of data points to return. If `None`, all data points are returned.
            lower_limit (Union[None, int], optional): The lower limit for the number of data points to return. If `None`, the lower limit is set to 0. Defaults to `None`.

        Returns:
            Tuple[List[int], List[float]]: A tuple containing the x-axis values (list of integers) and the y-axis values (list of floats).
        """
        if not self.sensor_values.get(sensor):
            return [0], [0]
        x = list(range(len(self.sensor_values[sensor])))
        y = self.sensor_values[sensor]
        if upper_limit is None:
            return x, y

        if upper_limit and len(y) > upper_limit and lower_limit is None:
            x = x[-upper_limit:]
            y = y[-upper_limit:]
            return x, y

        x = x[lower_limit:upper_limit]
        y = y[lower_limit:upper_limit]
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

    def add_control_button(self, text: str, func: Callable) -> None:
        button = tk.Button(self.control_frame, text=text, command=func)
        button.grid(row=self.button_num, column=0, padx=10, pady=10)
        self.button_num += 1
        # Remember the button
        self.control_buttons[text] = button

    def add_menu_button(self, text: str, func: Callable):
        # Add sign in button
        sign_in_button = tk.Button(self.header_frame, text=text, command=func)
        sign_in_button.grid(row=self.body_row, column=self.menu_button_num+1, padx=0, pady=10)
        self.menu_button_num += 1
        self.control_buttons[text] = sign_in_button

    """ Sensor Comm Control """

    def pause_comm(self) -> None:
        self.is_paused = True

    def resume_comm(self) -> None:
        self.is_paused = False

    """ Pop up functions """

    def show_sign_in_popup(self):
        self.pause()
        pop_up = UserDetailsWindow(self, title=ui_config.ElementNames.sign_in_popup_title.value)
        pop_up.add_button(txt="Log in", func=self.sign_in)
        pop_up.add_button(txt="Cancel", func=pop_up.close)
        self.sign_in_popup = pop_up

    def show_register_popup(self):
        self.pause()
        pop_up = UserRegistrationWindow(self, title=ui_config.ElementNames.registration_popup_title.value)
        pop_up.add_button(txt="Submit", func=self.register_user)
        pop_up.add_button(txt="Cancel", func=pop_up.close)
        self.registration_popup = pop_up

    def show_edit_photo_popup(self):
        self.pause()
        popup = FileUploadWindow(self, "File Upload")
        popup.add_button(txt="Select File", func=self.select_file)
        popup.add_button(txt="Upload", func=self.submit_new_user_photo)
        popup.add_button(txt="Cancel", func=popup.close)
        self.edit_photo_popup = popup

    def show_notes_entry(self):
        title = ui_config.ElementNames.data_notes_label.value
        self.note_frame = NotesEntryFrame(self.body_frame, title=title)
        self.note_frame.add_button(text="Save", func=self.save_selected_data)
        self.note_frame.grid(row=2, column=1, padx=10, pady=10)

    """ Control functions """

    def set_user_photo(self, path=None):
        photo_label: tk.Label = self.user_photo
        # The order of procedure should not be changed
        if path is None:
            path: str = self.db_manager.get_user_photo_path()
        if path == "":
            path: str = ui_config.FilePaths.user_photo_icon.value
        width: int = ui_config.Measurements.photo_w.value
        height: int = ui_config.Measurements.photo_h.value
        img = TkCustomImage(path, w=width, h=height)
        photo_label.configure(image=img.tk_image)
        photo_label.image = img.tk_image

    def submit_new_user_photo(self):
        popup: FileUploadWindow = self.edit_photo_popup
        file_path = popup.get_file_path()
        if file_path:
            self.set_user_photo(path=file_path)
            self.db_manager.save_new_photo_path(new_path=file_path)
            popup.show_message_frame("File Uploaded", f"The file '{file_path}' has been uploaded.")
            popup.disable_submission_button()
        else:
            popup.show_message_frame("Error", "Please select a file to upload.")

    def select_file(self):
        popup: FileUploadWindow = self.edit_photo_popup
        file_path = filedialog.askopenfilename()
        popup.file_path_entry.delete(0, tk.END)
        popup.file_path_entry.insert(0, file_path)

    def do_nothing(self):
        # Function to visualize
        pass

    def close(self) -> None:
        self.is_stopped = True

    def save_data(self):
        self.save_graph()
        self.db_manager.save_data(data=self.sensor_values, time=self.sensor_time)

    def sign_in(self):
        pop_up: UserDetailsWindow = self.sign_in_popup
        user_details: UserDetails = pop_up.get_entered_details()
        if not self.db_manager.is_valid_sign_in(details=user_details):
            pop_up.show_message_frame(subject="Error",
                                      details="Entered details do not match the details in the database")
            return
        pop_up.show_message_frame(subject="Success",
                                  details=f"Welcome back, {self.db_manager.session.user_details.get_full_name()}")
        self.set_user_photo()

        print(f"Checking if file exists at path: {self.csv_path}")
        if os.path.exists(self.csv_path):
            print(f"File found at path: {self.csv_path}")
            self.user_data = self.load_user_data(self.csv_path)
            print(f"User data loaded: {self.user_data.head()}")

            print(f"User details: {self.db_manager.session.user_details.__dict__}")

            user_info = {
                'Age': self.db_manager.session.user_details.age,
                'Shoulder Size': self.db_manager.session.user_details.shoulder_size,
                'Height': self.db_manager.session.user_details.height,
                'Weight': self.db_manager.session.user_details.weight
            }
            self.current_user_features = self.process_user_info(user_info)
            print(f"User features loaded and set: {self.current_user_features}")
        else:
            print(f"File not found at path: {self.csv_path}")

        # Change button config
        sign_in_button: tk.Button = self.control_buttons[ui_config.ElementNames.sign_in_button_txt.value]
        sign_in_button.configure(text=ui_config.ElementNames.sign_out_button_txt.value, command=self.sign_out)
        # Add button
        edit_button_txt = ui_config.ElementNames.edit_photo_button_txt.value
        self.add_menu_button(text=edit_button_txt, func=self.show_edit_photo_popup)
        self.add_user_name_label(name=self.db_manager.session.user_details.get_full_name(),
                                 row=self.footer_row,
                                 col=0,
                                 master=self.header_frame)
        self.resume()

    def sign_out(self):
        # Forget session
        self.db_manager.session.reset()
        self.set_user_photo()

        self.current_user_features = None

        # Change button config
        sign_in_button: tk.Button = self.control_buttons[ui_config.ElementNames.sign_in_button_txt.value]
        sign_in_button.configure(text=ui_config.ElementNames.sign_in_button_txt.value, command=self.show_sign_in_popup)
        # Remove the button with name:
        button_txt: str = ui_config.ElementNames.edit_photo_button_txt.value
        self.control_buttons[button_txt].destroy()
        self.user_name.destroy()

    def register_user(self):
        popup: UserRegistrationWindow = self.registration_popup
        user_details: UserDetails = popup.get_entered_details()
        saved: bool = self.db_manager.save_user(user_details)
        if saved:
            popup.show_message_frame(subject="Success",
                                     details="Your personal details has been saved!\n"
                                             "Please try to sign in to your account.",
                                     row=popup.message_location[0],
                                     col=popup.message_location[1])
            self.resume()
        else:
            popup.show_message_frame(subject="Error",
                                     details="User with similar personal details already exists!\n"
                                             "Please try to sign in.",
                                     row=popup.message_location[0],
                                     col=popup.message_location[1])

    def pause(self):
        self.is_paused = True
        button = self.control_buttons[ui_config.ElementNames.pause_button_txt.value]
        resume_txt: str = ui_config.ElementNames.resume_button_txt.value
        button.config(text=resume_txt, command=self.resume)
        # Add scroll bar for the Graph
        self.scroll_bar_frame = tk.Frame(self.body_frame)
        self.scroll_bar_frame.grid(row=3, column=1, pady=10, padx=10, sticky=tk.NSEW)
        self.graph_scroll_bar = GraphScrollBar(parent=self.scroll_bar_frame,
                                               options=self.sensor_time,
                                               figure_func=self.update_graph)

    def resume(self):
        self.is_paused = False
        stop_txt: str = ui_config.ElementNames.pause_button_txt.value
        button = self.control_buttons[stop_txt]
        button.config(text=stop_txt, command=self.pause)
        if self.scroll_bar_frame:
            self.graph_scroll_bar.destroy()
            self.scroll_bar_frame.destroy()

    def save_graph(self):
        file_path = self.db_manager.get_graph_save_path()
        self.figure.savefig(file_path)
        print(f"Graph saved to {file_path}")

    @staticmethod
    def load_user_data(filepath: str) -> Union[pd.DataFrame, None]:
        try:
            data = pd.read_csv(filepath)
            print(f"CSV data loaded successfully from {filepath}")
            print(data.head())
            return data
        except Exception as e:
            print(f"Error loading CSV data: {e}")
            return None

    @staticmethod
    def process_user_info(user_info):
        try:
            birth_date = datetime.datetime.strptime(user_info['Age'], '%m-%d-%Y')
            age = int((datetime.datetime.now() - birth_date).days / 365.25)

            shoulder_size_map = {'XS': 0, 'S': 1, 'M': 2, 'L': 3, 'XL': 4}
            size = shoulder_size_map.get(user_info['Shoulder Size'], -1)

            height = float(user_info['Height']) / 100
            weight = float(user_info['Weight'])

            flexibility = 170  # NEED TO BE CHANGED according to posture_data_collec.py

            features = np.array([age, size, weight, height, flexibility], dtype=float)
            print(f"Processed user features: {features}")
            return features
        except Exception as e:
            print(f"Error processing user info: {e}")
            return None

    # @staticmethod
    # def user_login(user_details):
    #     global user_features
    #     user_features = extract_features(user_details)
    #     print(f"User features loaded: {user_features}")
    #
    # def data_received(self, sensor_data):
    #     data = parse_sensor_data(sensor_data)
    #     self.detect_anomaly(data)
