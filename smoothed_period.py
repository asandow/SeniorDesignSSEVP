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

SENSOR_ID = "O1"

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
            yield packet
            gevent.sleep(0)
    except KeyboardInterrupt:
        headset.close()
    finally:
        is_running = False
        headset.close()

x = np.arange(0, 4096)
pre_buf = np.zeros(x.size)

fig, ax = plt.subplots()
line, = ax.plot(x, pre_buf)
plt.axis([0, x.size - 1, -8192, 8191])

def init():
    line.set_ydata(np.ma.array(x, mask=True))
    return line,

animate_pos = 0
animate_ring_buf = np.zeros(x.size)

def animate(packet, spre):
    global animate_pos, animate_ring_buf
    animate_ring_buf[animate_pos] = packet.sensors[SENSOR_ID]["value"]
    animate_pos = (animate_pos + 1) % animate_ring_buf.size

    if animate_pos % 4 == 0:
        rb = np.concatenate((animate_ring_buf[
                animate_pos:animate_ring_buf.size:1], animate_ring_buf[0:animate_pos:1]))
        dft = np.fft.fft(rb)
        line.set_ydata(np.square(np.absolute(dft))/dft.size)
        return line,
    else:
        return []

packet_generator = evt_main()
try:
    pos = 0
    while pos < pre_buf.size:
        packet = next(packet_generator)
        pre_buf[pos] = packet.sensors[SENSOR_ID]["value"]
        pos += 1
        if packet.sensors[SENSOR_ID]["quality"] <= 7:
            pos = 0
except StopIteration:
    pass

print "Pre SSVEP data collected successfully"
rpre = np.fft.rfft(np.square(np.fft.fft(pre_buf)))
hamming_window = 0.5*(1 + np.cos(np.arange(-np.pi, np.pi, rpre.size)))

spre = np.fft.fft(rpre * hamming_window)

ani = animation.FuncAnimation(fig, animate, packet_generator, init_func=init, interval=20, blit=True, fargs=spre)
plt.show()
is_running = False

while True:
    gevent.sleep(0)

