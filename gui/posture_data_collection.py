import tkinter as tk
from tkinter import messagebox
import time
import csv
from datetime import datetime
import serial
import re
from serial_manager import SerialManager


class PostureDataCollection(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Posture Data Collection")
        self.geometry("400x300")

        self.serial_manager = SerialManager()

        self.init_ui()

    def init_ui(self):
        self.instruction_text = tk.Label(self, text="Pos 1 for 3 sec：\n1. RS+PC\n2. NS+NE\nat（65/70/80cm）")
        self.instruction_text.pack(pady=15)

        self.start_button = tk.Button(self, text="Start collecting", command=self.on_start)
        self.start_button.pack(pady=15)

    def on_start(self):
        distances = [65, 70, 80]
        postures = ["RS+PC", "NS+NE"]
        data = []

        for posture in postures:
            for distance in distances:
                messagebox.showinfo("Reminder", f"Please stay still：{posture}，at distance：{distance}cm，for 3 sec。")
                time.sleep(3)
                readings = self.read_sensor_data()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for reading in readings:
                    data.append([timestamp, posture, distance, reading])

        self.save_data(data)
        messagebox.showinfo("Reminder", "Data collection done")

    def read_sensor_data(self):
        readings = []
        end_time = time.time() + 3
        while time.time() < end_time:
            line = self.serial_manager.read_line()
            if line:
                reading = self.parse_data(line)
                if reading is not None:
                    readings.append(reading)
        return readings

    def parse_data(self, data) -> float:
        match = re.match(r"Range, (\d+), mm", data)
        if match:
            value = int(match.group(1))
            return value
        return None

    def save_data(self, data):
        directory = 'C:\\Users\\icadmin\\PostureResearchProject\\gui\\data\\users\\'
        filename = directory + 'posture_data.csv'
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Only write the header if the file is empty
            if file.tell() == 0:
                writer.writerow(["Timestamp", "Posture", "Distance (cm)", "Sensor Reading"])
            for row in data:
                writer.writerow(row)


if __name__ == '__main__':
    app = PostureDataCollection()
    app.mainloop()
