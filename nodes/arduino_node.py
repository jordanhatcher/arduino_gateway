"""
arduino_node

Contains the ArduinoNode class
"""

import asyncio
import logging
import threading
import serial_asyncio
from pubsub import pub
from node import Node

LOGGER = logging.getLogger(__name__)

NODE_CLASS_NAME = 'ArduinoNode'

class ArduinoNode(Node):
    """
    ArduinoNode

    Acts as an interface to an arduino via serial port
    """

    def __init__(self, label, state, config=None):
        """
        Constructor
        """

        super().__init__(label, state, config)

        self._device = config['device']
        self._baud_rate = config['baud_rate']

        loop = asyncio.get_event_loop()
        self._reader, self._writer = loop.run_until_complete(self._init_reader_writer())
        loop.create_task(self.handler())

        pub.subscribe(self.send, f'{self.label}.send')
        LOGGER.info('Initialized')

    async def _init_reader_writer(self):
        """
        Helper function to get a pyserial asyncio reader/writer pair
        """

        return await serial_asyncio.open_serial_connection(url=self._device, baudrate=self._baud_rate)

    def send(self, msg):
        """
        Handler for sending messages to the arduino
        """

        device_code = msg['device_code']
        device_id = msg['device_id']
        data = msg['data']
        write_data = f'{device_code}{device_id}{data}'
        LOGGER.debug(f'Sending serial data: {write_data}')
        self._writer.write(write_data.encode('UTF-8'))

    async def handler(self):
        """
        Main loop
        """

        while True:
            serial_data = await self._reader.readline()
            msg = serial_data.decode('UTF-8').strip()
            LOGGER.info(f'Received data from serial port: {serial_data}')
            pub.sendMessage(f'messages.{self.label}', msg={
                'serial_data': serial_data
            })
