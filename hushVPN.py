#!/usr/bin/env python

# External modules
from twisted.internet import reactor
import os

# Internal modules
from hush_writer import HushWriter
from tun_reader import TUNReader
from tun_writer import TUNWriter
from tunConfig import tunDevice
from nflog_reader import NFLogReader



def main():

    mtu = 1500
    mytun = tunDevice(remote_ip = '10.1.1.1',
                      local_ip  = '10.1.1.2',
                      netmask   = '255.255.255.0',
                      mtu       = mtu)

    mytun.up()
    # read packets from tun device and write it to HushWriter
    hushWriter  = HushWriter('10.1.1.1')
    tunReader   = TUNReader(mytun, mtu=mtu, handlePacket=hushWriter.addPacket)

    # receive packets from nflogReader and send to tunWriter
    tunWriter   = TUNWriter(mytun)
    nflogReader = NFLogReader(handlePacket=tunWriter.addPacket)


    reactor.run()


if __name__ == '__main__':
    main()

