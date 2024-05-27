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

    def show_message_frame(self, subject: str, details: str, row=3, col=0):
        self.clear_messages()  # remove previous messages
        frame = tk.LabelFrame(self, text=subject, font=ui_config.Fonts.info_panel_font.value)
        frame.grid(row=row, column=col, padx=10, pady=10)
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
        details = UserDetails(full_name)
        details.password = password
        return details


class UserRegistrationWindow(UserDetailsWindow):
    def __init__(self, parent, title):
        super().__init__(parent, title)
        # Basic memory cells
        self.data_entries_num = 3  # minimum is 3, because other 3 [0-2] are taken for name, password, and buttons
        self.message_location = (7, 0)
        self.category_selection = None
        # Add Shoulder Size categories
        shoulder_sizes: list[str] = ui_config.ElementNames.shoulder_options.value
        self.shoulder_size_var = self.add_category_selection(options=shoulder_sizes,
                                                             name=ui_config.ElementNames.shoulder_category_txt.value)
        # Add Gender categories
        gender_options: list[str] = ui_config.ElementNames.gender_options.value
        self.gender_var = self.add_category_selection(options=gender_options,
                                                      name=ui_config.ElementNames.gender_category_txt.value)
        # Add Date of Birth Selection
        self.date_entry = self.add_date_selection(label_name="Date of Birth")
        # Add numeral entry of data
        self.weight_var, self.weight_entry = self.add_numeral_selection(limit=(30, 300), name="Weight (KG)")
        self.height_var, self.height_entry = self.add_numeral_selection(limit=(100, 300), name="Height (CM)")

    def add_category_selection(self, options: list, name: str) -> tk.StringVar:
        """
        Add a dropdown selection for categories.
        :param options is a list of the categories
        :param name is the category name
        :returns address which will contain selected category for retrieval
        """
        category_label = tk.Label(self, text=f"{name}:")
        category_label.grid(row=self.data_entries_num, column=0, padx=10, pady=10, sticky="e")

        selection_address = tk.StringVar(self)
        selection_address.set(options[0])  # Set the default value

        category_dropdown = tk.OptionMenu(self, selection_address, *options)
        category_dropdown.grid(row=self.data_entries_num, column=1, padx=10, pady=10)
        self.data_entries_num += 1
        return selection_address

    def add_date_selection(self, label_name: str) -> tk.Entry:
        date_label = tk.Label(self, text=label_name)
        date_label.grid(row=self.data_entries_num, column=0, padx=10, pady=10, sticky="e")
        date_field = tk.Entry(self, width=12)
        date_field.grid(row=self.data_entries_num, column=1, padx=10, pady=10)
        date_field.insert(0, "dd-mm-yyyy")
        date_field.bind("<FocusIn>", self.clear_date_placeholder)
        date_field.bind("<FocusOut>", self.validate_date)
        self.data_entries_num += 1
        return date_field

    def clear_date_placeholder(self, event):
        if self.date_entry.get() == "dd-mm-yyyy":
            self.date_entry.delete(0, tk.END)

    def validate_date(self, event):
        date_str = self.date_entry.get()
        try:
            date = datetime.strptime(date_str, "%d-%m-%Y")
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, date.strftime("%d-%m-%Y"))
        except ValueError:
            if date_str == "":
                self.date_entry.insert(0, "dd-mm-yyyy")
            else:
                self.show_message_frame("Error", "Please enter a valid date in the format dd-mm-yyyy.",
                                        row=self.message_location[0],
                                        col=self.message_location[1])

    def add_numeral_selection(self, limit: tuple, name: str) -> tuple[tk.IntVar, tk.Entry]:
        num_label = tk.Label(self, text=name)
        num_label.grid(row=self.data_entries_num, column=0, padx=10, pady=10, sticky="e")
        selection_variable = tk.IntVar()
        selection_variable.set(limit[0])
        selection_entry = tk.Entry(self, textvariable=selection_variable, width=5)
        selection_entry.grid(row=self.data_entries_num, column=1, padx=10, pady=10)
        selection_entry.bind("<FocusOut>", lambda event: self.validate_number(limit, name, selection_variable))
        self.data_entries_num += 1
        return selection_variable, selection_entry

    def validate_number(self, limit: tuple, name: str, selection_variable: tk.IntVar, event=None):
        """
        Validates the numerical input entered by the user.

        Args:
            limit (tuple): A tuple containing the minimum and maximum values for the input.
            name (str): The name of the input field.
            selection_variable (int): it a num containing the selected value
        """
        input_value = selection_variable.get()
        try:
            value = int(input_value)
            if limit[0] <= value <= limit[1]:
                return  # Valid input
            else:
                self.show_message_frame("Error", f"{name} must be between {limit[0]} and {limit[1]}.",
                                        row=self.message_location[0],
                                        col=self.message_location[1])
                selection_variable.set("")
        except ValueError:
            self.show_message_frame("Error", f"{name} must be a valid integer.",
                                    row=self.message_location[0],
                                    col=self.message_location[1])
            selection_variable.set("")

    def get_entered_details(self) -> UserDetails:
        details: UserDetails = super().get_entered_details()
        # get other details
        details.weight = self.weight_var.get()
        details.height = self.height_var.get()
        details.shoulder_size = self.shoulder_size_var.get()
        details.age = self.date_entry.get()
        details.gender = self.gender_var.get()
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
