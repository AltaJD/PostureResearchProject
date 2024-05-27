import tkinter as tk
from tkinter import filedialog
from typing import Callable
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

import ui_config
from database_manager import DatabaseManager, UserDetails
from custom_widgets import Clock, TkCustomImage, UserDetailsWindow, FileUploadWindow, UserRegistrationWindow


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
        self.attributes("-fullscreen", True)
        self.db_manager = DatabaseManager()
        # Standard variables
        self.sensor_values = dict()
        self.alarm_num = 0
        self.button_num = 0
        self.menu_button_num = 0
        self.is_stopped = False
        self.is_paused = False
        self.graph_size = (12, 4)
        self.info_panel_wnum = 0
        self.prev_alarm_pos = 0
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
        self.figure = None
        self.func_ani = None
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
        self.start_graph_refreshing()
        self.create_control_frame()

    def run_app(self) -> None:
        self.mainloop()

    def update_graph(self, frame=None) -> list:
        lines = []
        lim: int = ui_config.Measurements.graph_x_limit.value
        for i, sens_name in enumerate(self.sensor_values.keys()):
            x, y = self.get_axes_values(sens_name, limit=lim)
            self.graph_lines[i].set_data(x, y)
            self.graph_ax.set_xlim(x[0], x[-1])
            lines.append(self.graph_lines[i])
        if self.sensor_values and not self.is_paused:
            y_min = min((min(y) for y in self.sensor_values.values() if y), default=0)
            y_max = max((max(y) for y in self.sensor_values.values() if y), default=1)
            self.graph_ax.set_ylim(y_min, y_max)
            self.detect_anomaly(self.sensor_values)
            self.graph_canvas.draw()
        return lines

    def detect_anomaly(self, data: dict):
        # RAISE ALARM
        sensor_2, sensor_4 = "Sensor 2", "Sensor 4"
        if sensor_2 in data and sensor_4 in data and data[sensor_2] and data[sensor_4]:
            if abs(data[sensor_2][-1] - data[sensor_4][-1]) >= 50: ##RANGE MAY BE CHANGED
                self.update_alarm_num(pos=len(data[sensor_2]) - 1)

    def update_sensor_values(self, new_data: dict) -> None:
        """ The new data should have the format:
        {"Sensor #:
        [1, 2, 3],
        }
        """
        self.sensor_values = new_data
        self.func_ani.event_source.start()

    def update_alarm_num(self, pos: int) -> None:
        if not self.alarm_num_label or not self.graph_ax or pos == self.prev_alarm_pos:
            return None
        self.alarm_num += 1
        self.alarm_num_label.config(text=str(self.alarm_num))
        self.draw_vert_span(x=pos)
        self.prev_alarm_pos = pos

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
            x, y = self.get_axes_values(sensor_name, limit=lim)
            line, = ax.plot(x, y, label=sensor_name)
            self.graph_lines.append(line)
        ax.legend()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.graph_canvas = canvas
        self.figure = fig
        self.graph_ax = ax

    def get_axes_values(self, sensor: str, limit=None):
        if self.sensor_values.get(sensor):
            x = list(range(len(self.sensor_values[sensor])))
            y = self.sensor_values[sensor]
            if limit and len(y) > limit:
                x = x[-limit:]
                y = y[-limit:]
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

    """ UI modification """

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

    """ Control functions """

    def set_user_photo(self, path=None):
        photo_label: tk.Label = self.user_photo
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

    def close(self, event=None) -> None:
        self.is_stopped = True

    def save_data(self):
        self.db_manager.save_data(data=self.sensor_values, user_id=0)

    def sign_in(self):
        pop_up: UserDetailsWindow = self.sign_in_popup
        user_details: UserDetails = pop_up.get_entered_details()
        if not self.db_manager.is_valid_sign_in(details=user_details):
            pop_up.show_message_frame(subject="Error",
                                      details="Entered details do not match the details in the database")
            return
        pop_up.show_message_frame(subject="Success",
                                  details=f"Welcome back, {self.db_manager.session.full_name}")
        self.set_user_photo()
        # Change button config
        sign_in_button: tk.Button = self.control_buttons[ui_config.ElementNames.sign_in_button_txt.value]
        sign_in_button.configure(text=ui_config.ElementNames.sign_out_button_txt.value, command=self.sign_out)
        # Add button
        edit_button_txt = ui_config.ElementNames.edit_photo_button_txt.value
        self.add_menu_button(text=edit_button_txt, func=self.show_edit_photo_popup)
        self.add_user_name_label(name=self.db_manager.session.full_name,
                                 row=self.footer_row,
                                 col=0,
                                 master=self.header_frame)
        self.resume()

    def sign_out(self):
        # Forget session
        self.db_manager.session.reset()
        self.set_user_photo()
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

    def start_graph_refreshing(self):
        self.func_ani = FuncAnimation(self.figure, self.update_graph, interval=50, blit=True)  # remember the object

    def pause(self):
        self.is_paused = True
        button = self.control_buttons[ui_config.ElementNames.pause_button_txt.value]
        resume_txt: str = ui_config.ElementNames.resume_button_txt.value
        button.config(text=resume_txt, command=self.resume)

    def resume(self):
        self.is_paused = False
        stop_txt: str = ui_config.ElementNames.pause_button_txt.value
        button = self.control_buttons[stop_txt]
        button.config(text=stop_txt, command=self.pause)