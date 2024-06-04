import pandas as pd
import ui_config
import csv
import bcrypt
from typing import Union


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
    user_details: Union[UserDetails, None]
    full_name: str
    alarm_times: list[int]  # remember the time for alarms detected per session # TODO

    def __init__(self):
        self.user_id = -1
        self.user_details = None
        self.full_name = "Unknown"
        self.alarm_times = []

    def update(self, user_id: int, details: UserDetails):
        """ Remember user details when signed in """
        self.user_id = user_id
        self.user_details = details
        self.full_name = details.first_name+" "+details.last_name

    def reset(self):
        """ Reset is used when the user signs out """
        self.user_id = -1
        self.user_details = None


class DatabaseManager:
    """ Storage and reading the data in csv format
    using pandas
    """
    users_login_path: str
    values_folder: str
    session: SessionInstance

    def __init__(self):
        self.users_login_path = ui_config.FilePaths.user_login_db_path.value
        self.values_folder = ui_config.FilePaths.values_folder_path.value
        """ Store user session instance """
        self.session = SessionInstance()

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

    def save_data(self, data: dict, user_id: int):
        """ The function receive the sensor data collected by app
        and transform to csv file named according to the user id
        """
        path: str = self.values_folder+f'/{user_id}'
        df = pd.DataFrame.from_dict(data)
        df.to_csv(path)
        print("Data has been saved")

    def get_user_photo_path(self) -> str:
        details: UserDetails = self.session.user_details
        return details.photo_path

    def save_new_photo_path(self, new_path: str):
        user_id: int = self.session.user_id
        df: pd.DataFrame = self.get_user_db()
        df['Photo Path'] = df['Photo Path'].astype(str)
        df.loc[user_id, 'Photo Path'] = new_path
        df.to_csv(self.users_login_path, index=False)