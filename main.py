import pandas as pd
import data_cleaner as dc
import data_processor as dp
import config_reader as cr


def main() -> None:
    def show_discrepancies(df: pd.DataFrame, category=None) -> None:
        column_name = cr.get("discrepancies_column")
        discrepancies_data: dict[str, list[int]] = dp.get_discrepancies(df[column_name].tolist())
        if category is not None:
            title_bar = f"Discrepancies ({df.name}, {category})"
        else:
            title_bar = f"Discrepancies ({df.name})"
        dp.show_bar_chart(discrepancies_data, title=title_bar)

    def show_data_per_subject(df_passed: pd.DataFrame, sensor_cols: list[str], test=False) -> None:
        dataframes_subjects = dp.split_per_person(df=df_passed, num_splits=5)
        for i, df in enumerate(dataframes_subjects):
            subject_num = f"Subject {i+1}"
            print(subject_num)
            # df = dc.exclude_errors(df)
            df.name = "With Errors"

            """ Process data """
            # dp.find2_correlations(df, col1="Horizontal distance between eyes and head posture device", col2="Sensor 2")
            head_data     = dp.get_compressed_data_group(df, group_column=f"Head Posture", columns_to_compress=sensor_cols)
            shoulder_data = dp.get_compressed_data_group(df, group_column=f"Shoulder Posture", columns_to_compress=sensor_cols)
            dp.show_subplots(data=head_data, title=f"Head Positions (Subject {i+1})", columns_to_compress=sensor_cols)
            dp.show_subplots(data=shoulder_data, title=f"Shoulder positions (Subject {i+1})", columns_to_compress=sensor_cols)
            if i == 0 and test is True:
                # stop at the first iteration
                break

    def show_all_values(df_orig: pd.DataFrame, cols: list[str]) -> None:
        zipped = dp.compress_sensors_data(df_orig, columns=cols)
        dp.show_subplots(data={"All Sensors": zipped},
                         title=f"All data ({df_orig.name})",
                         columns_to_compress=cols)

    """ Extract and clean data  """
    file = cr.get("input_csv_file_path")
    df_original = pd.read_csv(file, delimiter=",")
    # df_original = df_original.iloc[:4320]  # get only first 2 subjects only
    df_original.name = "With Errors"
    dc.strip_columns(df_original)
    dp.calculate_discrepancies_column(df=df_original, column_name=cr.get("discrepancies_column"))
    sensor_columns = cr.get("sensor_columns")

    """ Describe sensors basic statistics """
    dp.describe_sensors_values(df_original)  # includes errors
    df_cleaned: pd.DataFrame = dc.exclude_errors(df_original)
    df_cleaned.name = "No Errors"
    dp.describe_sensors_values(df_cleaned)  # excludes error

    print('\n')
    print("Total VALID rows:\t", df_cleaned.shape[0])
    print("Total INVALID rows:\t", df_original.shape[0]-df_cleaned.shape[0])
    print('\n')

    show_all_values(df_original, cols=sensor_columns)

    """ Save DF """
    # file = "data_storage/output_data/df_cleaned.csv"
    # df_cleaned.to_csv(file)

    size_data = dp.get_compressed_data_group(df_cleaned,
                                             group_column=f"Size",
                                             columns_to_compress=sensor_columns)
    dp.show_subplots(data=size_data,
                     title=f"Shoulder Size vs Sensors",
                     columns_to_compress=sensor_columns)

    """ Show correlations and basic math """
    dp.find_group_description(df_original, column_name="Head Posture")
    dp.find_group_description(df_original, column_name="Shoulder Posture")

    """ Show values as clusters new functions """
    dp.visualize_clusters(df_cleaned, label_col="Head Posture")
    dp.visualize_clusters(df_cleaned, label_col="Shoulder Posture")

    """ Show information per subject """
    # show_data_per_subject(df_passed=df_original, sensor_cols=sensor_columns)
    columns = cr.get("correlation_map_columns")
    dp.show_corr_map(df_original[columns], notes="ALL")

    """ Show clusters per shoulder width """
    groups = df_cleaned.groupby("Size")
    for width, data in groups:
        df_shoulder = groups.get_group(width)
        dp.visualize_clusters(df_shoulder,
                              label_col=f"Shoulder Posture",
                              title_note=str(width))

    """ Show discrepancies per head posture """
    groups = df_cleaned.groupby("Head Posture")
    for head, data in groups:
        df_head = groups.get_group(head)
        df_head.name = "With Errors"
        show_discrepancies(df_head, category=str(head))

    """ Show correlation between postures and other parameters """
    cols = ["Width of shoulders",
            "Vertical distance between shoulderes and table surface (shoulder normal)",
            "Vertical distance between shoulderes and table surface (round shoulder)",
            "Vertical distance between eye level and table surface",
            "Vertical distance between Head posture device and table surface",
            "Vertical distance between Chair and the ground",
            "Horizational Distance (CM)",
            "Horizontal distance between eyes and head posture device",
            "Head Posture"]
    df_sorted = df_cleaned[cols]
    df_sorted.name = "No Errors"
    dp.show_one_plot_grouped_by(df_sorted, grouping_col_name="Head Posture")


if __name__ == '__main__':
    main()
