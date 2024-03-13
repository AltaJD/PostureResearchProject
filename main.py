import pandas as pd
import data_cleaner
import matplotlib.pyplot as plt

columns_to_compress = ["Sensor 2", "Sensor 1", "Sensor 3"]


def show_subplots(data: dict, title: str) -> None:
    """ Represent data in different subplots
    :param data is list consisting of lists of any type of data.
    :param title represents the name of the group of values.
    """
    fig, axs = plt.subplots(nrows=len(data))
    fig.suptitle(title)
    for i, key in enumerate(data):
        # key represents posture name of head/shoulder
        values: list[list] = data[key]
        for j, value in enumerate(values):
            # print("Sensor ", j, value)
            axs[i].plot(value, label=columns_to_compress[j])
            axs[i].legend()
            axs[i].set_ylabel("Distance")
            axs[i].set_xlabel("Number of values")
        axs[i].set_title(key)
    plt.tight_layout()
    plt.show()


def compress_sensors_data(df: pd.DataFrame, columns: list[str]) -> list[list[float]]:
    result = []
    for col_name in columns:
        result.append(df[col_name].tolist())
    return result


def get_compressed_data(df: pd.DataFrame, group_column: str) -> dict:
    """ Returns the data in the format:
    {"Posture Name": [float1, float2, ...]}
    """
    result = {}
    grouped_df = df.groupby(group_column)
    for group_name, data_frame in grouped_df:
        # print(str(group_name))
        grouped_values = grouped_df.get_group(group_name)
        result[str(group_name)] = compress_sensors_data(grouped_values, columns=columns_to_compress)
    return result


def describe_sensors_values(df_original: pd.DataFrame) -> None:
    """ Shows the percentage of valid values over all received values
    Assumption: error values are considered to be outside of range [lr, hr]
    Formula: valid_values/all_values*100 rounded to 2 digits after comma
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

    data: list[list[float]] = compress_sensors_data(df_original, columns=["Sensor 1", "Sensor 2", "Sensor 3"])
    orig_data_lengths = get_lengths(sensors_values=data)
    cleaned_data = [filtered_list(values) for values in data]
    cleaned_data_lengths = get_lengths(sensors_values=cleaned_data)
    sensor_id = 1
    # Show the percentage of valid values
    for original_length, cleaned_length in zip(orig_data_lengths, cleaned_data_lengths):
        accuracy = round(cleaned_length/original_length*100, 2)
        print(f"Sensor {sensor_id} has accuracy {accuracy}%\t"
              f"Valid values: {cleaned_length}\t"
              f"Invalid values: {original_length-cleaned_length}\t"
              f"Total values: {original_length}")
        sensor_id += 1


def find_correlations(df: pd.DataFrame, col1: str, col2: str) -> None:
    def is_significant(corr: float, n: int) -> bool:
        """ Determines the significance of the correlation
        :param corr is correlation value
        :param n is sample size
        :returns true if p_values < 5%, otherwise false
        """
        p_value = 2 * (1 - abs(corr)) * (n - 2) / (n * (n - 2 - 1))  # based on pearson method
        if p_value < 0.05:
            return True
        return False

    corr = df[col1].corr(df[col2], method="pearson")
    sample_size = df[col1].shape[0]
    if corr > 0:
        print(f"Corr: {corr}\t"
              f"Positive relationship between {col1} and {col2}\t"
              f"Is significant: {is_significant(corr, n=sample_size)}")
    elif corr < 0:
        print(f"Corr: {corr}\t"
              f"Negative relationship between {col1} and {col2}\t"
              f"Is significant: {is_significant(corr, n=sample_size)}")
    else:
        print(f"Corr: {corr}\t"
              f"No relationship found between {col1} and {col2}\t"
              f"Is significant: {is_significant(corr, n=sample_size)}")


if __name__ == '__main__':
    """ Extract and clean data  """
    file = "posture_data.csv"
    df = pd.read_csv(file, delimiter=",")
    data_cleaner.strip_columns(df)
    describe_sensors_values(df)
    df = data_cleaner.exclude_errors(df)

    """ Process data """
    df["Sensor 2-3"] = df["Sensor 2"] - df["Sensor 3"]
    df["Sensor 2-1"] = df["Sensor 2"] - df["Sensor 1"]

    find_correlations(df, col1="Sensor 2", col2="Sensor 1")
    find_correlations(df, col1="Sensor 2", col2="Sensor 3")

    # head_data = get_compressed_data(df, group_column="Head Posture")
    # shoulder_data = get_compressed_data(df, group_column="Shoulder Posture")
    #
    # show_subplots(data=head_data, title="Head Positions")
    # show_subplots(data=shoulder_data, title="Shoulder positions")

    # size_data = get_compressed_data(df, group_column="Size")
    # show_subplots(data=size_data, title="Size vs Sensors")

