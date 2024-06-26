import threading
from app_ui import App
import time
import ui_config as uc
import random
import serial
import re
from posture_data_collection import PostureDataCollection
import wx
from serial_manager import SerialManager
class ThreadManager:
    """ The prototype consists of 2 TOF sensors and 1 image sensor,
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
        self.time_delay = uc.Measurements.thread_delay.value
        self.alarm_num = 0
        self.ser = None

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
        self.app.destroy()

    def connect(self, data=None) -> None:
        """ Connect to the COM port """
        # Add communication with COM port (DONE)
        try:
            ser = serial.Serial('COM8', 115200, timeout=1)
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            return
        while not self.app.is_stopped:
            if not self.app.is_paused:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').rstrip()
                    self.parse_data(line)
            time.sleep(self.time_delay)
        else:
            print("Data Parsing has been stopped")
            ser.close()

    def parse_data(self, data) -> None:
        """ Parse the sensor data """
        print(f"=== Data Received: {data} ===")
        match = re.match(r"Range, (\d+), (\d+), mm", data)
        if match:
            value1, value2 = map(int, match.groups())
            print(f"Parsed values: {value1}, {value2}")

            new_vals = self.app.sensor_values
            if "Sensor 2" not in new_vals:
                new_vals["Sensor 2"] = []
            if "Sensor 4" not in new_vals:
                new_vals["Sensor 4"] = []

            # Check for anomalies and replace with the previous value if over 1200
            if value1 >= 1200:
                if new_vals["Sensor 2"]:
                    value1 = new_vals["Sensor 2"][-1]
                else:
                    value1 = 600
            if value2 >= 1200:
                if new_vals["Sensor 4"]:
                    value2 = new_vals["Sensor 4"][-1]
                else:
                    value2 = 600

            new_vals["Sensor 2"].append(value1)
            new_vals["Sensor 4"].append(value2)

            self.app.update_sensor_values(new_vals)

    def send_command(self, command: str) -> None:
        """ Send a command to the device """
        if self.ser and self.ser.is_open:
            self.ser.write(command.encode())
            time.sleep(0.5)  # Wait for the command to be processed
            response = self.ser.readline().decode('utf-8').rstrip()
            print(f"Command: {command}, Response: {response}")
        else:
            print("Serial port did not get this command. Please debug.")

def main_test():
    app = wx.App(False)
    test_proc = ThreadManager(app_title="Testing Data Validation")
    sample_data = {"Sensor 2": [], "Sensor 4": []}
    test_proc.app.sensor_values = sample_data
    """ Add buttons """
    pause_graph_txt: str = uc.ElementNames.pause_button_txt.value
    close_app_txt: str = uc.ElementNames.close_button_txt.value
    save_txt: str = uc.ElementNames.save_data_button_txt.value
    sign_in_txt: str = uc.ElementNames.sign_in_button_txt.value
    register_txt: str = uc.ElementNames.register_button_txt.value

    num_alarms_label: str = uc.ElementNames.alarm_num_label.value
    proc_time_label: str = uc.ElementNames.processing_time_label.value

    app_ui = test_proc.app

    app_ui.add_control_button(text=pause_graph_txt, func=app_ui.pause)
    app_ui.add_control_button(text=close_app_txt, func=test_proc.close_app)
    app_ui.add_control_button(text=save_txt, func=app_ui.save_data)
    app_ui.add_menu_button(text=sign_in_txt, func=app_ui.show_sign_in_popup)
    app_ui.add_menu_button(text=register_txt, func=app_ui.show_register_popup)
    """ Add info panels """
    test_proc.app.create_alarms_label(num_alarms_label, str(0))
    test_proc.app.create_clock_label(proc_time_label)

    # Xijun is woking on:
    # frame = PostureDataCollection(None, title="Posture Data Collection")
    # frame.Show()

    test_proc.run()
    app.MainLoop()

if __name__ == '__main__':
    main_test()
