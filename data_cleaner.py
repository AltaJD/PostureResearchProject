import pandas as pd


def split_per_person(df: pd.DataFrame, num_splits=5) -> list[pd.DataFrame]:
    """ Divide the dataframe into new dataframes
    !Assumption: each subject has equal number of records
    :param df is original (non-modified) dataframe with all values
    :param num_splits is number of subjects per sample
    :returns the list of new dataframes
    """
    total_rows = 4321
    rows_per_split = total_rows // num_splits
    dataframes = []
    start_index = 0

    for i in range(num_splits):
        end_index = start_index + rows_per_split

        if i == num_splits - 1:
            # For the last split, include any remaining rows
            end_index = total_rows

        split_df = df.iloc[start_index:end_index]
        dataframes.append(split_df)

        start_index = end_index

    return dataframes


def strip_columns(data: pd.DataFrame) -> None:
    """ Removes the left and right whitespaces of the headers of df """
    original_columns: list[str] = data.columns
    cleared_columns = list(map(lambda x: x.strip(), original_columns))
    assert len(cleared_columns) == len(original_columns), "MISSING columns"
    # create the dictionary of org columns (keys) and new columns (value)
    columns_to_rename = {key: value for key, value in zip(original_columns, cleared_columns)}
    data.rename(columns=columns_to_rename, inplace=True)
    print("Dataframe Columns are cleared")


def exclude_errors(df: pd.DataFrame) -> pd.DataFrame:
    """ Exclude rows that includes the sensor values below 650 and higher than 900 """
    # configure attributes containing error values
    columns = ["Sensor 1", "Sensor 2", "Sensor 3"]
    # define range of appropriate range of values
    lr = 650  # low range
    hr = 900  # high range
    # Exclude rows with values outside the range
    filtered_df = df[
        (df[columns[0]].between(lr, hr)) &
        (df[columns[1]].between(lr, hr)) &
        (df[columns[2]].between(lr, hr))
    ]
    return filtered_df
