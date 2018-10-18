#!/usr/bin/python3

import serial
import logging


def parseResponse(bts: bytes, dict=dict):
    res = dict()
    res['datasize'] = int(bts[1])
    res['packetNum'] = int(bts[2]) * 8 + int(bts[3])
    res['status'] = int(bts[4])
    res['data'] = bts[5:-1]
    res['checksum'] = int(bts[-1])
    return res


def make_packet(**dct):
    if 'data' not in dct:
        dct['data'] = []
    if 'datasize' not in dct:
        dct['datasize'] = len(dct['data'])
    if 'checksum' not in dct:
        dct['checksum'] = sum(dct['data']) & 0xff
    return (bytes([0xff, dct['datasize'],
                   dct['packetNum'] >> 8 & 0xff,
                   dct['packetNum'] & 0xff,
                   dct['command'] >> 8 & 0xff,
                   dct['command'] & 0xff]) +
            dct['data'] +
            bytes([dct['checksum']]))


class LinxConnection(serial.Serial):
    xmethods = {'sync': {'no': 0x0000,
                         'bts_num': 0},
                'getDeviceId': {'no': 0x0003,
                                'bts_num': 0},
                'getLinxApiV': {'no': 0x0004,
                                'bts_num': 0},
                'getUartMaxBaud': {'no': 0x0005,
                                   'bts_num': 0},
                'setUartMaxBaud': {'no': 0x0006,
                                   'bts_num': 0}}

    def __init__(self, **kwargs):
        self.packetNum = 0
        serial_kwargs = dict(port='COM3')
        serial_kwargs.update(kwargs)
        serial.Serial.__init__(self, **serial_kwargs)

    def recv_raw(self):
        packet = self.read(2)
        packet += self.read(int(packet[1]) - 2)
        return packet

    def recv(self, dict=dict):
        return parseResponse(self.recv_raw(), dict)

    def send_raw(self, packet: bytes):
        self.write(packet)
        return len(packet)

    def send(self, **kwargs):
        return self.send_raw(make_packet(**kwargs))

    def send_cmd(self, cmd: str, *args):
        if len(args) == 1 and type(args[0]) == bytes:
            res = self.send(command=LinxConnection.xmethods[cmd],
                            data=args[0])
        else:
            res = self.send(command=LinxConnection.xmethods[cmd],
                            data=bytes(args))
        self.packetNum += 1
        return res


def make_method(method: str, no: int, bts_num: int):
    def inner(self, *args):
        nonlocal method, no, bts_num
        data = bytes(args)
        if len(data) != bts_num:
            logging.warn('In method "%s": wrong number of argument bytes'
                         '(got %i, nedded %i)' %
                         (method, len(data), bts_num))
        res = self.send_cmd(method, data)
        return res
    inner.__name__ = method
    inner.__doc__ = 'This is automatically genetated by make_method %s'\
                    'method for LinxConnection class' % method
    return inner


for method, val in LinxConnection.xmethods.items():
    setattr(LinxConnection, method, make_method(method, **val))
