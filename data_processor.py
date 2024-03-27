import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Callable
import numpy as np
import config_reader as cr
from mpl_toolkits.mplot3d import Axes3D

save_img_file_path = cr.get("save_img_file_path")
save_csv_file_path = cr.get("save_csv_file_path")
fig_height = cr.get("fig_height")  # inches
fig_width = cr.get("fig_width")  # inches


def rename_img_file(name: str) -> str:
    global save_img_file_path
    file_path = save_img_file_path.replace("default.png", name)
    return file_path


def rename_csv_file(name: str) -> str:
    global save_csv_file_path
    file_path = save_csv_file_path.replace("default.csv", name)
    return file_path


def get_discrepancies(values: list[int]) -> dict[str, list[int]]:
    """
    Discrepancies are represented as dict:
    {
    "larger_50": [1, 2, 3],
    "larger_100": [1, 2, 3],
    "larger_150": [1, 2, 3],
    }
    """
    def get_filter_func(threshold: int) -> Callable:
        def filter_func(x) -> bool:
            if x > threshold:
                return True
            else:
                return False

        return filter_func

    larger_50  = get_filter_func(50)
    larger_100 = get_filter_func(100)
    larger_150 = get_filter_func(150)

    return {"larger_50": list(filter(larger_50, values)),
            "larger_100": list(filter(larger_100, values)),
            "larger_150": list(filter(larger_150, values))}


def compress_sensors_data(df: pd.DataFrame, columns: list[str]) -> list[list[float]]:
    """ Return the list of the sensors values as list of list
    where index represents sensor number
    :returns [[659, 651, ...], [850, 851, ...], [659, 651, ...]]
    """
    result = []
    for col_name in columns:
        result.append(df[col_name].tolist())
    return result


def split_per_person(df: pd.DataFrame, num_splits=5) -> list[pd.DataFrame]:
    """ Divide the dataframe into new dataframes
    !Assumption: each subject has equal number of records
    :param df is original (non-modified) dataframe with all values
    :param num_splits is number of subjects per sample
    :returns the list of new dataframes
    """
    total_rows = len(df)
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


def get_compressed_data_group(df: pd.DataFrame, group_column: str, columns_to_compress: list[str]) -> dict:
    """ Returns the data in the format:
    {"Posture Name": [float1, float2, ...]}
    """
    result = {}
    grouped_df = df.groupby(group_column)
    for group_name, data_frame in grouped_df:
        grouped_values = grouped_df.get_group(group_name)
        result[str(group_name)] = compress_sensors_data(grouped_values, columns=columns_to_compress)
    return result


def describe_sensors_values(df: pd.DataFrame) -> None:
    """
    1. Shows the percentage of valid values over all received values
    Assumption: error values are considered to be outside of range [lr, hr]
    Formula: valid_values/all_values*100 rounded to 2 digits after comma
    2. Provides basic statistics of sensor values using pd.describe()
    3. Determines the correlations between sensor values
    """
    def filtered_list_from_errors(values: list[float]) -> list[float]:
        """ Return only the values in range [lr, hr]"""
        lr = cr.get("low_limit")
        hr = cr.get("high_limit")
        return [value for value in values if lr <= value <= hr]

    def get_lengths(sensors_values: list[list[float]]) -> list[int]:
        """ Return the lengths of the values accordingly
        Index of the list represents sensor id
        """
        return [len(values) for values in sensors_values]

    def convert_to_dataframe(orig_data_lens: list[int], cleaned_data_lens: list[int]) -> pd.DataFrame:
        """ The data as {"col_name": int or string}
        will be converted to dataframe in pandas
        """
        compressed_data = {}
        sensors      = [f"Sensor {i+1}" for i in range(len(orig_data_lens))]
        accuracies   = list(map(lambda x, y: round(x/y*100, 2), cleaned_data_lens, orig_data_lens))
        out_of_range = list(map(lambda x: round(100-x, 2), accuracies))
        total_values_removed = list(map(lambda x, y: x-y, orig_data_lens, cleaned_data_lens))
        """ Save results in dataframe """
        compressed_data["Sensor"] = sensors
        compressed_data["Accuracy (%)"] = accuracies
        compressed_data["Out of Range (%)"] = out_of_range
        compressed_data["Valid Values"] = cleaned_data_lens
        compressed_data["Invalid Values"] = total_values_removed
        compressed_data["Total Values"] = orig_data_lens
        return pd.DataFrame.from_dict(compressed_data)

    """ Show general statistics """
    sensor_columns = ["Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4"]  # name of the columns containing the values
    interested_characteristics = ["count", "mean", "min", "max", "std"]
    df_sensors = df[sensor_columns]
    df_sensors = df_sensors.describe()
    print(df_sensors.loc[interested_characteristics])
    print('\n')

    """ Show the percentage of valid values """
    data: list[list[float]] = compress_sensors_data(df, columns=sensor_columns)
    orig_data_lengths = get_lengths(sensors_values=data)
    cleaned_data = [filtered_list_from_errors(values) for values in data]
    cleaned_data_lengths = get_lengths(sensors_values=cleaned_data)
    df_stats = convert_to_dataframe(orig_data_lengths, cleaned_data_lengths)
    df_stats.to_csv(rename_csv_file(f"sensor_accuracy_data_{df.name}.csv"), index=False)


