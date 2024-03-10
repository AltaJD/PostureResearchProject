import pandas as pd
import data_cleaner
import matplotlib.pyplot as plt


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
            axs[i].plot(value, label=f"Sensor {j}")
            axs[i].legend()
            axs[i].set_ylabel("Distance")
            axs[i].set_xlabel("Number of values")
        axs[i].set_title(key)
    plt.tight_layout()
    plt.show()


def compress_sensors_data(df: pd.DataFrame) -> list[list[float]]:
    sensor1_data = df["Sensor 1"].tolist()
    sensor2_data = df["Sensor 2"].tolist()
    sensor3_data = df["Sensor 3"].tolist()
    return [sensor1_data, sensor2_data, sensor3_data]


def get_compressed_data(df: pd.DataFrame, group_column: str) -> dict:
    """ Returns the data in the format:
    {"Posture Name": [float1, float2, ...]}
    """
    result = {}
    grouped_df = df.groupby(group_column)
    for group_name, data_frame in grouped_df:
        # print(str(group_name))
        grouped_values = grouped_df.get_group(group_name)
        result[str(group_name)] = compress_sensors_data(grouped_values)
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

    data: list[list[float]] = compress_sensors_data(df_original)
    orig_data_lengths = get_lengths(sensors_values=data)
    cleaned_data = [filtered_list(values) for values in data]
    cleaned_data_lengths = get_lengths(sensors_values=cleaned_data)
    sensor_id = 1
    # Show the percentage of valid values
    for original_length, cleaned_length in zip(orig_data_lengths, cleaned_data_lengths):
        accuracy = round(cleaned_length/original_length*100, 2)
        print(f"Sensor {sensor_id} has accuracy {accuracy}%")
        sensor_id += 1


if __name__ == '__main__':
    """ Extract and clean data  """
    file = "posture_data.csv"
    df = pd.read_csv(file, delimiter=",")
    data_cleaner.strip_columns(df)
    describe_sensors_values(df)
    df = data_cleaner.exclude_errors(df)

    """ Process data """
    head_data = get_compressed_data(df, group_column="Head Posture")
    shoulder_data = get_compressed_data(df, group_column="Shoulder Posture")

    show_subplots(data=head_data, title="Head Positions")
    show_subplots(data=shoulder_data, title="Shoulder positions")
