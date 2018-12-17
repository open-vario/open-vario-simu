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
import socket


####################################################
#### Data types


####################################################
#### Classes


class UdpSocket(object):
    '''
        UDP socket
    '''

    def __init__(self):
        '''
            Constructor
        '''

        self.__timeout = 0.5
        ''' Socket timeout in seconds '''

        self.__socket = None
        ''' Socket object '''

        return
        
    def set_timeout(self, timeout):
        '''
            Set the socket timeout

            @param timeout: timeout value in seconds
            @type timeout: int
        '''

        self.__timeout = timeout
        if( self.__socket != None ):
            self.__socket.settimeout(self.__timeout)

        return
        
    def get_timeout(self):
        '''
            Get the socket timeout

            @return: timeout value in seconds
            @rtype: int
        '''

        return self.__timeout

    def open(self):
        '''
            Open the socket

            @return: True if the socket is opened, False otherwise
            @rtype: bool
        '''
        
        ret = False
        if( self.__socket == None ):
            
            try:
                self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.__socket.settimeout(self.__timeout)
                ret = True
            except:
                pass
            
        return ret
    
    def close(self):
        '''
            Close the socket

            @return: True if the socket is closed, False otherwise
            @rtype: bool
        '''
        
        ret = False
        if( self.__socket != None ):
            
            try:
                self.__socket.close()
                self.__socket = None
                ret = True
            except:
                pass
            
        return ret

    def bind(self, ip_address, port):
        '''
            Bind the socket to specific IP address/port 
            
            @param ip_address: IP address
            @type ip_address: string
            @param port: Port
            @type port: int

            @return: True if the socket is bound, False otherwise
            @rtype: bool
        '''
        
        ret = False
        if( self.__socket != None ):
            
            try:
                self.__socket.bind((ip_address, port))
                ret = True
            except:
                pass
            
        return ret
    
    def send_to(self, ip_address, port, data):
        '''
            Send data through the socket 
            
            @param ip_address: Destination IP address
            @type ip_address: string
            @param port: Destination port
            @type port: int
            @param data: Data to send
            @type data: string

            @return: True if the data has been sent, False otherwise
            @rtype: bool
        '''
        
        ret = False
        if( self.__socket != None ):
            
            try:
                self.__socket.sendto(data, (ip_address, port))
                ret = True
            except:
                pass
            
        return ret
    
        
    def recv_from(self):
        '''
            Receive data from the socket 
            
            @return None if no data is available, data and IP address otherwise
            @rtype A tuple (data, (ip_address, port) with data as a string
        '''
        
        ret = None
        if( self.__socket != None ):
            
            try:
                data, addr = self.__socket.recvfrom(65535)
                ret = (data, addr)
            except:
                ret = None
            
        return ret
