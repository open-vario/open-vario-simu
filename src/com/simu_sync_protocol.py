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
import time
from com.simu_protocol import SimuProtocolListener 

####################################################
#### Data types



####################################################
#### Classes


class SimuSyncProtocol(SimuProtocolListener):
    '''
        Simulator synchronous protocol
    '''

    def __init__(self, simu_protocol):
        '''
            Constructor

            @param simu_protocol: Simulation protocol instance to use for communication
            @type simu_protocol: SimuProtocol
        '''

        self.__simu_protocol = simu_protocol
        '''
            Simulation protocol instance to use for communication
        '''

        self.__response_ready = False
        '''
            Indicates if a response if available
        '''

        self.__response = None
        '''
            Simulator's response
        '''

        self.__listener = None
        '''
            Listener
        '''

        self.__is_connected = False
        '''
            Indicate if the simulator protocol is closed
        '''

        return

    def is_connected(self):
        '''
            Indicate if the simulator protocol is connected

            @return: True if the simulator protocol is connected, False otherwise
            @rtype: bool
        '''

        return self.__is_connected
        
    def connect(self, listener):
        '''
            Start the connection process to the Open Vario simulated instance

            @param listener: Listener to simulator value notifications
            @type listener: SimuSyncProtocolListener

            @return: True if the connection process has succeeded, False otherwise
            @rtype: bool
        '''
        
        self.__listener = listener
        ret = self.__simu_protocol.connect(self)
        if ret:
            ret = self.__wait_response("connect")
            if ret:
                ret = self.__response

        return ret
    
    def close(self):
        '''
            Close the connection with the Open Vario simulated instance

            @return: True if the connection has been closed, False otherwise
            @rtype: bool
        '''
        
        self.__is_connected = False
        ret = self.__simu_protocol.close()
        return ret


    def get_sensors_list(self):
        '''
            Get the sensor list of the Open Vario simulated instance

            @return: List of sensors on success, None if no response received
            @rtype: [ (int, string, SimuSensorType, SimuSensorValueType) ]
        '''

        sensors = None
        ret = self.__simu_protocol.get_sensors_list()
        if ret:
            ret = self.__wait_response("get_sensors_list")
            if ret:
                sensors = self.__response
                
        return sensors

    def update_sensor(self, id, value, value_type):
        '''
            Update a sensor value of the Open Vario simulated instance

            @param id: Id of the sensor
            @type id: int
            @param value: Value of the sensor
            @type value: int or float or bool or string
            @param value_type: Value type of the sensor
            @type value_type: SimuSensorValueType

            @param success: Indicates if the sensor update has succeed, None if no response received
            @type success: bool
        '''
        
        update_succeed = None
        ret = self.__simu_protocol.update_sensor(id, value, value_type)
        if ret:
            ret = self.__wait_response("update_sensor")
            if ret:
                update_succeed = self.__response
                
        return update_succeed


    def on_connect(self, success):
        '''
            Called at the end of the connection process

            @param success: Indicates if the connection process has succeed
            @type success: bool
        '''

        if self.__response == "connect":
            self.__is_connected = success
            self.__response = success
            self.__response_ready = True

        return

    def on_close(self):
        '''
            Called when the connection has been closed
        '''
        self.__is_connected = False
        return

    def on_sensors_list(self, sensors):
        '''
            Called at the end of the sensors list exchange

            @param sensors: List of sensors on success, None if no response received
            @type sensors: [ (int, string, SimuSensorType, SimuSensorValueType) ]
        '''

        if self.__response == "get_sensors_list":
            self.__response = sensors
            self.__response_ready = True

        return

    def on_update_sensor(self, success):
        '''
            Called at the end of the sensor update exchange

            @param success: Indicates if the sensor update has succeed, None if no response received
            @type success: bool
        '''
        
        if self.__response == "update_sensor":
            self.__response = success
            self.__response_ready = True

        return

    def on_value(self, notif_type, notif_values):
        '''
            Called when a value has been received

            @param notif_type: Indicates the type of the received values
            @type notif_type: string
            @param notif_values: Received values
            @type notif_values: {string:value}
        '''
        self.__listener.on_value(notif_type, notif_values)
        return

    def __wait_response(self, response):
        '''
            Wait for a response from the simulator

            @param response: Expected response
            @type response: string

            @return: True if the response has been received, False otherwise
            @rtype: bool
        '''
        
        timeout = 0
        self.__response = response
        self.__response_ready = False
        while ((self.__response_ready == False) and (timeout != 1)):
            timeout += 0.1
            time.sleep(0.1)

        return self.__response_ready



class SimuSyncProtocolListener(object):
    '''
        Simulator synchronous protocol listener
    '''

    def on_value(self, notif_type, notif_values):
        '''
            Called when a value has been received

            @param notif_type: Indicates the type of the received values
            @type notif_type: string
            @param notif_values: Received values
            @type notif_values: {string:value}
        '''
        return
