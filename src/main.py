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

        self.__protocol = SimuProtocol("127.0.0.1", 45678,45678)
        print "Connect..."
        self.__protocol.connect(self)

        while True:
            time.sleep(1)

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

            print "Update sensor"
            self.__protocol.update_sensor(5, 53.2, SimuSensorValueType.FLOAT)

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

            if success:
                print "Success!"
            else:
                print "Denied!"

        else:
            print "Failed!"

        return


if  __name__ == '__main__':

    SimuApp().start()

       

