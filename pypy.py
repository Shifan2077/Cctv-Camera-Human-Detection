#!/usr/bin/env python3
"""
Raspberry Pi Security Camera Script
Detects human figures during specified hours and sends mobile alerts
"""

import cv2
import numpy as np
import datetime
import time
import json
import os
import requests
from threading import Thread
import logging
from picamera2 import Picamera2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/pi/security_camera.log'),
        logging.StreamHandler()
    ]
)

class SecurityCamera:
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)
        self.camera = None
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.last_alert_time = 0
        self.alert_cooldown = self.config.get('alert_cooldown', 300)  # 5 minutes
        
        # Initialize camera
        self.init_camera()
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        default_config = {
            "monitoring_start": "18:00",  # 6 PM
            "monitoring_end": "08:00",    # 8 AM
            "alert_cooldown": 300,        # 5 minutes between alerts
            "detection_threshold": 0.5,
            "min_detection_area": 3000,
            "email": {
                "enabled": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "your_email@gmail.com",
                "sender_password": "your_app_password",
                "recipient_email": "alert@example.com"
            },
            "pushbullet": {
                "enabled": False,
                "api_key": "your_pushbullet_api_key"
            },
            "telegram": {
                "enabled": False,
                "bot_token": "your_bot_token",
                "chat_id": "your_chat_id"
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                logging.error(f"Error loading config: {e}")
                return default_config
        else:
            # Create default config file
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            logging.info(f"Created default config file: {config_file}")
            return default_config
    
    def init_camera(self):
        """Initialize the camera"""
        try:
            self.camera = Picamera2()
            config = self.camera.create_preview_configuration(
                main={"size": (640, 480)}
            )
            self.camera.configure(config)
            self.camera.start()
            time.sleep(2)  # Let camera warm up
            logging.info("Camera initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize camera: {e}")
            raise
    
    def is_monitoring_time(self):
        """Check if current time is within monitoring hours"""
        now = datetime.datetime.now().time()
        start_time = datetime.datetime.strptime(
            self.config['monitoring_start'], "%H:%M"
        ).time()
        end_time = datetime.datetime.strptime(
            self.config['monitoring_end'], "%H:%M"
        ).time()
        
        # Handle overnight monitoring (e.g., 18:00 to 08:00)
        if start_time > end_time:
            return now >= start_time or now <= end_time
        else:
            return start_time <= now <= end_time
    
    def detect_humans(self, frame):
        """Detect humans in the frame using HOG descriptor"""
        # Convert to grayscale for processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect people
        boxes, weights = self.hog.detectMultiScale(
            gray,
            winStride=(8, 8),
            padding=(32, 32),
            scale=1.05
        )
        
        # Filter detections based on confidence and size
        valid_detections = []
        for i, (x, y, w, h) in enumerate(boxes):
            if (weights[i] > self.config['detection_threshold'] and 
                w * h > self.config['min_detection_area']):
                valid_detections.append((x, y, w, h))
        
        return valid_detections
    
    def draw_detections(self, frame, detections):
        """Draw bounding boxes around detected humans"""
        for (x, y, w, h) in detections:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, 'Human', (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return frame
    
    def save_detection_image(self, frame, detections):
        """Save image with detections"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/home/pi/detections/detection_{timestamp}.jpg"
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Draw detections on frame
        annotated_frame = self.draw_detections(frame.copy(), detections)
        
        cv2.imwrite(filename, annotated_frame)
        logging.info(f"Detection image saved: {filename}")
        return filename
    
    def send_email_alert(self, image_path, detection_count):
        """Send email alert with detection image"""
        if not self.config['email']['enabled']:
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['sender_email']
            msg['To'] = self.config['email']['recipient_email']
            msg['Subject'] = f"Security Alert: {detection_count} Human(s) Detected"
            
            body = f"""
            Security Alert!
            
            Time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            Number of humans detected: {detection_count}
            
            Please check the attached image for details.
            
            Sent from Raspberry Pi Security Camera
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach image
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    img_data = f.read()
                    image = MIMEImage(img_data)
                    image.add_header('Content-Disposition', 
                                   f'attachment; filename="detection.jpg"')
                    msg.attach(image)
            
            # Send email
            server = smtplib.SMTP(self.config['email']['smtp_server'], 
                                self.config['email']['smtp_port'])
            server.starttls()
            server.login(self.config['email']['sender_email'], 
                        self.config['email']['sender_password'])
            server.send_message(msg)
            server.quit()
            
            logging.info("Email alert sent successfully")
            
        except Exception as e:
            logging.error(f"Failed to send email alert: {e}")
    
    def send_pushbullet_alert(self, detection_count):
        """Send Pushbullet notification"""
        if not self.config['pushbullet']['enabled']:
            return
        
        try:
            url = "https://api.pushbullet.com/v2/pushes"
            headers = {
                "Access-Token": self.config['pushbullet']['api_key'],
                "Content-Type": "application/json"
            }
            data = {
                "type": "note",
                "title": "Security Alert",
                "body": f"Human detection alert! {detection_count} person(s) detected at {datetime.datetime.now().strftime('%H:%M:%S')}"
            }
            
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                logging.info("Pushbullet notification sent successfully")
            else:
                logging.error(f"Pushbullet notification failed: {response.text}")
                
        except Exception as e:
            logging.error(f"Failed to send Pushbullet notification: {e}")
    
    def send_telegram_alert(self, detection_count):
        """Send Telegram notification"""
        if not self.config['telegram']['enabled']:
            return
        
        try:
            bot_token = self.config['telegram']['bot_token']
            chat_id = self.config['telegram']['chat_id']
            
            message = f"🚨 Security Alert!\n\n{detection_count} person(s) detected\nTime: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message
            }
            
            response = requests.post(url, data=data)
            if response.status_code == 200:
                logging.info("Telegram notification sent successfully")
            else:
                logging.error(f"Telegram notification failed: {response.text}")
                
        except Exception as e:
            logging.error(f"Failed to send Telegram notification: {e}")
    
    def send_alerts(self, image_path, detection_count):
        """Send all configured alerts"""
        current_time = time.time()
        
        # Check cooldown period
        if current_time - self.last_alert_time < self.alert_cooldown:
            logging.info("Alert cooldown active, skipping notification")
            return
        
        # Send alerts in separate threads to avoid blocking
        alert_threads = []
        
        if self.config['email']['enabled']:
            t = Thread(target=self.send_email_alert, args=(image_path, detection_count))
            alert_threads.append(t)
        
        if self.config['pushbullet']['enabled']:
            t = Thread(target=self.send_pushbullet_alert, args=(detection_count,))
            alert_threads.append(t)
        
        if self.config['telegram']['enabled']:
            t = Thread(target=self.send_telegram_alert, args=(detection_count,))
            alert_threads.append(t)
        
        # Start all alert threads
        for thread in alert_threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in alert_threads:
            thread.join()
        
        self.last_alert_time = current_time
        logging.info(f"All alerts sent for {detection_count} detection(s)")
    
    def run(self):
        """Main monitoring loop"""
        logging.info("Starting security camera monitoring...")
        
        try:
            while True:
                if not self.is_monitoring_time():
                    time.sleep(60)  # Check every minute
                    continue
                
                # Capture frame
                frame = self.camera.capture_array()
                
                # Detect humans
                detections = self.detect_humans(frame)
                
                if detections:
                    logging.info(f"Human detection: {len(detections)} person(s) detected")
                    
                    # Save detection image
                    image_path = self.save_detection_image(frame, detections)
                    
                    # Send alerts
                    self.send_alerts(image_path, len(detections))
                
                # Small delay to prevent excessive CPU usage
                time.sleep(1)
                
        except KeyboardInterrupt:
            logging.info("Monitoring stopped by user")
        
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
        
        finally:
            if self.camera:
                self.camera.stop()
            logging.info("Camera stopped")

def main():
    try:
        # Create security camera instance
        security_cam = SecurityCamera()
        
        # Start monitoring
        security_cam.run()
        
    except Exception as e:
        logging.error(f"Failed to start security camera: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
