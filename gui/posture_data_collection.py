import wx
import time
import csv
from datetime import datetime
import serial
import re
from serial_manager import SerialManager
# Xijun is still debugging this file
class PostureDataCollection(wx.Frame):
    def __init__(self, parent, title):
        super(PostureDataCollection, self).__init__(parent, title=title, size=(400, 300))

        self.InitUI()
        self.Centre()
        self.Show()


        self.serial_manager = SerialManager()

    def InitUI(self):
        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.instruction_text = wx.StaticText(panel, label="Pos 1 for 3 sec：\n"
                                                           "1. RS+PC\n"
                                                           "2. NS+NE\n"
                                                           "at（65/70/80cm）")
        vbox.Add(self.instruction_text, flag=wx.ALL | wx.EXPAND, border=15)

        self.start_button = wx.Button(panel, label="Start collecting")
        self.start_button.Bind(wx.EVT_BUTTON, self.OnStart)
        vbox.Add(self.start_button, flag=wx.ALL | wx.CENTER, border=15)

        panel.SetSizer(vbox)

    def OnStart(self, event):
        distances = [65, 70, 80]
        postures = ["RS+PC", "NS+NE"]
        data = []

        for posture in postures:
            for distance in distances:
                wx.MessageBox(f"Please stay still：{posture}，at distance：{distance}cm，for 3 sec。", "Reminder",
                              wx.OK | wx.ICON_INFORMATION)
                time.sleep(3)
                readings = self.read_sensor_data()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for reading in readings:
                    data.append([timestamp, posture, distance, reading])

        self.save_data(data)
        wx.MessageBox("Data collection done", "Reminder", wx.OK | wx.ICON_INFORMATION)

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
    app = wx.App(False)
    frame = PostureDataCollection(None, title="Posture Data Collection")
    app.MainLoop()
