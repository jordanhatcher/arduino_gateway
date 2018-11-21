# Arduino Gateway

This is a package for my automation system that provides a serial port interface to an arduino.

# Setup

This package depends on having access to the USB device for the arduino. If running in a docker
container, add the device to the docker-compose.yml file:

```yaml
services:
  #Service for the actual automation system
  automation:
    image: automation
    devices:
      - /dev/ttyUSB0:/dev/ttyUSB0
...
```

To install this package, clone this repo in the packages directory for the
automation system. In the config.yml file, add the following under nodes:

```yaml
arduino_node:
  node_type: arduino_gateway.arduino_node
  config:
    device: /dev/ttyUSB0
    baud_rate: 9600
```
