import pandas as pd
import ui_config
import csv
import datetime
import bcrypt
from typing import Union
from tkinter import filedialog
from pathlib import Path
import re


class UserDetails:
    # Meta Data
    first_name: str
    last_name: str
    middle_name: str
    password: str
    # Other details
    weight: Union[int, None]
    height: Union[int, None]
    gender: Union[str, None]
    age: Union[int, None]
    shoulder_size: Union[str, None]
    photo_path: str

    def __init__(self, full_name: str, new_password: str):
        self.parse_full_name(full_name)
        self.photo_path = ui_config.FilePaths.user_photo_icon.value
        self.password = new_password
        self.weight = None
        self.height = None
        self.gender = None
        self.age = None
        self.shoulder_size = None

    def __repr__(self) -> str:
        representation = f"Received UserDetails:\n" \
                         f"Name:\t\t{self.get_full_name()}\n" \
                         f"Has Photo:\t\t{self.has_photo()}\n" \
                         f"Weight:\t\t{self.weight} (kg)\n" \
                         f"Height:\t\t{self.height} (cm)\n" \
                         f"Shoulder Size:\t\t{self.shoulder_size}\n" \
                         f"Gender:\t\t{self.gender}\n" \
                         f"Age:\t\t{self.age}\n"
        return representation

    def parse_full_name(self, name: str) -> None:
        if name == "Unknown":
            self.first_name = name
            self.middle_name = ""
            self.last_name = ""
            return None
        first, *middle, last = name.split()
        # convert array to a single str
        middle = ''.join(middle)
        self.first_name = first
        self.middle_name = self.reformat_mid_name(middle)
        self.last_name = last

    def get_full_name(self) -> str:
        return f"{self.first_name} " \
               f"{self.middle_name} " \
               f"{self.last_name}"

    def has_photo(self) -> bool:
        if self.photo_path == ui_config.FilePaths.user_photo_icon.value:
            return False
        return True

    def get_ordered_data(self) -> list[Union[str, int]]:
        ordered_data = [self.first_name,
                        self.last_name,
                        self.middle_name,
                        self.encrypt_password(self.password),
                        self.photo_path,
                        self.gender,
                        self.age,
                        self.shoulder_size,
                        self.height,
                        self.weight]
        return ordered_data

    def is_valid_password(self, stored_password: str) -> bool:
        stored_password: bytes = stored_password.encode('utf-8')
        this_pw: bytes = self.password.encode('utf-8')
        return bcrypt.checkpw(password=this_pw, hashed_password=stored_password)

    @staticmethod
    def encrypt_password(new_password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def reformat_mid_name(name: Union[str, None]) -> str:
        if name is None:
            return ""
        return name


class SessionInstance:
    user_id: int
    alarm_times: list[str]
    user_details: UserDetails
    session_start_time: datetime.datetime
    graph_file_path: str

    def __init__(self):
        self.user_id = -1
        self.user_details = self.get_default_details()
        self.alarm_times = []
        self.session_start_time = datetime.datetime.now()
        self.graph_file_path = self.get_graph_img_path()

    def update(self, user_id: int, details: UserDetails):
        """ Remember user details when signed in """
        self.user_id = user_id
        self.user_details = details
        self.graph_file_path = self.get_graph_img_path()

    def get_total_alarm_time(self) -> float:
        if len(self.alarm_times) == 0:
            return 0.0
        # Calculate the time difference in minutes
        time_format: str = ui_config.Measurements.time_format.value
        first_time = datetime.datetime.strptime(self.alarm_times[0], time_format)
        last_time = datetime.datetime.strptime(self.alarm_times[-1], time_format)
        time_diff = (last_time - first_time).total_seconds() / 60
        return time_diff

    def get_session_elapsed_time(self) -> str:
        this_time = datetime.datetime.now()
        elapsed_time: datetime.timedelta = this_time-self.session_start_time
        # Convert the elapsed_time to the desired format
        total_seconds = elapsed_time.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        elapsed_time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return elapsed_time_str

    def get_graph_img_path(self, relative_path=False) -> str:
        file_name = "/graph_"+str(self.user_id)+".png"
        if not relative_path:
            return ui_config.FilePaths.graph_folder_path.value + file_name
        path = "/gui/data/img/graphs" + file_name
        return path

    def reset(self):
        """ Reset is used when the user signs out """
        self.user_id = -1
        self.user_details = self.get_default_details()

    @staticmethod
    def get_default_details() -> UserDetails:
        return UserDetails(full_name="Unknown", new_password='')


class ReportWriter:

    path: Union[None, Path]
    session: SessionInstance

    def __init__(self, session: SessionInstance):
        self.session = session
        self.path = None

    def get_stats(self) -> str:
        content = f"""## User Details:\n
        | Name | {self.session.user_details.get_full_name()} |
        | --- | --- |
        | Alarm Total Time | {self.session.get_total_alarm_time()} |
        | Elapsed Time | {self.session.get_session_elapsed_time()} |
        | Age | {self.session.user_details.age} |
        | Gender | {self.session.user_details.gender} |
        | Shoulder Size | {self.session.user_details.shoulder_size} |
        | Weight | {self.session.user_details.weight} |
        | Height | {self.session.user_details.height} |\n
        User photo:\n
        ![User Photo]({self.session.user_details.photo_path})\n
        """
        return content

    def get_header(self) -> str:
        content = f"""# User Report\n
        The report represents the basics information over the usage of the app\n
        ## Sensor Readings:\n
        ![Sensor Values]({self.session.get_graph_img_path(relative_path=True)})\n
        """
        return content

    def save_report(self, path=None):
        """ The function collect all the data from the app
        and save in the format of .md or .txt
        If the param path is None, the user may have an opportunity to select the destination
        """
        content = self.get_header() + self.get_stats()
        content = re.sub(r'\n\s+', '\n', content)
        with open(self.get_path(path), "w", encoding="utf-8") as file:
            file.write(content)

    def get_path(self, path: Union[None, str]) -> Path:
        if path is not None:
            self.path = Path(path)
            return self.path
        new_path = filedialog.asksaveasfilename(filetypes=[("Text Files", ["*.txt", "*.md"])])
        self.path = Path(new_path)
        return self.path


class DatabaseManager:
    """
    Storage and reading the data in csv format
    using pandas
    """
    users_login_path: str
    values_folder: str
    session: SessionInstance
    report_writer: ReportWriter

    def __init__(self):
        self.users_login_path = ui_config.FilePaths.user_login_db_path.value
        self.values_folder = ui_config.FilePaths.values_folder_path.value
        """ Store other object instances """
        self.session = SessionInstance()
        self.report_writer = ReportWriter(session=self.session)

    def get_user_db(self) -> pd.DataFrame:
        """ The method checks for the existence of the file
        and creates an empty file with proper column names
        if no file exists
        """
        try:
            return pd.read_csv(self.users_login_path)
        except:
            users_login_db_headers: list[str] = ui_config.ElementNames.user_login_db_headers.value
            with open(self.users_login_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(users_login_db_headers)
            print("Empty user login csv file has been created")
            return pd.read_csv(self.users_login_path)

    def find_user_in_db(self, details: UserDetails) -> pd.DataFrame:
        df = self.get_user_db()
        df = df.fillna("")
        if df.shape[0] == 0:
            return df  # return an empty df
        df_condition = (df["First Name"] == details.first_name) \
                        & (df["Second Name"] == details.last_name) \
                        & (df["Middle Name"] == details.middle_name)
        df = df[df_condition]
        print(df)
        return df  # return sorted df

    def is_valid_sign_in(self, details: UserDetails) -> bool:
        """ The function determines whether entered details are correct and add them into one session instance """
        df_user = self.find_user_in_db(details)
        if df_user.shape[0] == 0 or not details.is_valid_password(df_user["Password"].iloc[0]):
            return False
        # Get other details
        details.photo_path = df_user["Photo Path"].iloc[0]
        details.gender     = df_user["Gender"].iloc[0]
        details.age        = df_user["Age"].iloc[0]
        details.shoulder_size = df_user["Shoulder Size"].iloc[0]
        details.height     = df_user["Height"].iloc[0]
        details.weight     = df_user["Weight"].iloc[0]
        print("==== User below has signed in ====")
        print(details)
        self.session.update(df_user.index,
                            details)
        return True

    def save_user(self, details: UserDetails) -> bool:
        """ The function returns bool to determine completion of the process
        True if the data has been successfully added
        False if the data is already stored in the db
        """
        data_entity = details.get_ordered_data()
        if self.find_user_in_db(details).shape[0] > 0:
            return False  # details already exists

        with open(self.users_login_path, "a", newline="") as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(data_entity)
        return True  # details have been saved

    def save_data(self, data: dict, time: list[str]):
        """
        The function receive the sensor data collected by app
        and transform to csv file named according to the user id
        """
        # Ensure the user ID is a string and print it for debugging
        user_id = str(self.session.user_id)
        print(f"User ID: {user_id}")

        # Correctly format the path with the user ID
        path: str = f'{self.values_folder}/{user_id}.csv'
        print(f"Path: {path}")

        df = pd.DataFrame.from_dict(data)
        time_ds = pd.Series(data=time)
        df["Time"] = time_ds
        """ Save data """
        df.to_csv(path, index=False)
        path = self.get_default_report_path(extension='.md')
        self.report_writer.save_report(path)  # set path=None, to allow the user for selection of the destination
        print("Total alarm time: ", self.session.get_total_alarm_time(), " minutes")
        print(f"Data has been saved to {path}")
        print(f"Report has been saved to {self.report_writer.path.name}")

    def get_default_report_path(self, extension: str) -> str:
        return ui_config.FilePaths.reports_folder_path.value + '/report_' + str(self.session.user_id) + extension

    def get_user_photo_path(self, relative_path=False) -> str:
        if not relative_path:
            details: UserDetails = self.session.user_details
            if details is None:
                return ""
            return details.photo_path

    def get_graph_save_path(self) -> str:
        path = ui_config.FilePaths.graph_folder_path.value + "/graph_" + str(self.session.user_id) + ".png"
        return path

    def save_new_photo_path(self, new_path: str):
        user_id: int = self.session.user_id
        df: pd.DataFrame = self.get_user_db()
        df['Photo Path'] = df['Photo Path'].astype(str)
        df.loc[user_id, 'Photo Path'] = new_path
        df.to_csv(self.users_login_path, index=False)
