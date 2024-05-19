import pandas as pd
import ui_config
import sys
import csv


class DatabaseManager:
    """ Storage and reading the data in csv format
    using pandas
    """
    def __init__(self):
        self.users_login_path: str = ui_config.FilePaths.user_login_db_path.value
        self.values_folder: str = ui_config.FilePaths.values_folder_path.value

    def check_user_login(self, first_name: str, second_name: str, middle_name: str, password: str):
        try:
            df_users_login: pd.DataFrame = pd.read_csv(self.users_login_path)
            # TODO: check the number of rows including the passed parameters
        except Exception as e:
            print(f"The users login table csv does not exists! {e}", file=sys.stderr)

    def register_user(self, first_name: str, second_name: str, middle_name: str, new_password: str):
        # TODO: implement the function
        pass

    def save_data(self, data: dict, user_id: int):
        path: str = self.values_folder+f'/{user_id}'
        df = pd.DataFrame.from_dict(data)
        df.to_csv(path)
        print("Data has been saved")
