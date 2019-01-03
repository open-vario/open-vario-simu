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
from com.simu_protocol import SimuProtocol, SimuProtocolListener, SimuSensorValueType

####################################################
#### Data types


####################################################
#### Software entry point


class SimuApp(SimuProtocolListener):

    def start(self):
        '''
            Start the application
        '''

        self.__protocol = SimuProtocol("127.0.0.1", 45678, 45679)
        print "Connect..."
        self.__protocol.connect(self)

        temp_sensor_value = -200
        temp_sensor_step = 25

        baro_sensor_value = 100000
        baro_sensor_step = 50

        switch_sensor = True
        self.__update_sensors = False
        while True:
            time.sleep(0.25)
            if self.__update_sensors == True:
                self.__update_sensors = False

                if switch_sensor:
                    self.__protocol.update_sensor(3, baro_sensor_value, SimuSensorValueType.UINT)
                    baro_sensor_value += baro_sensor_step
                    if ((baro_sensor_value <= 90000) or (baro_sensor_value >= 102000)):
                        baro_sensor_step = -1 * baro_sensor_step
                else:
                    self.__protocol.update_sensor(2, temp_sensor_value, SimuSensorValueType.INT)
                    temp_sensor_value += temp_sensor_step
                    if ((temp_sensor_value < -400) or (temp_sensor_value >= 500)):
                        temp_sensor_step = -1 * temp_sensor_step

                switch_sensor = not switch_sensor

        return

    def on_connect(self, success):
        '''
            Called at the end of the connection process

            @param success: Indicates if the connection process has succeed
            @type success: bool
        '''

        if success:
            print "Success!"
            print "Get sensor list..."
            self.__protocol.get_sensors_list()
        else:
            print "Failed! Retry..."
            self.__protocol.connect(self)

        return

    def on_close(self):
        '''
            Called when the connection has been closed
        '''

        print "Connection closed!"

        return

    def on_sensors_list(self, sensors):
        '''
            Called at the end of the sensors list exchange

            @param sensors: List of sensors on success, None if no response received
            @type sensors: [ (int, string, SimuSensorType, SimuSensorValueType) ]
        '''

        if not (sensors == None):

            print "Sensor list :"
            for sensor in sensors:
                print " - " + str(sensor[0]) + " | " + sensor[1] + " | " + str(sensor[2]) + " | " + str(sensor[3])

            print "Update sensors"
            
            self.__update_sensors = True

        else:

            print "Failed! Retry...."
            self.__protocol.get_sensors_list()

        return

    def on_update_sensor(self, success):
        '''
            Called at the end of the sensor update exchange

            @param success: Indicates if the sensor update has succeed, None if no response received
            @type success: bool
        '''

        if not (success == None):

            if not success:
                print "Denied!"

        else:
            print "Failed!"

        self.__update_sensors = True

        return

    def on_value(self, notif_type, notif_values):
        '''
            Called when a value has been received

            @param notif_type: Indicates the type of the received values
            @type notif_type: string
            @param notif_values: Received values
            @type notif_values: {string:value}
        '''

        print "[" + notif_type + "] : " + str(notif_values)

        return


if  __name__ == '__main__':

    SimuApp().start()

       

