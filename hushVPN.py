#!/usr/bin/env python

from hush_writer import HushWriter
from tun_reader import TUNReader
from tun_writer import TUNWriter
from tunConfig import tunDevice
from nflog_reader import NFLogReader


def main():

    mytun = tunDevice(remote_ip = '10.1.1.1',
                      local_ip  = '10.1.1.2',
                      netmask   = '255.255.255.0',
                      mtu       = 1500)


    # read packets from tun device and write it to HushWriter
    hushWriter  = HushWriter('127.0.0.1')
    tunReader   = TUNReader(mytun.tun, handlePacket=hushWriter.addPacket)

    # receive packets from nflogReader and send to tunWriter
    tunWriter   = TUNWriter(mytun.tun)
    nflogReader = NFLogReader(handlePacket=tunWriter.addPacket)


    reactor.run()


if __name__ == '__main__':
    main()

