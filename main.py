import pandas as pd
import data_cleaner


def show_sensor_vs_postures(df: pd.DataFrame):
    column_name = "Horizational Distance (CM)"
    grouped_df = df.groupby(column_name)
    print("="*50)
    for group, data_frame in grouped_df:
        # Do something with each group
        print("Group:", group)
        print("Data:")
        print(data_frame)
        print()


if __name__ == '__main__':
    file = "posture_data.csv"
    df = pd.read_csv(file, delimiter=",")
    # print(df)
    # print(f"Columns: {df.columns}")
    data_cleaner.strip_columns(df)
    df = data_cleaner.exclude_errors(df)
    # print(df)
    # print(f"Columns: {df.columns}")
    show_sensor_vs_postures(df)
