from enum import Enum


class FrameColors(Enum):
    graph = "red"
    control = "black"


class ElementNames(Enum):
    app_title = "Posture Analysis Dashboard"
    graph_title = "Sensor Values"
    graph_y = "Distance (mm)"
    graph_x = "Number of Data"

    button1 = "Stop Graph"
    button2 = "Close APP"


class Measurements(Enum):
    graph_size = (12, 4)
    graph_padding_x = 10
    graph_padding_y = 10


class Fonts(Enum):
    info_panel_font = ("Helvetica", 48)
    button_font = None
    title_font = None


class FilePaths(Enum):
    """ Notes:
    Absolute path for user photos are preferred
    """
    user_photo = "/Users/altairissametov/PycharmProjects/PostureResearchProject/gui/data/img/user_photo.png"
