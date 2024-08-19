import cv2
from cvzone.PoseModule import PoseDetector
import pygame
import smtplib
from datetime import datetime
import time

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('en22167147@git-india.edu.in', 'Yashu@4115')

pygame.mixer.init()
pygame.mixer.music.load('D:\\pythonpro\\chor.mp3')  # Ensure the path to the sound file is correctly specified

detector = PoseDetector()
cap = cv2.VideoCapture(0)

motion_threshold = 10
modec = False
sp = False

while True:
    current_time = datetime.now()  # Get the current time
    start_time = current_time.replace(hour=23, minute=38, second=0, microsecond=0)  # Set start time to 12 AM today
    end_time = current_time.replace(hour=0,minute=0,second=0,microsecond=0)
    success, img = cap.read()
    cv2.imshow("Camera Output", img)

    # Activate pose detection only if current time is past 12 AM
    if current_time >= start_time and start_time >= end_time: 
        img = detector.findPose(img)
        lmlst, bbox = detector.findPosition(img)

        if len(lmlst) > motion_threshold:
            if not modec:
                pygame.mixer.music.play(-1)
                sp = True
                modec = True

                
                if modec:
                    time.sleep(2)
                    message = "Subject: Room Entry Alert\n\nSomeone has entered the room."
                    server.sendmail('en22167147@git-india.edu.in', 'en22163445@git-india.edu.in', message)
        else:
            if modec:
                pygame.mixer.music.stop()
                sp = False
                modec = False
    else:
        if modec:
            pygame.mixer.music.stop()
            sp = False
            modec = False

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
server.quit()
