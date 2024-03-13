import pandas as pd
import data_cleaner as dc
import data_processor as dp


if __name__ == '__main__':
    """ Extract and clean data  """
    file = "posture_data.csv"
    df_original = pd.read_csv(file, delimiter=",")
    dc.strip_columns(df_original)
    df_original["Sensor 2-3"] = df_original["Sensor 2"] - df_original["Sensor 3"]
    df_original["Sensor 2-1"] = df_original["Sensor 2"] - df_original["Sensor 1"]
    dp.describe_sensors_values(df_original)
    dataframes = dc.split_per_person(df=df_original, num_splits=5)

    size_data = dp.get_compressed_data(dc.exclude_errors(df_original), group_column=f"Size")
    dp.show_subplots(data=size_data, title=f"Size vs Sensors")

    for i, df in enumerate(dataframes):
        df = dc.exclude_errors(df)
        """ Process data """
        dp.find_correlations(df, col1="Sensor 2", col2="Sensor 1")
        dp.find_correlations(df, col1="Sensor 2", col2="Sensor 3")
        dp.find_correlations(df, col1="Horizontal distance between eyes and head posture device", col2="Sensor 2")

        head_data     = dp.get_compressed_data(df, group_column=f"Head Posture")
        shoulder_data = dp.get_compressed_data(df, group_column=f"Shoulder Posture")

        dp.show_subplots(data=head_data, title=f"Head Positions (Subject {i+1})")
        dp.show_subplots(data=shoulder_data, title=f"Shoulder positions (Subject {i+1})")
