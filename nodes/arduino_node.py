"""
arduino_node

Contains the ArduinoNode class
"""

import logging
import threading
import serial
from pubsub import pub
from ....node import Node

LOGGER = logging.getLogger(__name__)

NODE_CLASS_NAME = 'ArduinoNode'

class ArduinoNode(Node, threading.Thread):
    """
    ArduinoNode

    Acts as an interface to an arduino via serial port
    """

    def __init__(self, label, state, config=None):
        """
        Constructor
        """

        Node.__init__(self, label, state, config)
        threading.Thread.__init__(self, daemon=True)

        self.running_event = threading.Event()

        device = config['device']
        baud_rate = config['baud_rate']

        self.serial_com = serial.Serial(device, baud_rate)

        pub.subscribe(self.send, f'{self.label}.send')
        pub.subscribe(self.stop, f'{self.label}.stop')
        pub.subscribe(self.start, f'{self.label}.start')

        LOGGER.debug('Initialized')

    def update_state(self):
        """
        Gets the state of the node
        """

        LOGGER.info('Updating state')
        state = {'running' : not self.running_event.is_set()}
        self.state.update_states(self.label, **state)

    def stop(self):
        """
        Stops the node
        """

        LOGGER.info('Stopping')
        self.running_event.set()
        self.update_state()
        LOGGER.info('Stopped')

    def send(self, msg):
        """
        Handler for sending messages to the arduino
        """

        device_code = msg['device_code']
        device_id = msg['device_id']
        data = msg['data']
        write_data = f'{device_code}{device_id}{data}'
        self.serial_com.write(write_data.encode('UTF-8'))

    def run(self):
        """
        Run loop
        """

        while not self.running_event.is_set():
            serial_data = self.serial_com.readline().decode('UTF-8').strip('\n')
            LOGGER.info(f'Received data from arduino: {serial_data}')
            pub.sendMessage(f'messages.{self.label}', msg={
                'serial_data': serial_data
            })
