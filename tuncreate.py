#!/usr/bin/env python

import pytun


def main():

    tunDevice = pytun.TunTapDevice(name='tun0')
    tunDevice.addr    = '10.1.1.1'
    tunDevice.dstaddr = '10.1.1.2'
    tunDevice.netmask = '255.255.255.0'
    tunDevice.mtu     = 1400
    tunDevice.up()
    tunDevice.persist(True)


if __name__ == '__main__':
    main()
