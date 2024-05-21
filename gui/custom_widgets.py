import tkinter as tk
from typing import Callable
from datetime import datetime
from datetime import timedelta
from PIL import Image, ImageTk
import ui_config


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

    def show_image(self, master: tk.Tk, row: int, col: int):
        image_label = tk.Label(master, image=self.tk_image)
        image_label.grid(row=row, column=col)


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


class UserDetailsWindow(tk.Toplevel):
    def __init__(self, parent, title: str):
        super().__init__(parent)
        self.title(title)
        self.parent = parent
        # Basic variables
        self.button_nums = 0
        # Remember the fields
        self.full_name_entry = None
        self.password_entry = None
        # Create the widgets
        self.create_widgets()
        self.submission_button = None

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

    def add_button(self, txt: str, func: Callable):
        # Submit button
        submit_button = tk.Button(self, text=txt, command=func)
        submit_button.grid(row=2, column=self.button_nums, padx=10, pady=10)
        self.submission_button = submit_button
        self.button_nums += 1

    def get_entered_details(self) -> dict:
        """ Get the values from popupfields as str
        and return as a dict
        {"first_name": str,
        "middle_name": str,
        "last_name": str,
        "password": str
        }
        """
        # Get the values from the entry fields
        full_name: str = self.full_name_entry.get()
        password: str = self.password_entry.get()
        first, *middle, last = full_name.split()
        # convert array middle to a string
        middle = ''.join(middle)
        # Perform any necessary validation or processing
        print(f"First Name: {first}")
        print(f"Middle Name: {middle}")
        print(f"Last Name: {last}")
        print(f"Password: {password}")

        return {"first_name": first,
                "middle_name": middle,
                "last_name": last,
                "password": password
                }

    def show_message_frame(self, subject: str, details: str):
        message_frame = tk.LabelFrame(self, text=subject, font=ui_config.Fonts.info_panel_font.value)
        message_frame.grid(row=3, column=1, padx=10, pady=10)
        details_label = tk.Label(message_frame, text=details)
        details_label.pack()
        delay: int = ui_config.Measurements.pop_up_closing_delay.value
        self.after(delay, func=self.close_pop_up)

    def disable_submission_button(self):
        button: tk.Button = self.submission_button
        button.config(command=self.do_nothing)

    def close_pop_up(self):
        self.destroy()

    @staticmethod
    def do_nothing():
        pass


class FileUploadWindow(tk.Toplevel):
    def __init__(self, parent, title: str):
        super().__init__(parent)
        self.title(title)
        self.parent = parent
        # Basic variables
        self.button_nums = 0
        # Remember the fields
        self.file_path_entry = None
        # Create the widgets
        self.create_default_widgets()
        self.submission_button = None

    def create_default_widgets(self):
        # File path label and entry
        file_path_label = tk.Label(self, text="File Path:")
        file_path_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.file_path_entry = tk.Entry(self)
        self.file_path_entry.grid(row=0, column=1, padx=10, pady=10)

    def add_button(self, txt: str, func: Callable):
        # Submit button
        submit_button = tk.Button(self, text=txt, command=func)
        submit_button.grid(row=1, column=self.button_nums, padx=10, pady=10)
        self.submission_button = submit_button
        self.button_nums += 1

    def get_file_path(self) -> str:
        return self.file_path_entry.get()

    def show_message_frame(self, subject: str, details: str):
        message_frame = tk.LabelFrame(self, text=subject, font=("Arial", 16))
        message_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        details_label = tk.Label(message_frame, text=details)
        details_label.pack()
        delay: int = ui_config.Measurements.pop_up_closing_delay.value
        self.after(delay, func=self.close_pop_up)

    def disable_submission_button(self):
        button: tk.Button = self.submission_button
        button.config(command=self.do_nothing)

    def close_pop_up(self):
        self.destroy()

    @staticmethod
    def do_nothing():
        pass
