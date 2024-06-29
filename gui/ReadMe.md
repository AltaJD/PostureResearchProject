# Sensor Monitoring Dashboard
This is a Tkinter-based application that allows users to monitor sensor data and detect potential alarms. The application provides a graphical user interface (GUI) where users can view real-time sensor data, detect anomalies, and manage user accounts.
![Simple GUI Overview](data/img/UI_Overview.png)
## Features
### 1. Show multiple lines on one graph with legends (DONE)
The application can display multiple sensor data streams on a single graph, with corresponding legends for easy identification.
### 2. Create alarm detection and show it on the graph (DONE)
The application can detect anomalies in the sensor data and display them on the graph.
### 3. Add time to determine processing time (DONE)
The application can measure the processing time for various operations, such as data retrieval and alarm detection.
### 4. Change position of the buttons and the graph (DONE)
The application allows users to customize the layout of the GUI, including the positioning of the buttons and the graph.
### 5. Create a simple database for storing user data (DONE)
The application uses a simple database to store user information, such as login credentials and sensor data.
### 6. Add data retrieve method (DONE)
The application provides a method to retrieve sensor data from the database.
### 7. Add sign-in/sign-out methods (DONE)
The application includes sign-in and sign-out functionality, allowing users to securely access their data.
### 8. Add background color of the alarm detected (DONE)
The application displays a distinctive background color when an alarm is detected on the graph.
### 9. Fix image display (DONE)
The application can now properly display images.
### 10. Improve the design (TODO)
The application's design can be further improved to enhance the user experience.
### 11. Add password encryption (DONE)
The application should encrypt user passwords for better security.
### 12. Code Refactoring (TODO)
The codebase can be refactored to improve readability, maintainability, and code organization.
### 13. User reports (DONE)
Add reports generating fuction, including: user used the device for (duration), alarm generated during (local time), etc. So that user can understand their postural behavior.
### 14. Data cleaning (Xijun is working on this)
Replace extream values with the last value. And add low-pass filter(if needed).
### 15. Alarm date and time recording (DONE)
Alarm generated at XX:XX AM/PM, dd-mm-yy. Lasted for XX mins. 
### 16. New Data Entry upon Registration (DONE)
The app requests and store more data, such as age, gender, weight, height, and shoulder size [XL, L, M, S, XS]
### 17. Pause monitoring (TODO)
User have the choice to Pause Monitoring for X mins.
### 18. Neutral and Extreme Posture Data collection (TODO, Xijun)
After a new user has created a profile, give Instruction: Please make two posture(1.round shoulder with extream poking chin, 2. normal shoulder with neck extention) at 3 different distances(65/70/80cm), one by one. User should stay still at each posture for at least 10s. Data will be used to culculate individual fleibility. 
### 19. General Setting (TODO)
1. User may be able to set how frequent they want to be notified. "I want to be notified if I maintained a bad posture for 3/5/10/X mins."
2. User can set if they want alarm sound or mute device. Sound enable:'!s1#', Sound disable:'!s0#'.
### 20. Model Tuning and Deployment （TODO, Xijun）
The next step will be to continue tuning the model and make deployment attempts. Areas of concern: computational intensive？ memory usage？
### 21.Interactive graph for error reporting （TODO, Xijun）
In the first phase, Xijun trained the model using data from static postures. In the second phase, we will test the correctness of the model in monitoring dynamic postures. Reporting wrong prediction of the model is a very important approach to check device accuracy, new data labeling and model retraining.
Add error reporting: Turn the real time image into an interactive image where the user can click on any point of time/time window on the x-axis. When that point of time (window) is clicked, the local time as well as the posture prediction class is recorded. Save all sensor data, predicted class, and actual class within this time window. The saved data is used to retrain the model. 
### 22. Dynamic posture data collection scenario. (TODO)
Provide users with instructions such as: slowly leaning forwards to the monitor, slowly leaning backwards from the monitor, slowly tilt the body to the left/right, slowly turn the head; and other tasks (typing, reading..) that mimic real-usage scenarios. Move the chair to a specified distance, and repeat the aforementioned actions.
### 23. Movement Classification (TODO) 
Apply a Hidden Markov Model or tangent slope to classify movements as relatively stationary, leaning forward, or leaning backward etc. Rapid and short-term changes in posture will not trigger an alarm. Only relative stationary bad postures will raise an alarm.
### 24. Memory Assessment (DONE)
Small computers such as Raspberry Pi has limited memory space. Therefore, assessment of the memory usage is essential over the testings and optimization processes.
### 25. Enhanced Graph Monitoring (DONE)
Allow the selection of the certain range using a scrollbar

## Installation and Usage
### 1. Clone the repository:
``` git clone https://github.com/AltaJD/PostureResearchProject/tree/master/gui```
### 2. Install the required dependencies:
```pip install -r requirements.txt```
### 3. Run the application:
```python main.py```
## Contributing
We welcome contributions to the project. If you find any issues or have ideas for improvements, please feel free to create a new issue or submit a pull request.
