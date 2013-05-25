#!/usr/bin/python

# Copyright (c) 2010 Martin Abente Lahaye. - martin.abente.lahaye@gmail.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA

import socket
import struct
import sys
import time
import datetime


class Worldtime:

    TIME1970 = 2208988800L
    MAGIC_NUMBER = '\x1b' + 47 * '\0'
    NTP_SERVER = '3.north-america.pool.ntp.org'
    VERSION = 123
    SIZE = 1024
    OFFSET = '!12I'
    POSITION = 10

    @staticmethod
    def now():
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.sendto(Worldtime.MAGIC_NUMBER,
                     (Worldtime.NTP_SERVER,
                      Worldtime.VERSION))

        data, address = client.recvfrom(Worldtime.SIZE)
        if data:
            payload = struct.unpack(Worldtime.OFFSET, data)

            timestamp = payload[Worldtime.POSITION]
            timestamp -= Worldtime.TIME1970
            return str(datetime.datetime.utcfromtimestamp(timestamp))
        return None


def main():
    print Worldtime.now()

if __name__ == "__main__":
    main()
