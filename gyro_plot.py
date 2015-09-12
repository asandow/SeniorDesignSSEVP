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

def evt_main(ring_buf):
    headset = Emotiv()

    gevent.spawn(headset.setup)
    gevent.sleep(0)
    pos = 0
    try:
        while True:
            packet = headset.dequeue()
            print packet.gyro_x, packet.gyro_y

            ring_buf[pos] = packet.gyro_x
            if pos % 4 == 0:
                yield ring_buf
            pos = (pos + 1) % 1024

            gevent.sleep(0)
    except KeyboardInterrupt:
        headset.close()
    finally:
        is_running = False
        headset.close()

x = np.linspace(0, 1023, 1024)
test_buf = np.zeros(1024)

fig, ax = plt.subplots()
line, = ax.plot(x, test_buf)
plt.axis([0, 1024, -100, 100])

def evt_wrapper():
    def gen():
        return evt_main(test_buf)
    return gen

def init():
    line.set_ydata(np.ma.array(x, mask=True))
    return line,

def animate(rb):
    print "Animation!"
    print rb
    line.set_ydata(rb)
    return line,

def counter():
    i = 0
    while is_running:
        yield i
        i = i + 1

ani = animation.FuncAnimation(fig, animate, evt_wrapper(), init_func=init, interval=20, blit=True)
plt.show()

# gevent.Greenlet.spawn(evt_main, test_buf)

while True:
    gevent.sleep(0)

