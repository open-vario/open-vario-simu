# -*- coding: utf-8 -*-

'''

Copyright(c) 2017 Cedric Jimenez

This file is part of Open-Vario Simulator.

Open-Vario Simulator is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Open-Vario Simulator is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with Open-Vario Simulator.  If not, see <http://www.gnu.org/licenses/>.

'''


####################################################
#### Imports
import sys
from threading import Thread, RLock
from enum import Enum
from udp_socket import UdpSocket
from api.requests_pb2 import SimuRequest
from api.responses_pb2 import SimuResponse
from api.notifications_pb2 import SimuNotification


####################################################
#### Data types

class SimuProtocolState(Enum):
    '''
        Simulator protocol states
    '''
    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2

class SimuSensorType(Enum):
    '''
        Simulated sensor types
    '''
    UNKNOWN = 0
    PRESSURE = 1
    TEMPERATURE = 2
    ALTITUDE = 4
    GNSS = 8

class SimuSensorValueType(Enum):
    '''
        Simulated sensor value types
    '''
    UNKNOWN = 0
    UINT = 1
    INT = 2
    FLOAT = 3
    DOUBLE = 4
    STRING = 5
    BOOL = 6


####################################################
#### Classes


class SimuProtocol(object):
    '''
        Simulator protocol
    '''

    RESPONSE_FRAME = 'R'
    '''
        Response frame
    '''

    NOTIFICATION_FRAME = 'N'
    '''
        Notification frame
    '''

    def __init__(self, target_ip, target_port, host_port):
        '''
            Constructor

            @param target_ip: IP address of the Open Vario simulated instance
            @type target_ip: string
            @param target_port: Port of the Open Vario simulated instance
            @type target_port: int
            @param host_port: Port of the simulator
            @type host_port: int
        '''

        self.__target_ip = target_ip
        '''
            IP address of the Open Vario simulated instance
        '''
        self.__target_port = target_port
        '''
            Port of the Open Vario simulated instance
        '''
        self.__host_port = host_port
        '''
            Port of the simulator
        '''
        self.__socket = UdpSocket()
        '''
            UDP socket for communication with the Open Vario simulated instance
        '''
        self.__state = SimuProtocolState.DISCONNECTED
        '''
            Protocol state
        '''
        self.__listener = SimuProtocolListener()
        '''
            Protocol listener
        '''
        self.__awaited_response = None
        '''
            Current awaited response 
        '''
        self.__ping_number = 0
        '''
            Current ping number
        '''
        self.__timeout_counter = 0
        '''
            Current timeout counter value
        '''
        self.__lock = RLock()
        '''
            Lock
        '''

        return
        
    def connect(self, listener):
        '''
            Start the connection process to the Open Vario simulated instance

            @param listener: Listener to simulator events
            @type listener: SimuProtocolListener

            @return: True if the connection process is starting, False otherwise
            @rtype: bool
        '''
        
        self.__lock.acquire()

        # Check current state
        if ((self.__state == SimuProtocolState.DISCONNECTED) and 
            not (listener == None)):

            # Open and bind the UDP socket
            ret = self.__socket.open()
            if ret:
                ret = self.__socket.bind("", self.__host_port)
                if ret:

                    # Send the connect request
                    req = SimuRequest()
                    req.connect.SetInParent()
                    ret = self.__socket.send_to(self.__target_ip, self.__target_port, req.SerializeToString())
                    if ret:

                        # Start the receive thread
                        self.__listener = listener
                        self.__state = SimuProtocolState.CONNECTING
                        self.__timeout_counter = 0
                        self.__awaited_response = None
                        Thread(target=self.__rx_thread).start()

        else:
            ret = False

        self.__lock.release()
            
        return ret
    
    def close(self):
        '''
            Close the connection with the Open Vario simulated instance

            @return: True if the connection has been closed, False otherwise
            @rtype: bool
        '''
        
        self.__lock.acquire()

        # Check current state
        if not (self.__state == SimuProtocolState.DISCONNECTED):

            # Send the disconnect request
            req = SimuRequest()
            req.disconnect.SetInParent()
            ret = self.__socket.send_to(self.__target_ip, self.__target_port, req.SerializeToString())
            
            # Update state
            ret = False
            self.__state = SimuProtocolState.DISCONNECTED

            # Close socket
            ret = self.__socket.close() and ret

        else:
            ret = False

        self.__lock.release()

        return ret

    def get_sensors_list(self):
        '''
            Get the sensor list of the Open Vario simulated instance

            @return: True if the request has been sent, False otherwise
            @rtype: bool
        '''

        self.__lock.acquire()

        # Check current state
        if ((self.__state == SimuProtocolState.CONNECTED) and
            ((self.__awaited_response == None) or (self.__awaited_response == self.__handle_ping)) ):

            # Send the request
            req = SimuRequest()
            req.list_sensors.SetInParent()
            ret = self.__socket.send_to(self.__target_ip, self.__target_port, req.SerializeToString())
            if ret:
                self.__timeout_counter = 0
                self.__awaited_response = self.__handle_list_sensors

        else:
            ret = False

        self.__lock.release()

        return ret

    def update_sensor(self, id, value, value_type):
        '''
            Update a sensor value of the Open Vario simulated instance

            @param id: Id of the sensor
            @type id: int
            @param value: Value of the sensor
            @type value: int or float or bool or string
            @param value_type: Value type of the sensor
            @type value_type: SimuSensorValueType

            @return: True if the request has been sent, False otherwise
            @rtype: bool
        '''

        self.__lock.acquire()

        # Check current state
        if ((self.__state == SimuProtocolState.CONNECTED) and
            ((self.__awaited_response == None) or (self.__awaited_response == self.__handle_ping)) ):

            # Prepare the request
            ret = True
            req = SimuRequest()
            req.update_sensor.id = id
            if value_type == SimuSensorValueType.UINT:
                req.update_sensor.uint_value = int(value)
            elif value_type == SimuSensorValueType.INT:
                req.update_sensor.int_value = int(value)
            elif value_type == SimuSensorValueType.FLOAT:
                req.update_sensor.float_value = float(value)
            elif value_type == SimuSensorValueType.DOUBLE:
                req.update_sensor.double_value = float(value)
            elif value_type == SimuSensorValueType.STRING:
                req.update_sensor.string_value = str(value)
            elif value_type == SimuSensorValueType.BOOL:
                req.update_sensor.bool_value = bool(value)
            else:
                ret = False
            if ret:

                # Send the request
                ret = self.__socket.send_to(self.__target_ip, self.__target_port, req.SerializeToString())
                if ret:
                    self.__timeout_counter = 0
                    self.__awaited_response = self.__handle_update_sensor

        else:
            ret = False

        self.__lock.release()

        return ret

    def __rx_thread(self):
        '''
            Thread to receive data from the Open Vario simulated instance
        '''

        # Thread loop
        end = False
        while not end:

            # Wait for data
            ret = self.__socket.recv_from()

            self.__lock.acquire()

            if not (ret == None):

                # Extract data
                data = ret[0]
                
                # Try decoding data
                try:
                    if data[0] == self.RESPONSE_FRAME:
                        frame = SimuResponse()
                    elif data[0] == self.NOTIFICATION_FRAME:
                        frame = SimuNotification()
                    else:
                        pass

                    frame.ParseFromString(data[1:])
                except:
                    frame = None

                # Dispatch data
                if not (frame == None):
                    
                    if isinstance(frame, SimuResponse):

                        # Connection response
                        if self.__state == SimuProtocolState.CONNECTING:
                            if (frame.HasField("connect") and
                                frame.connect.accept):

                                # Connection success
                                self.__state = SimuProtocolState.CONNECTED

                                # Notify user 
                                self.__listener.on_connect(True)
                        else:
                            
                            # Handle response
                            if frame.HasField("disconnect"):

                                # Close connection
                                self.close()

                                # Notify user
                                self.__listener.on_close()
                                end = True

                            elif frame.HasField("list_sensors"):
                                if self.__awaited_response == self.__handle_list_sensors:
                                    self.__awaited_response = None
                                    self.__handle_list_sensors(False, frame.list_sensors)

                            elif frame.HasField("update_sensor"):
                                if self.__awaited_response == self.__handle_update_sensor:
                                    self.__awaited_response = None
                                    self.__handle_update_sensor(False, frame.update_sensor)

                            elif frame.HasField("ping"):
                                if self.__awaited_response == self.__handle_ping:
                                    self.__handle_ping(False, frame.ping)

                            else:
                                # Ignore frame
                                pass

            else:

                # Timeout or error
                self.__timeout_counter += 1

                # Check connection status
                if self.__state == SimuProtocolState.CONNECTING:
                    
                    # Check timeout
                    if self.__timeout_counter > 2:

                        # Connexion failed, close connection
                        self.close()

                        # Notify user
                        self.__listener.on_connect(False)
                        end = True

                else:

                    # Check timeout
                    if self.__timeout_counter > 2:

                        # Reset counter
                        self.__timeout_counter = 0

                        # Check if a response is awaited
                        if self.__awaited_response == None:

                            # Send a ping request
                            req = SimuRequest()
                            self.__ping_number += 1
                            req.ping.number = self.__ping_number
                            self.__socket.send_to(self.__target_ip, self.__target_port, req.SerializeToString())
                            self.__awaited_response = self.__handle_ping

                            print "Ping!"

                        else:

                            # Notify timeout
                            self.__awaited_response(True, None)
                            end = (self.__awaited_response == self.__handle_ping)
                            self.__awaited_response = None
                        

            self.__lock.release()

        return

    def __handle_list_sensors(self, timeout, list_sensors_response):
        '''
            Handle the list sensor response

            @param timeout: Indicates if a timeout occured
            @type timeout: bool
            @param list_sensors_response: List sensor response
            @type list_sensors_response: ListSensorsResponse
        '''

        # Check timeout
        if timeout:
            sensors = None

        else:
            # Extract sensor list
            sensors = []
            for sensor in list_sensors_response.sensors:
                sensors.append( (sensor.id, sensor.name, SimuSensorType(sensor.type), SimuSensorValueType(sensor.value_type)) )

        # Notify user
        self.__listener.on_sensors_list(sensors)

        return

    def __handle_update_sensor(self, timeout, update_sensor_response):
        '''
            Handle the update sensor response

            @param timeout: Indicates if a timeout occured
            @type timeout: bool
            @param update_sensor_response: Update sensor response
            @type update_sensor_response: UpdateSensorResponse
        '''

        # Check timeout
        if timeout:
            ret = None

        else:
            ret = update_sensor_response.success

        # Notify user
        self.__listener.on_update_sensor(ret)

        return

    def __handle_ping(self, timeout, ping_response):
        '''
            Handle the ping response

            @param timeout: Indicates if a timeout occured
            @type timeout: bool
            @param ping_response: Ping response
            @type ping_response: PingResponse
        '''

        # Check timeout
        if timeout:

            # Close connection
            self.close()

            # Notify user
            self.__listener.on_close()

        else:

            # Check expected ping number
            if (ping_response.number == self.__ping_number):
                self.__awaited_response = None
                print "Pong!"

        return


class SimuProtocolListener(object):
    '''
        Simulator protocol listener
    '''

    def on_connect(self, success):
        '''
            Called at the end of the connection process

            @param success: Indicates if the connection process has succeed
            @type success: bool
        '''
        return

    def on_close(self):
        '''
            Called when the connection has been closed
        '''
        return

    def on_sensors_list(self, sensors):
        '''
            Called at the end of the sensors list exchange

            @param sensors: List of sensors on success, None if no response received
            @type sensors: [ (int, string, SimuSensorType, SimuSensorValueType) ]
        '''
        return

    def on_update_sensor(self, success):
        '''
            Called at the end of the sensor update exchange

            @param success: Indicates if the sensor update has succeed, None if no response received
            @type success: bool
        '''
        return