def find2_correlations(df: pd.DataFrame, col1: str, col2: str) -> None:
    def is_significant(corr_value: float, n: int) -> bool:
        """ Determines the significance of the correlation
        :param corr_value is correlation value
        :param n is sample size
        :returns true if p_values < 5%, otherwise false
        """
        p_value = 2 * (1 - abs(corr_value)) * (n - 2) / (n * (n - 2 - 1))  # based on pearson method
        if p_value < 0.05:
            return True
        return False

    corr = df[col1].corr(df[col2], method="pearson")
    sample_size = df[col1].shape[0]
    if corr > 0:
        print(f"Corr: {corr}\t"
              f"Positive relationship between '{col1}' and '{col2}'\t"
              f"Is significant: {is_significant(corr, n=sample_size)}")
    elif corr < 0:
        print(f"Corr: {corr}\t"
              f"Negative relationship between '{col1}' and '{col2}'\t"
              f"Is significant: {is_significant(corr, n=sample_size)}")
    else:
        print(f"Corr: {corr}\t"
              f"No relationship found between '{col1}' and '{col2}'\t"
              f"Is significant: {is_significant(corr, n=sample_size)}")
    if abs(corr) > 0.5:
        print("Strong correlation")
    else:
        print("Weak correlation")
    print("\n")


def find_group_description(df: pd.DataFrame, column_name: str) -> None:
    """ Describes the df according to the group common attribute
    :param df is dataframe containing column_name
    :param column_name indicates the column where to find the common attribute
    """
    sensor_cols = ["Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4"]
    interested_characteristics = ["count", "mean", "min", "max", "std"]
    groups = df.groupby(column_name)
    for group_name, data in groups:
        df_grouped: pd.DataFrame = groups.get_group(group_name)
        # describe sensor values per group
        stats = df_grouped[sensor_cols].describe()
        print(column_name, ": ", group_name)
        print(stats.loc[interested_characteristics])
        print("\n")

        # get correlations per group/posture
        interested_cols = cr.get("correlation_map_columns")
        note = column_name.split()[0]+f"_{str(group_name)}"
        show_corr_map(df_grouped[interested_cols], notes=note)


def visualize_clusters(df, label_col, title_note=None):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    x = df[cr.get("x")]
    y = df[cr.get("x")]
    z = df[cr.get("x")]
    labels = df[label_col]

    unique_labels = labels.unique()
    num_labels = len(unique_labels)

    colormap = plt.cm.get_cmap('viridis', num_labels)

    for i, label in enumerate(unique_labels):
        cluster_indices = labels == label
        color = colormap(i / (num_labels - 1))  # Normalize the index to [0, 1]
        ax.scatter(x[cluster_indices], y[cluster_indices], z[cluster_indices], color=color, label=label)

    ax.set_xlabel(cr.get("x"))
    ax.set_ylabel(cr.get("y"))
    ax.set_zlabel(cr.get("z"))

    ax.legend()
    # plt.show()
    if title_note is not None:
        title = f"Values Clustering ({label_col}, {title_note})"
    else:
        title = f"Values Clustering ({label_col})"
    plt.title(title)
    plt.savefig(rename_img_file(title))
    plt.close()


