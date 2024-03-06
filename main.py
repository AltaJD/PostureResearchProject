import pandas as pd
import numpy as np
# import seaborn as sbs


def sep_():
    print("="*40)


def strip_columns(data: pd.DataFrame) -> None:
    """ Removes the left and right whitespaces of the headers of df """
    original_columns: list[str] = data.columns
    cleared_columns = list(map(lambda x: x.strip(), original_columns))
    assert len(cleared_columns) == len(original_columns), "MISSING columns"
    # create the dictionary of org columns (keys) and new columns (value)
    columns_to_rename = {key: value for key, value in zip(original_columns, cleared_columns)}
    data.rename(columns=columns_to_rename, inplace=True)
    sep_()
    print("Dataframe Columns are cleared")


def exclude_errors(df: pd.DataFrame) -> pd.DataFrame:
    """ Exclude rows that includes the sensor values below 650 and higher than 900 """
    # configure attributes containing error values
    columns = ["Sensor 1", "Sensor 2", "Sensor 3"]
    # define range of appropriate range of values
    lr = 650  # low range
    hr = 900  # high range
    # skip rows containing the values not in the range
    sep_()
    print("Error rows were excluded")
    return df[np.logical_and(df[columns[0]] > lr, df[columns[0]] < hr) |
            np.logical_and(df[columns[1]] > lr, df[columns[1]] < hr) |
            np.logical_and(df[columns[1]] > lr, df[columns[1]] < hr)
            ]


if __name__ == '__main__':
    file = "posture_data.csv"
    df = pd.read_csv(file, delimiter=",")
    sep_()
    print(df)
    print(f"Columns: {df.columns}")
    strip_columns(df)
    df = exclude_errors(df)
    sep_()
    print(df)
    print(f"Columns: {df.columns}")
