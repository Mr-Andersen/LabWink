#!/usr/bin/python3

import serial
import logging
from time import sleep
import ruamel.yaml as yaml


def parse_response(bts: bytes, dict=dict):
    res = dict()
    res['datasize'] = int(bts[1])
    res['packetNum'] = int(bts[2]) << 8 + int(bts[3])
    res['status'] = int(bts[4])
    res['data'] = bts[5:-1]
    res['checksum'] = int(bts[-1])
    return res


def make_packet(**dct):
    if 'data' not in dct:
        dct['data'] = []
    if 'datasize' not in dct:
        dct['datasize'] = len(dct['data']) + 7
    bts = (bytes([0xff,
                  dct['datasize'],
                  (dct['packetNum'] >> 8) & 0xff,
                  dct['packetNum'] & 0xff,
                  (dct['command'] >> 8) & 0xff,
                  dct['command'] & 0xff]) +
           dct['data'])
    if 'checksum' not in dct:
        dct['checksum'] = sum(bts) & 0xff
    return bts + bytes([dct['checksum']])


class LinxConnection(serial.Serial):
    xmethods = yaml.load(open('xmethods.yaml', 'rt'))

    def __init__(self, **kwargs):
        self.packetNum = 0
        serial_kwargs = dict(port='COM3', baudrate=9600)
        serial_kwargs.update(kwargs)
        serial.Serial.__init__(self, **serial_kwargs)
        sleep(2)

    def recv_raw(self, **kwargs):
        packet = self.read(2, **kwargs)
        packet += self.read(int(packet[1]) - 2, **kwargs)
        logging.debug('Received "%s"' % packet)
        return packet

    def recv(self, dict=dict, **kwargs):
        return parse_response(self.recv_raw(**kwargs), dict)

    def send_raw(self, packet: bytes):
        num = self.write(packet)
        logging.debug('Sent "%s"' % packet)
        if num != len(packet):
            logging.warn('write(packet) returned int != len(packet)')
        return num

    def send(self, **kwargs):
        return self.send_raw(make_packet(**kwargs))

    def send_cmd(self, cmd: str, *args):
        if len(args) == 1 and type(args[0]) == bytes:
            res = self.send(command=LinxConnection.xmethods[cmd]['no'],
                            data=args[0], packetNum=self.packetNum)
        else:
            res = self.send(command=LinxConnection.xmethods[cmd]['no'],
                            data=bytes(args), packetNum=self.packetNum)
        self.packetNum += 1
        return res


def make_method(method: str, no: int, bts_num: int, doc: str=None):
    def inner(self, dict=dict, *args, **kwargs):
        nonlocal method, no, bts_num
        data = bytes(args)
        if bts_num is not None and len(data) != bts_num:
            logging.warn('In method "%s": wrong number of argument bytes '
                         '(got %i, nedded %i)' %
                         (method, len(data), bts_num))
        self.send_cmd(method, data)
        return self.recv(dict, **kwargs)
    inner.__name__ = method
    if doc is None:
        inner.__doc__ = 'This is automatically genetated by make_method %s '\
                        'method for LinxConnection class. **kwargs are '\
                        'passed directly to Serial.read' % method
    else:
        inner.__doc__ = 'This is automatically genetated by make_method %s '\
                        'method for LinxConnection class. **kwargs are '\
                        'passed directly to Serial.read\n\n%s' % (method, doc)
    return inner


for method, val in LinxConnection.xmethods.items():
    setattr(LinxConnection, method, make_method(method, **val))
