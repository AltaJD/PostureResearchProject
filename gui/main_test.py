""" File imitates the communication with the sensors
and used for remote testing of new UI features
"""

import threading
from app_ui import App
import time
import ui_config as uc
import random
import psutil


class ThreadManager:
    """ The prototype consists of 2-4 sensors,
    based on their data, we create the graph in one subplot to show
    Procedure: read and store data
    """
    app: App
    alarm_num: int
    time_delay: float
    reading_thread: threading.Thread

    def __init__(self, app_title: str):
        self.process = psutil.Process()
        self.app = App(title=app_title)
        self.reading_thread = threading.Thread(target=self.connect, daemon=True)
        self.time_delay = uc.Measurements.thread_delay.value
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
        time.sleep(0.1)
        self.check_memory_usage()
        self.app.destroy()

    def connect(self, data=None) -> None:
        """ Connect to the COM port """
        # TODO: Add communication with COM port
        while not self.app.is_stopped:
            if not self.app.is_paused:
                self.parse_data(data)
            time.sleep(self.time_delay)
        else:
            print("Data Parsing has been stopped")

    def parse_data(self, data) -> None:
        # print("=== Data Parsed ===")
        # remove everything lower
        new_vals = self.app.sensor_values
        # increase values by one
        if new_vals:
            for key, value in new_vals.items():
                some_value: int = random.randint(-30, 30)
                value.append(some_value)
            self.app.update_sensor_values(new_vals)

    def check_memory_usage(self):
        memory_info = self.process.memory_info()
        print(f"Memory usage: {memory_info.rss / (1024 ** 2):.2f} MB (resident set size)")
        print(f"Memory usage: {memory_info.vms / (1024 ** 2):.2f} MB (virtual memory size)")


def main_test():
    test_proc = ThreadManager(app_title="Testing Data Validation")
    sample_data = {"Sensor 2": [],
                   "Sensor 4": [],
                   }
    test_proc.app.sensor_values = sample_data
    """ Add buttons """
    pause_graph_txt: str = uc.ElementNames.pause_button_txt.value
    close_app_txt: str = uc.ElementNames.close_button_txt.value
    save_txt: str = uc.ElementNames.save_data_button_txt.value
    sign_in_txt: str = uc.ElementNames.sign_in_button_txt.value
    register_txt: str = uc.ElementNames.register_button_txt.value
    add_notes_txt: str = uc.ElementNames.save_selected_button_txt.value

    num_alarms_label: str = uc.ElementNames.alarm_num_label.value
    proc_time_label: str = uc.ElementNames.processing_time_label.value

    app_ui = test_proc.app

    app_ui.add_control_button(text=pause_graph_txt, func=app_ui.pause)
    app_ui.add_control_button(text=close_app_txt, func=test_proc.close_app)
    app_ui.add_control_button(text=save_txt, func=app_ui.save_data)
    app_ui.add_control_button(text=add_notes_txt, func=app_ui.show_notes_entry)
    app_ui.add_menu_button(text=sign_in_txt, func=app_ui.show_sign_in_popup)
    app_ui.add_menu_button(text=register_txt, func=app_ui.show_register_popup)
    """ Add info panels """
    test_proc.app.create_alarms_label(num_alarms_label, str(0))
    test_proc.app.create_clock_label(proc_time_label)

    test_proc.run()


if __name__ == '__main__':
    main_test()