def show_corr_map(df: pd.DataFrame, notes=None) -> None:
    def formatted_columns(columns: list[str]) -> dict:
        result = {}
        max_length = len("Sensor X")
        for col in columns:
            if len(col) <= max_length:
                continue
            first_letters = [word[0].upper() for word in col.split()]
            new_col_name = ''.join(first_letters)
            result[col] = new_col_name.split('(')[0]  # exclude everything after (
        return result

    """ Show correlation map using seaborn """
    # new_cols = formatted_columns(df.columns)
    # df_copied = df.rename(columns=new_cols)
    correlation_matrix: pd.DataFrame = df.corr(method="pearson")
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
    title = "Corr Map"
    # plt.show()
    file_path = rename_img_file(title)
    if notes is not None:
        comment = f"({notes})"
        file_path += comment
        title += comment
    plt.title(title)
    plt.savefig(file_path)
    plt.close()
    correlation_matrix.to_csv(rename_csv_file(title+'.csv'))


def show_subplots(data: dict, title: str, columns_to_compress: list[str]) -> None:
    """ Represent data in different subplots
    :param data is list consisting of lists of any type of data,
    where key is a label and value is a list of values
    :param title represents the name of the group of values.
    """
    def get_boundaries(values: list[list[int]]) -> tuple:
        """ Get array of the hr and lr values to
        represent the boundaries lines for subplots
        The first array is lower boundary
        The second array is higher boundary
        """
        lr = cr.get("low_limit")  # lower range
        hr = cr.get("high_limit")  # higher range
        length = len(values[0])
        lb = np.full(length, lr)
        hb = np.full(length, hr)
        return lb, hb

    def modify_axe(axe, values_list: list[list[int]], subplot_title: str) -> None:
        for j, values in enumerate(values_list):
            axe.plot(values, label=columns_to_compress[j])
            axe.set_title(subplot_title)
        lb, hb = get_boundaries(values_list)
        axe.plot(lb, label="Lower Boundary", color="r", linestyle="--")
        axe.plot(hb, label="Higher Boundary", color="r", linestyle="--")
        axe.legend()
        axe.set_ylabel("Distance")
        axe.set_xlabel("Number of values")

    fig, axs = plt.subplots(nrows=len(data), figsize=(fig_width, fig_height))
    fig.suptitle(title)
    if len(data) > 1:
        for i, key in enumerate(data):
            # key represents posture name of head/shoulder/size etc
            modify_axe(axs[i], data[key], subplot_title=key)
    else:
        # since the dictionary consists of only one key, the value is:
        value = list(data.values())[0]
        key = list(data.keys())[0]
        modify_axe(axs, value, subplot_title=key)
    plt.tight_layout()
    # plt.show()
    """ Save image """
    fig.savefig(rename_img_file(title))
    plt.close()


def show_bar_chart(data, title: str) -> None:
    """ Show Bar Chart
    :param data = {"label", list[int]}
    :param title of the bar
    """
    categories = list(data.keys())
    counts = [len(data[category]) for category in categories]
    plt.bar(categories, counts)
    # Add accurate number per bar
    for i, count in enumerate(counts):
        plt.text(i, count, str(count), ha="center", va="top")

    # Calculate and display the total count
    total_count = sum(counts)
    plt.text(len(categories)/2, max(counts), f'Total: {total_count}', ha='center', va='bottom')
    plt.xlabel('Category')
    plt.ylabel('Count')
    plt.title(title)
    # plt.show()
    plt.savefig(rename_img_file(title))
    plt.close()
