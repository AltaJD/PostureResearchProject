import tkinter as tk
from typing import Callable
from datetime import datetime
from datetime import timedelta
from PIL import Image, ImageTk
import ui_config
from database_manager import UserDetails
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class TkCustomImage:
    """ Store 3 type of images:
    1. Original image as np.array
    2. Scaled image as np.array
    3. Tk image of scaled image
    """
    def __init__(self, file_path: str, w: int, h: int):
        self.original_image = Image.open(file_path)
        self.scaled_image = self.original_image.resize((w, h), resample=Image.LANCZOS)
        self.tk_image: tk.PhotoImage = ImageTk.PhotoImage(image=self.scaled_image)

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
        details = UserDetails(full_name, password)
        return details


class UserRegistrationWindow(UserDetailsWindow):
    def __init__(self, parent, title):
        super().__init__(parent, title)
        # Basic memory cells
        self.data_entries_num = 3  # minimum is 3, because other 3 [0-2] are taken for name, password, and buttons
        self.message_location = (7, 3)
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


class NotesEntryFrame(tk.Frame):
    def __init__(self, parent, title=""):
        super().__init__(parent)
        self.add_header_text(title)
        self.paragraph_entry = tk.Text(self, height=10, width=50, wrap="word")
        self.paragraph_entry.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)
        self.control_button_frame = tk.Frame(self, pady=5, padx=5)
        self.control_button_frame.pack(side=tk.BOTTOM, fill='x')
        self.add_scroll_bar()

    def add_header_text(self, title: str) -> None:
        header_label = tk.Label(self, text=title, font=ui_config.Fonts.title_font.value)
        header_label.pack(side=tk.TOP, padx=10, pady=10)

    def add_scroll_bar(self) -> None:
        scrollbar = tk.Scrollbar(self, command=self.paragraph_entry.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.paragraph_entry.config(yscrollcommand=scrollbar.set)

    def add_button(self, text: str, func: Callable) -> None:
        save_button = tk.Button(self.control_button_frame, text=text, command=func)
        save_button.pack(side=tk.LEFT, fill='x')

    def get_notes(self) -> str:
        return self.paragraph_entry.get("1.0", tk.END).strip()


class GraphScrollBar(tk.Scrollbar):
    def __init__(self, parent, options: list[int], figure_func: Callable):
        super().__init__(parent)
        self.config(orient=tk.HORIZONTAL)
        self.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.list_box = self.add_listbox(parent, options)
        self.config(command=self.list_box.xview)
        self.bind('<Motion>', self.scroll_callback)
        self.update_figure_func = figure_func
        self.move_cursor_end()

    def add_listbox(self, parent, options: list[int]):
        box = tk.Listbox(parent, xscrollcommand=self.set, selectmode=tk.EXTENDED, height=2)
        item_string = " ".join([str(option) for option in range(len(options))])
        box.insert(tk.END, item_string)
        box.config(background='#f0f0f0', bd=0, highlightthickness=0)
        box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        return box

    def scroll_callback(self, event=None):
        # Get the visible range of the Listbox
        first, last = self.list_box.xview()
        lower, upper = self.get_visible_range(lower_range=first,
                                              upper_range=last)
        self.update_figure_func(event=None, lower_range=lower, upper_range=upper)

    def get_visible_range(self, lower_range: float, upper_range: float) -> tuple:
        """ The function determine which of the listbox elements are visible for the user
        and figure to be updated
        :returns range as a tuple(from_int, to_int)
        """
        string_options: str = self.list_box.get(0)
        options: list[int] = [int(option) for option in string_options.split()]
        first_el = options[int(lower_range*len(options))]
        last_el = options[int(upper_range * len(options)) - 1]
        # print(f"X_first: {lower_range}, X_last: {upper_range}")
        # print(f"First: {first_el}, Last: {last_el}")
        return first_el, last_el

    def move_cursor_end(self):
        # Scroll to the end of the Listbox
        self.list_box.xview_moveto(1.0)

    def destroy(self):
        super().destroy()
        self.list_box.destroy()

