import os.path
from enum import Enum


class FrameColors(Enum):
    graph = "black"
    control = "black"
    header = "white"
    body = "white"
    footer = "white"


class ElementNames(Enum):
    app_title = "Posture Analysis Dashboard"

    graph_title = "Sensor Values"
    graph_y = "Distance (mm)"
    graph_x = "Number of Data"
    sensor_names = ["Sensor 2", "Sensor 4"]

    alarm_num_label = "Number of Alarms"
    processing_time_label = "Processing Time"
    data_notes_label = "Data Notes"

    pause_button_txt = "Pause Graph"
    resume_button_txt = "Resume Graph"
    close_button_txt = "Close APP"
    save_data_button_txt = "Save All Data"
    sign_in_button_txt = "Sign in"
    sign_out_button_txt = "Sign out"
    register_button_txt = "Register"
    edit_photo_button_txt = "Edit Photo"
    save_selected_button_txt = "Save Selected Data"

    sign_in_error = "The user does not exists. Please try again!"

    registration_popup_title = "User Registration"
    sign_in_popup_title = "User Sign In"

    user_login_db_headers = ["First Name",
                             "Second Name",
                             "Middle Name",
                             "Password",
                             "Photo Path",
                             "Gender",
                             "Age",
                             "Shoulder Size",
                             "Height",
                             "Weight"]

    shoulder_options = ["XL", "L", "M", "S", "XS"]
    shoulder_category_txt = "Shoulder Size"

    gender_options = ["Male", "Female", "Prefer not to say"]
    gender_category_txt = "Gender"


class Measurements(Enum):
    graph_size = (12, 4)
    graph_padding_x = 10
    graph_padding_y = 10
    graph_x_limit = 50  # show up to last X values or None for infinite number
    header_h = 200
    footer_h = 100

    photo_h = 50
    photo_w = 50

    pop_up_closing_delay = 2000  # ms
    thread_delay = 0.01  # s

    time_format = "%I:%M:%S %p, %d-%m-%y"


class Fonts(Enum):
    info_panel_font = ("Helvetica", 48)
    button_font = None
    title_font = None


class FilePaths(Enum):
    """ Notes:
    Absolute path for user photos are preferred
    """
    project_root = os.path.dirname(os.path.abspath(__file__))

    """ Specific file paths """
    user_photo_icon = project_root + '/data/img/user_photo.jpeg'
    user_login_db_path = project_root + "/data/users/logins.csv"

    """ Folder paths """
    values_folder_path = project_root + "/data/values"
    graph_folder_path = project_root + "/data/img/graphs"
    reports_folder_path = project_root + "/data/reports"

