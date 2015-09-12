# This is an example of popping a packet from the Emotiv class's packet queue
# and printing the gyro x and y values to the console. 

from emokit.emotiv import Emotiv
import platform
if platform.system() == "Windows":
    import socket  # Needed to prevent gevent crashing on Windows. (surfly / gevent issue #459)
import gevent

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

is_running = True 
# TODO: is_running is not working as expected. But it DOES work!

def evt_main():
    global is_running
    ring_buf = np.zeros(x.size)
    headset = Emotiv()

    gevent.spawn(headset.setup)
    gevent.sleep(0)
    pos = 0
    try:
        while is_running:
            packet = headset.dequeue()
            print packet.gyro_x, packet.gyro_y

            ring_buf[pos] = packet.sensors["O1"]["value"]
            pos = (pos + 1) % ring_buf.size
            if pos % 4 == 0:
                yield np.concatenate((ring_buf[pos:ring_buf.size:1], ring_buf[0:pos:1]))

            gevent.sleep(0)
    except KeyboardInterrupt:
        headset.close()
    finally:
        is_running = False
        headset.close()

x = np.arange(0, 1024)
test_buf = np.zeros(x.size)

fig, ax = plt.subplots()
line, = ax.plot(x, test_buf)
plt.axis([0, x.size - 1, 0, 40000])

def init():
    line.set_ydata(np.ma.array(x, mask=True))
    return line,

def animate(rb):
    dft = np.fft.fft(rb)
    line.set_ydata(np.absolute(dft))
    return line,


ani = animation.FuncAnimation(fig, animate, evt_main, init_func=init, interval=20, blit=True)
plt.show()
is_running = False

while True:
    gevent.sleep(0)

