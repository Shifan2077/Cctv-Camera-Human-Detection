
# Room Entry Alert System

## Overview

This project is a Room Entry Alert System that uses a webcam to detect human motion based on body posture and sends an email alert when someone enters the room during a specified time range. Additionally, a sound alarm will play to notify the user of any detected motion.

## Features

- **Pose Detection:** The system uses OpenCV and the PoseDetector module from `cvzone` to detect human posture.
- **Real-Time Video Capture:** The webcam feed is continuously monitored for motion detection.
- **Email Alerts:** Upon detecting motion, an email alert is sent to a specified address.
- **Sound Alarm:** An alarm sound plays when motion is detected, alerting the user audibly.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.x
- OpenCV (`cv2`)
- cvzone (`PoseModule`)
- Pygame (`pygame`)
- smtplib (Standard Python library)
- A valid Gmail account for sending emails

## Installation

1. Clone or download the project files to your local machine.

2. Install the required Python libraries using pip:
   ```bash
   pip install opencv-python-headless cvzone pygame
   ```

3. Ensure you have a working webcam connected to your computer.

4. Replace the Gmail login credentials and the recipient email in the script with your own.

## Usage

1. **Set Up the Sound File:**
   - Ensure the alarm sound file (`chor.mp3`) is located in the correct directory specified in the script (`D:\\pythonpro\\chor.mp3`).
   - Update the file path in the script if the sound file is located in a different directory.

2. **Run the Script:**
   - Run the Python script to start the Room Entry Alert System:
   ```bash
   python room_entry_alert.py
   ```

3. **Monitor the System:**
   - The system will only activate the pose detection and email alert during the specified time window (from 11:38 PM to 12:00 AM). If motion is detected, the alarm will sound and an email will be sent.

4. **Stop the Script:**
   - Press the 'q' key to terminate the video feed and stop the script.

## Configuration

- **Time Settings:**
  - You can modify the `start_time` and `end_time` in the script to set your preferred time range for monitoring.

- **Email Settings:**
  - Ensure the Gmail account used for sending emails has "Less secure app access" enabled in the account settings.

## Important Notes

- This script uses the Gmail SMTP server for sending emails. Ensure that your Gmail account allows less secure apps to access the email service.

- The pose detection sensitivity can be adjusted by modifying the `motion_threshold` variable.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Acknowledgements

- The `cvzone` library for providing easy-to-use pose detection features.
- Python's `smtplib` for enabling email functionality.
- Pygame for providing sound playback capabilities.

## Troubleshooting

- **No video feed:** Ensure that your webcam is properly connected and recognized by the system.
- **Email not sent:** Double-check the Gmail credentials and ensure that "Less secure app access" is enabled.
- **No sound:** Verify the path to the sound file and check that your system's speakers are functioning correctly.
