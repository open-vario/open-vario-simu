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
from com.simu_sync_protocol import SimuSyncProtocol, SimuSyncProtocolListener 

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
        self.__sync_protocol = SimuSyncProtocol(self.__protocol)

        while not self.__sync_protocol.is_connected():

            print "Connect..."
            while not self.__sync_protocol.connect(self):
                print "Failed! Retry..."

            print "Get sensor list..."
            sensors = None
            while (self.__sync_protocol.is_connected() and (sensors == None)):
                sensors = self.__sync_protocol.get_sensors_list()

            if self.__sync_protocol.is_connected():
                print "Sensor list :"
                for sensor in sensors:
                    print " - " + str(sensor[0]) + " | " + sensor[1] + " | " + str(sensor[2]) + " | " + str(sensor[3])

                print "Update sensors"

                temp_sensor_value = -200
                temp_sensor_step = 25

                baro_sensor_value = 100000
                baro_sensor_step = 50

                while self.__sync_protocol.is_connected():
                    time.sleep(0.25)
                    
                    ret = self.__sync_protocol.update_sensor(3, baro_sensor_value, SimuSensorValueType.UINT)
                    if not (ret == None):
                        if not ret:
                            print "Update failed"
                    else:
                        print "No response"
                        self.__sync_protocol.close()

                    baro_sensor_value += baro_sensor_step
                    if ((baro_sensor_value <= 90000) or (baro_sensor_value >= 102000)):
                        baro_sensor_step = -1 * baro_sensor_step

                    ret = self.__sync_protocol.update_sensor(2, temp_sensor_value, SimuSensorValueType.INT)
                    if not (ret == None):
                        if not ret:
                            print "Update failed"
                    else:
                        print "No response"
                        self.__sync_protocol.close()
                        
                    temp_sensor_value += temp_sensor_step
                    if ((temp_sensor_value < -400) or (temp_sensor_value >= 500)):
                        temp_sensor_step = -1 * temp_sensor_step

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

       

