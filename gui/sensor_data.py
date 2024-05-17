import threading
from app import App
import time


class DataProcessor:
    """ The prototype consists of 2-4 sensors,
    based on their data, we create the graph in one subplot to show
    Procedure: read and store data
    """
    app: App
    alarm_num: int
    time_delay: float
    reading_thread: threading.Thread

    def __init__(self, app_title: str):
        self.app = App(title=app_title)
        self.reading_thread = threading.Thread(target=self.connect, daemon=True)
        self.time_delay = 0.5
        self.alarm_num = 0

    def run(self):
        self.start_thread()
        self.app.run_app()

    def start_thread(self):
        self.reading_thread.start()

    def stop_thread(self):
        self.app.is_stopped = True
        if self.reading_thread.is_alive():
            self.reading_thread.join()

    def interrupt(self):
        self.app.is_stopped = True

    def close_app(self):
        self.interrupt()
        self.app.destroy()

    def connect(self, data=None) -> None:
        """ Connect to the COM port """
        # TODO: Add communication with COM port
        while not self.app.is_stopped:
            self.parse_data(data)
            time.sleep(0.5)
        else:
            print("Data Parsing has been stopped")

    def parse_data(self, data) -> None:
        # TODO: implement function
        print("Sensor Data Has been parsed")
        self.alarm_num += 1
        self.app.update_alarm_num(num=self.alarm_num)
        # remove everything lower
        new_vals = self.app.sensor_values
        # increase values by one
        if new_vals:
            for key, value in new_vals.items():
                value.append(value[-1])
            self.app.update_sensor_values(new_vals)


def main_test():
    test_proc = DataProcessor(app_title="Testing Data Validation")
    sample_data = {"Sensor 1": [2, 4, 6, 8, 10],
                   "Sensor 2": [1, 2, 3, 4, 5],
                   "Sensor 3": [5, 6, 3, 6, 7]
                   }
    test_proc.app.sensor_values = sample_data
    # Add elements
    test_proc.app.add_button(text="Stop Graph", func=test_proc.interrupt)
    test_proc.app.add_button(text="Close APP", func=test_proc.close_app)
    test_proc.app.add_alarms_label("Number of Alarms", str(0))
    test_proc.run()


if __name__ == '__main__':
    main_test()
