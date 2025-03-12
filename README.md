# Sensor Logger for a Raspberry Pi

## Install sensor

The SHT45 sensor measures temperature and relative humidity. The
breakout board supports I2C communication via a STEMMA QT connector,
which can be connected to the Raspberry Pi's SDA, SCL, 3V3, and GND
pins. Make sure to enable I2C on the Raspberry Pi with `raspi-config`.

If you don't want to run as root, set file permissions so that users
can access `/dev/i2c-1` and `/dev/i2c-2`.

## Collect data

```
pip3 install -r requirements.txt
python3 run_sensor.py
```

By default the script will collect sensor data at 5 minute intervals
until 12pm. Timestamped data will be saved in `logs`.

### Automatically collect data

We can create a systemd service to automatically launch the data
script on boot and daily at 12pm.

Create a service file at `etc/systemd/system/sensor_logger.service`:
```
[Unit]
Description=Sensor logger
After=network.target

[Service]
User=my-username
WorkingDirectory=/path/to/sensor_logger/logs
ExecStart=/path/to/python3 /path/to/sensor_logger/run_sensor.py
Restart=always
RestartSec=300
StandardOutput=append:/path/to/sensor_logger/logs/systemd.log
StandardError=append:/path/to/sensor_logger/logs/systemd.log

[Install]
WantedBy=multi-user.target
```

Create a timer file at `etc/systemd/system/sensor_logger.timer`:
```
[Unit]
Description=Runs sensor_logger.service at 12 PM daily

[Timer]
OnCalendar=*-*-* 12:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Start the service:
```
# Start service
sudo systemctl start sensor_logger.service
sudo systemctl start sensor_logger.timer

# Start service on boot
sudo systemctl enable sensor_logger.service
sudo systemctl enable sensor_logger.timer
```

## Setup web server

Install nginx:
```
sudo apt update
sudo apt install nginx
```

Configure a web server within the `http` section of
`/etc/nginx/nginx.conf`:
```
server {
	listen	8080;
	listen	80;
	server_name	localhost;
	location / {
		root	/path/to/sensor_logger/www/html;
		index	index.html;
	}
}
```
Make sure to set file permissions so that the nginx user (`www-data`)
can access the data. Also comment out
`/etc/nginx/sites-available/default` so that the server can use the
default port (80).

Start the server:
```
sudo systemctl start nginx  # Start nginx
sudo systemctl enable nginx  # Start nginx on boot
```

Figure out the IP address:
```
hostname -I
```
Devices on the local network should be able to access the website
simply by navigating to the IP address in a web browser.