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

    df_cleaned = dc.exclude_errors(df_original)
    print("Total VALID rows:\t", df_cleaned.shape[0])
    print("Total INVALID rows:\t", df_original.shape[0]-df_cleaned.shape[0])

    size_data = dp.get_compressed_data(df_cleaned, group_column=f"Size")
    dp.show_subplots(data=size_data, title=f"Shoulder Size vs Sensors (Sensor Values Difference)")

    dp.find_correlations(df_cleaned, col1="Width of shoulders", col2="Sensor 1")
    dp.find_correlations(df_cleaned, col1="Width of shoulders", col2="Sensor 3")

    for i, df in enumerate(dataframes):
        print(f"Subject {i+1}")
        df = dc.exclude_errors(df)
        """ Process data """
        dp.find_correlations(df, col1="Sensor 2", col2="Sensor 1")
        dp.find_correlations(df, col1="Sensor 2", col2="Sensor 3")
        dp.find_correlations(df, col1="Horizontal distance between eyes and head posture device", col2="Sensor 2")

        head_data     = dp.get_compressed_data(df, group_column=f"Head Posture")
        shoulder_data = dp.get_compressed_data(df, group_column=f"Shoulder Posture")

        dp.show_subplots(data=head_data, title=f"Head Positions (Sensor Values Difference) (Subject {i+1})")
        dp.show_subplots(data=shoulder_data, title=f"Shoulder positions (Sensor Values Difference) (Subject {i+1})")
        # if i == 0:
        #     # stop at the first iteration
        #     break
