# Sensor Logger for a Raspberry Pi

## Install sensor

The SHT45 breakout board supports I2C communication via a STEMMA QT
connector, which can be connected to the Raspberry Pi's SDA, SCL, 3V3,
and GND pins. Make sure to enable I2C within `raspi-config`.

If you don't want to run as root, set file permissions so that users
can access `/dev/i2c-1` and `/dev/i2c-2`.

## Collecting data

```
pip3 install -r requirements.txt
python3 run_sensor.py
```

By default, timestamped data will be saved in `logs`.

## Setup web server

Install nginx:
```
sudo apt update
sudo apt install nginx
```

Add the following within the `http` section of
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