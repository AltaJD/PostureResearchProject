import pandas as pd
import ui_config
import csv


class UserDetails:
    # Meta Data
    first_name: str | None
    last_name: str | None
    middle_name: str | None
    # Other details
    photo_path: str | None
    password: str | None

    def __init__(self):
        self.first_name = None
        self.last_name = None
        self.middle_name = None
        self.photo_path = None
        self.password = None

    def __repr__(self) -> str:
        representation = f"Received UserDetails:\n" \
                         f"Name: {self.get_full_name()}\n" \
                         f"Has Photo: {self.has_photo()}"
        return representation

    def parse_full_name(self, name: str) -> None:
        # TODO: implement function
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
        if self.photo_path:
            return True
        return False

    @staticmethod
    def encrypt_password(self, password: str):
        # TODO: implement encryption
        pass

    @staticmethod
    def reformat_mid_name(name: str | None) -> str:
        if name is None:
            return ""
        return name


class SessionInstance:
    user_id: int
    first_name: str | None
    second_name: str | None
    middle_name: str | None
    photo_path: str | None

    def __init__(self):
        self.user_id = -1
        self.first_name = None
        self.second_name = None
        self.middle_name = None
        self.full_name = None
        self.photo_path = ui_config.FilePaths.user_photo_icon.value

    def update_instance(self, id: int, details: UserDetails):
        """ Remember user details when signed in """
        self.user_id = id
        self.first_name = details.first_name
        self.second_name = details.last_name
        self.middle_name = details.middle_name
        self.photo_path = details.photo_path
        self.full_name = self.first_name+" "+self.second_name

    def reset(self):
        """ Reset is used when the user signs out """
        self.user_id = -1
        self.first_name = None
        self.second_name = None
        self.middle_name = None
        self.photo_path = ui_config.FilePaths.user_photo_icon.value


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
        if df_user.shape[0] == 0 or df_user["Password"].iloc[0] != details.password:
            return False
        details.photo_path = df_user["Photo Path"].iloc[0]
        self.session.update_instance(df_user.index,
                                     details)
        return True

    def save_user(self, details: UserDetails) -> bool:
        """ The function returns bool to determine completion of the process
        True if the data has been successfully added
        False if the data is already stored in the db
        """
        data_entity = [details.first_name, details.last_name, details.middle_name, details.password]
        if self.find_user_in_db(details).shape[0] > 0:
            return False  # details already exists

        with open(self.users_login_path, "a", newline="") as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(data_entity)
        return True  # details have been saved

    def save_data(self, data: dict, user_id: int):
        path: str = self.values_folder+f'/{user_id}'
        df = pd.DataFrame.from_dict(data)
        df.to_csv(path)
        print("Data has been saved")

    def get_user_photo_path(self) -> str:
        return self.session.photo_path

    def save_new_photo_path(self, new_path: str):
        user_id: int = self.session.user_id
        df: pd.DataFrame = self.get_user_db()
        df['Photo Path'] = df['Photo Path'].astype(str)
        df.loc[user_id, 'Photo Path'] = new_path
        df.to_csv(self.users_login_path, index=False)