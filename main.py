import pandas as pd
import data_cleaner as dc
import data_processor as dp


if __name__ == '__main__':
    """ Extract and clean data  """
    file = "data_storage/input_data/new_posture_data.csv"
    df_original = pd.read_csv(file, delimiter=",")
    df_original.name = "With Errors"
    dc.strip_columns(df_original)
    df_original["Sensor 2-3"] = df_original["Sensor 2"] - df_original["Sensor 3"]
    df_original["Sensor 2-1"] = df_original["Sensor 2"] - df_original["Sensor 1"]
    dataframes = dc.split_per_person(df=df_original, num_splits=2)
    columns_to_compress = ["Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4"]

    """ Describe sensors basic statistics """
    dp.describe_sensors_values(df_original)  # includes errors
    df_cleaned = dc.exclude_errors(df_original)
    df_cleaned.name = "No Errors"
    dp.describe_sensors_values(df_cleaned)  # excludes error

    print('\n')
    print("Total VALID rows:\t", df_cleaned.shape[0])
    print("Total INVALID rows:\t", df_original.shape[0]-df_cleaned.shape[0])
    print('\n')

    size_data = dp.get_compressed_data(df_cleaned,
                                       group_column=f"Size",
                                       columns_to_compress=columns_to_compress)
    dp.show_subplots(data=size_data,
                     title=f"Shoulder Size vs Sensors",
                     columns_to_compress=columns_to_compress)

    """ Show correlations """
    # dp.find2_correlations(df_cleaned, col1="Width of shoulders", col2="Sensor 1")
    # dp.find2_correlations(df_cleaned, col1="Width of shoulders", col2="Sensor 3")
    interested_cols = ["Horizational Distance (CM)",
                       "Vertical distance between shoulderes and table surface",
                       "Vertical distance between eye level and table surface",
                       "Width of shoulders",
                       "Horizontal distance between eyes and head posture device",
                       "Sensor 1",
                       "Sensor 2",
                       "Sensor 3",
                       "Sensor 4"]
    dp.show_corr_map(df_original[interested_cols], notes="With Errors")
    dp.show_corr_map(df_cleaned[interested_cols], notes="Without Errors")

    dp.find_group_description(df_cleaned, column_name="Head Posture")
    dp.find_group_description(df_cleaned, column_name="Shoulder Posture")

    """ Get information per subject """

    for i, df in enumerate(dataframes):
        print(f"Subject {i+1}")
        # df = dc.exclude_errors(df)

        """ Process data """
        # dp.find2_correlations(df, col1="Horizontal distance between eyes and head posture device", col2="Sensor 2")
        head_data     = dp.get_compressed_data(df, group_column=f"Head Posture", columns_to_compress=columns_to_compress)
        shoulder_data = dp.get_compressed_data(df, group_column=f"Shoulder Posture", columns_to_compress=columns_to_compress)
        dp.show_subplots(data=head_data, title=f"Head Positions (Subject {i+1})", columns_to_compress=columns_to_compress)
        dp.show_subplots(data=shoulder_data, title=f"Shoulder positions (Subject {i+1})", columns_to_compress=columns_to_compress)
        # if i == 0:
        #     # stop at the first iteration
        #     break

    """ Show values as clusters new functions """
    dp.visualize_clusters(df_cleaned, label_col="Head Posture")
    dp.visualize_clusters(df_cleaned, label_col="Shoulder Posture")
