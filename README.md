# Raspberry Pi Security Camera Setup Guide

## Prerequisites

### Hardware Requirements
- Raspberry Pi 4 (recommended) or Pi 3B+
- Raspberry Pi Camera Module or USB Camera
- MicroSD card (32GB recommended)
- Stable internet connection

### Software Requirements
- Raspberry Pi OS (latest version)
- Python 3.7+

## Installation Steps

### 1. Install Required Python Packages

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python packages
pip3 install opencv-python numpy requests picamera2

# Install additional system packages
sudo apt install python3-opencv python3-numpy -y
```

### 2. Enable Camera

```bash
# Enable camera interface
sudo raspi-config
# Navigate to Interface Options > Camera > Enable

# Reboot
sudo reboot
```

### 3. Create Project Directory

```bash
mkdir -p /home/pi/security_camera
cd /home/pi/security_camera

# Create directories
mkdir -p detections logs
```

### 4. Create Configuration File

Create a file named `config.json` in your project directory:

```json
{
    "monitoring_start": "18:00",
    "monitoring_end": "08:00",
    "alert_cooldown": 300,
    "detection_threshold": 0.5,
    "min_detection_area": 3000,
    "email": {
        "enabled": true,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "your_email@gmail.com",
        "sender_password": "your_app_password",
        "recipient_email": "alert@example.com"
    },
    "pushbullet": {
        "enabled": false,
        "api_key": "your_pushbullet_api_key"
    },
    "telegram": {
        "enabled": false,
        "bot_token": "your_bot_token",
        "chat_id": "your_chat_id"
    }
}
```

## Alert Setup Options

### Option 1: Email Alerts (Recommended)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security > 2-Step Verification > App passwords
   - Generate password for "Mail"
3. **Update config.json**:
   ```json
   "email": {
       "enabled": true,
       "smtp_server": "smtp.gmail.com",
       "smtp_port": 587,
       "sender_email": "youremail@gmail.com",
       "sender_password": "your_16_character_app_password",
       "recipient_email": "recipient@example.com"
   }
   ```

### Option 2: Pushbullet Notifications

1. **Create Pushbullet account** at pushbullet.com
2. **Get API key** from Account Settings
3. **Install Pushbullet app** on your phone
4. **Update config.json**:
   ```json
   "pushbullet": {
       "enabled": true,
       "api_key": "your_pushbullet_api_key"
   }
   ```

### Option 3: Telegram Bot

1. **Create Telegram bot**:
   - Message @BotFather on Telegram
   - Use `/newbot` command
   - Save the bot token
2. **Get Chat ID**:
   - Add bot to your chat
   - Send a message to the bot
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find your chat_id in the response
3. **Update config.json**:
   ```json
   "telegram": {
       "enabled": true,
       "bot_token": "your_bot_token",
       "chat_id": "your_chat_id"
   }
   ```

## Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `monitoring_start` | Start time for monitoring (24h format) | "18:00" |
| `monitoring_end` | End time for monitoring (24h format) | "08:00" |
| `alert_cooldown` | Minimum seconds between alerts | 300 |
| `detection_threshold` | Confidence threshold for human detection | 0.5 |
| `min_detection_area` | Minimum pixel area for valid detection | 3000 |

## Running the Script

### Manual Start
```bash
cd /home/pi/security_camera
python3 security_camera.py
```

### Auto-Start on Boot

1. **Create systemd service**:
```bash
sudo nano /etc/systemd/system/security-camera.service
```

2. **Add service configuration**:
```ini
[Unit]
Description=Security Camera Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/security_camera
ExecStart=/usr/bin/python3 /home/pi/security_camera/security_camera.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. **Enable and start service**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable security-camera.service
sudo systemctl start security-camera.service
```

4. **Check status**:
```bash
sudo systemctl status security-camera.service
```

## Troubleshooting

### Common Issues

1. **Camera not working**:
   ```bash
   # Test camera
   libcamera-hello --timeout 5000
   ```

2. **Permission errors**:
   ```bash
   # Add user to video group
   sudo usermod -a -G video pi
   ```

3. **Email authentication**:
   - Ensure 2FA is enabled
   - Use App Password, not regular password
   - Check "Less secure app access" if using regular password

4. **View logs**:
   ```bash
   # Real-time logs
   sudo journalctl -u security-camera.service -f
   
   # Application logs
   tail -f /home/pi/security_camera.log
   ```

### Performance Optimization

1. **Reduce resolution** for better performance:
   - Modify camera initialization in the script
   - Use 320x240 for faster processing

2. **Adjust detection frequency**:
   - Increase sleep time in main loop
   - Process every nth frame

3. **GPU acceleration** (if available):
   ```bash
   # Install OpenCV with GPU support
   pip3 install opencv-contrib-python
   ```

## Security Considerations

1. **Change default passwords**
2. **Use strong email app passwords**
3. **Secure your network**
4. **Regular updates**:
   ```bash
   sudo apt update && sudo apt upgrade
   ```

5. **Firewall configuration**:
   ```bash
   sudo ufw enable
   sudo ufw allow ssh
   ```

## Monitoring and Maintenance

- **Check disk space** regularly (detection images can accumulate)
- **Monitor logs** for errors
- **Test alerts** periodically
- **Backup configuration** files

## File Structure
```
/home/pi/security_camera/
├── security_camera.py    # Main script
├── config.json          # Configuration file
├── security_camera.log  # Application logs
└── detections/          # Detection images
    ├── detection_20241215_193045.jpg
    └── ...
```
