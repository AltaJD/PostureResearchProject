import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D

save_file_path = "data_storage/images/default.png"
fig_height = 10  # inches
fig_width = 20  # inches


def show_subplots(data: dict, title: str, columns_to_compress: list[str]) -> None:
    """ Represent data in different subplots
    :param data is list consisting of lists of any type of data.
    :param title represents the name of the group of values.
    """
    def modify_axe(axe, values_list: list[list[int]], subplot_title: str) -> None:
        for j, values in enumerate(values_list):
            axe.plot(values, label=columns_to_compress[j])
            axe.legend()
            axe.set_ylabel("Distance")
            axe.set_xlabel("Number of values")
            axe.set_title(subplot_title)

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
    global save_file_path
    file_path = save_file_path.replace("default.png", title)
    fig.savefig(file_path)
    plt.close()


def compress_sensors_data(df: pd.DataFrame, columns: list[str]) -> list[list[float]]:
    """ Return the list of the sensors values as list of list
    where index represents sensor number
    :returns [[650, 651, ...], [850, 851, ...], [650, 651, ...]]
    """
    result = []
    for col_name in columns:
        result.append(df[col_name].tolist())
    return result


def get_compressed_data(df: pd.DataFrame, group_column: str, columns_to_compress: list[str]) -> dict:
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
    def filtered_list(values: list[float]) -> list[float]:
        """ Return only the values in range [lr, hr]"""
        lr = 650
        hr = 900
        return [value for value in values if lr <= value <= hr]

    def get_lengths(sensors_values: list[list[float]]) -> list[int]:
        """ Return the lengths of the values accordingly
        Index of the list represents sensor id
        """
        return [len(values) for values in sensors_values]

    """ Show general statistics """
    sensor_columns = ["Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4"]  # name of the columns containing the values
    interested_characteristics = ["count", "mean", "min", "max"]
    df_sensors = df[sensor_columns]
    df_sensors = df_sensors.describe()
    print(df_sensors.loc[interested_characteristics])
    print('\n')

    """ Show the percentage of valid values """
    data: list[list[float]] = compress_sensors_data(df, columns=sensor_columns)
    orig_data_lengths = get_lengths(sensors_values=data)
    cleaned_data = [filtered_list(values) for values in data]
    cleaned_data_lengths = get_lengths(sensors_values=cleaned_data)
    sensor_id = 1
    total_values_valid = 0
    total_values_removed = 0
    for original_length, cleaned_length in zip(orig_data_lengths, cleaned_data_lengths):
        accuracy = round(cleaned_length/original_length*100, 2)
        print(f"Sensor {sensor_id} has accuracy {accuracy}%\t"
              f"Valid values: {cleaned_length}\t"
              f"Invalid values: {original_length-cleaned_length}\t"
              f"Total values: {original_length}")
        sensor_id += 1
        total_values_valid += cleaned_length
        total_values_removed += original_length - cleaned_length


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
    interested_characteristics = ["count", "mean", "min", "max"]
    groups = df.groupby(column_name)
    for group_name, data in groups:
        df_grouped: pd.DataFrame = groups.get_group(group_name)
        # describe sensor values per group
        stats = df_grouped[sensor_cols].describe()
        print(column_name, ": ", group_name)
        print(stats.loc[interested_characteristics])
        print("\n")


def visualize_clusters(df, label_col):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    x = df['Sensor 1']
    y = df['Sensor 2']
    z = df['Sensor 3']
    labels = df[label_col]

    unique_labels = labels.unique()
    num_labels = len(unique_labels)

    colormap = plt.cm.get_cmap('viridis', num_labels)

    for i, label in enumerate(unique_labels):
        cluster_indices = labels == label
        color = colormap(i / (num_labels - 1))  # Normalize the index to [0, 1]
        ax.scatter(x[cluster_indices], y[cluster_indices], z[cluster_indices], color=color, label=label)

    ax.set_xlabel('Sensor 1')
    ax.set_ylabel('Sensor 2')
    ax.set_zlabel('Sensor 3')

    ax.legend()
    # plt.show()
    title = f"Values Clustering ({label_col})"
    plt.title(title)
    global save_file_path
    file_path = save_file_path.replace("default.png", title)
    plt.savefig(file_path)
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
    new_cols = formatted_columns(df.columns)
    df_copied = df.rename(columns=new_cols)
    correlation_matrix: pd.DataFrame = df_copied.corr(method="pearson")
    print("Corr Matrix")
    print(df_copied)
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
    title = "Sensor Correlations Map"
    # plt.show()
    global save_file_path
    file_path = save_file_path.replace("default.png", title)
    if notes is not None:
        comment = f"({notes})"
        file_path += comment
        title += comment
    plt.title(title)
    plt.savefig(file_path)
    plt.close()
