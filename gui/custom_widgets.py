import tkinter as tk
from typing import Callable
from datetime import datetime
from datetime import timedelta
from PIL import Image, ImageTk
import ui_config
from database_manager import UserDetails


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

    def attach_image(self, master, row: int, col: int) -> tk.Label:
        image_label = tk.Label(master, image=self.tk_image)
        image_label.image = self.tk_image
        image_label.grid(row=row, column=col, padx=5, pady=5)
        return image_label


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


class AbstractWindow(tk.Toplevel):
    def __init__(self, parent, title: str):
        super().__init__()
        self.title(title)
        self.parent = parent
        self.submission_button = None
        self.button_nums = 0
        self.message_frame = None

    def close(self):
        self.destroy()

    def clear_messages(self):
        if self.message_frame:
            self.message_frame.destroy()

    def show_message_frame(self, subject: str, details: str):
        self.clear_messages()  # remove previous messages
        frame = tk.LabelFrame(self, text=subject, font=ui_config.Fonts.info_panel_font.value)
        frame.grid(row=3, column=1, padx=10, pady=10)
        details_label = tk.Label(frame, text=details)
        details_label.pack()
        delay: int = ui_config.Measurements.pop_up_closing_delay.value
        self.message_frame = frame
        if subject != "Error":
            self.after(delay, func=self.close)

    def disable_submission_button(self):
        button: tk.Button = self.submission_button
        button.config(command=self.do_nothing)

    def add_button(self, txt: str, func: Callable):
        # Submit button
        submit_button = tk.Button(self, text=txt, command=func)
        submit_button.grid(row=2, column=self.button_nums, padx=10, pady=10)
        self.submission_button = submit_button
        self.button_nums += 1

    @staticmethod
    def do_nothing():
        pass


class UserDetailsWindow(AbstractWindow):
    def __init__(self, parent, title: str):
        super().__init__(parent, title)
        # Remember the fields
        self.full_name_entry = None
        self.password_entry = None
        # Create the widgets
        self.create_widgets()

    def create_widgets(self):
        # Full name label and entry
        full_name_label = tk.Label(self, text="Full Name:")
        full_name_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.full_name_entry = tk.Entry(self)
        self.full_name_entry.grid(row=0, column=1, padx=10, pady=10)

        # Password label and entry
        password_label = tk.Label(self, text="Password:")
        password_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

    def get_entered_details(self) -> UserDetails:
        """ Get the values from popupfields as str
        and return as UserDetails object
        """
        # Get the values from the entry fields
        full_name: str = self.full_name_entry.get()
        password: str = self.password_entry.get()
        details = UserDetails()
        details.parse_full_name(full_name)
        details.password = password
        # Perform any necessary validation or processing
        print(details)
        return details


class FileUploadWindow(AbstractWindow):
    def __init__(self, parent, title: str):
        super().__init__(parent, title)
        # Remember the fields
        self.file_path_entry = None
        # Create the widgets
        self.create_widgets()

    def create_widgets(self):
        # File path label and entry
        file_path_label = tk.Label(self, text="File Path:")
        file_path_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.file_path_entry = tk.Entry(self)
        self.file_path_entry.grid(row=0, column=1, padx=10, pady=10)

    def get_file_path(self) -> str:
        return self.file_path_entry.get()
