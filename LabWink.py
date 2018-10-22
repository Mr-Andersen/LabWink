#!/usr/bin/python3

from andrew_anderson_utils.x_structs import *
from linx_connection import *

import logging
from time import time

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

conn = LinxConnection(port='/dev/ttyUSB0')

app = QtGui.QApplication([])
win = pg.GraphicsWindow(title='Current')
pg.setConfigOptions(antialias=True)

p1 = win.addPlot(title='Direct data')
curve1 = p1.plot(pen='y')
data = []

p2 = win.addPlot(title='Velocity')
curve2 = p2.plot(pen='y')
v_data = []

time_arr = []
start_time = time()


def update():
    dct = conn.AnalogRead(XDict, 0)
    time_arr.append(time() - start_time)
    new = 5 * ((dct.data[2] << 8) + dct.data[1]) / 2 ** dct.data[0]
    if len(data) > 0:
        v_new = (new - data[-1]) * dt
    else:
        v_new = new * dt

    data.append(new)
    v_data.append(v_new)

    curve1.setData(time_arr, data)
    curve2.setData(time_arr, v_data)


timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)

QtGui.QApplication.instance().exec_()
