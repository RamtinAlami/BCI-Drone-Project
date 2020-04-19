import socket
import threading
import time
from queue import Queue


class Tello:
    class Decorators(object):
        # This is a Decorator class that hold Decorators for the Tello Class
        @staticmethod
        def make_queueable(command_func):
            # Adds command functions to a Queue to run concurrently
            def queueable_func(self, *args, **kwargs):
                self.command_buffer.put(
                    lambda: command_func(self, *args, **kwargs))

            return queueable_func

    def __init__(self, command_buffer_size=15):
        assert type(command_buffer_size) == int
        assert command_buffer_size > 0

        self.command_buffer = Queue(command_buffer_size)
        self.read_buffer = Queue()
        self.current_command = "NaN"
        self.connected = self.start_connection()
        self.start_receiver()
        self.start_runner_thread()

    @Decorators.make_queueable
    def forward(self):
        # Moves forward
        self.current_command = "Forward    "
        self.rc_control(0, 85, 0, 0)
        time.sleep(0.4)
        self.rc_control(0, 0, 0, 0)
        time.sleep(0.2)

    @Decorators.make_queueable
    def backward(self):
        # Moves back
        self.current_command = "Back      "
        self.rc_control(0, -85, 0, 0)
        time.sleep(0.4)
        self.rc_control(0, 0, 0, 0)
        time.sleep(0.2)

    @Decorators.make_queueable
    def right(self):
        # Moves right
        self.current_command = "Right     "
        self.rc_control(85, 0, 0, 0)
        time.sleep(0.4)
        self.rc_control(0, 0, 0, 0)
        time.sleep(0.2)

    @Decorators.make_queueable
    def left(self):
        # Moves left
        self.current_command = "Left      "
        self.rc_control(-85, 0, 0, 0)
        time.sleep(0.4)
        self.rc_control(0, 0, 0, 0)
        time.sleep(0.2)

    @Decorators.make_queueable
    def takeoff(self):
        # Tello Takesoff
        self.current_command = "Takeoff    "
        msg = "takeoff"
        self.send_command(msg)
        time.sleep(1)

    @Decorators.make_queueable
    def land(self):
        # Lands Tello and ends connection
        self.current_command = "Land    "
        msg = "land"
        self.send_command(msg)
        # self.end_connection()

    def emergency_land(self):
        # Identical to the land method, except it is not queued
        self.current_command = "E-Land"
        msg = "land"
        self.send_command(msg)
        self.end_connection()

    def end_connection(self):
        # Ends connections by closing the socket and ending the threads
        self.connected = False
        self.sock.close()

    def start_connection(self):
        # Starts a socket connection to Tello
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tello_address = ("192.168.10.1", 8889)
        self.sock.bind(("", 9000))
        self.send_command("command")
        return True

    def recv(self):
        # Constantly checks for new data from the Tello
        while self.connected:
            data, server = self.sock.recvfrom(1518)
            dt = data.decode(encoding="utf-8")
            print(dt)
            self.read_buffer.put(dt)
        print("end")

    def start_receiver(self):
        # Starts a thread that runs the loop that checks for new data from Tello
        self.recvThread = threading.Thread(target=self.recv)
        self.recvThread.start()

    def rc_control(self, lr, fb, ud, y):
        """Send RC control via four channels

        Arguments:
            lr {Int} -- Left/Right
            fb {Int} -- Forward/Backward
            ud {Int} -- Up/Down
            y {Int} -- Yaw
        """
        assert lr >= -100 and lr <= 100
        assert fb >= -100 and fb <= 100
        assert ud >= -100 and ud <= 100
        assert y >= -100 and y <= 100

        msg = f"rc {lr} {fb} {ud} {y}"
        self.send_command(msg)

    def send_command(self, msg):
        """Send command string to Tello

        Arguments:
            msg {str} -- The message that will be sent to the Tello
        """
        assert type(msg) == str
        self.sock.sendto(msg.encode(encoding="utf-8"), self.tello_address)

    def runner(self):
        # The loop that runs concurrently and constantly runs commands from buffer
        while self.connected:
            if not self.command_buffer.empty():
                command = self.command_buffer.get()
                # print(command)
                command()

    def start_runner_thread(self):
        # This will start a thread that is constantly reading the queue and running function
        command_thread = threading.Thread(target=self.runner)
        command_thread.start()


if __name__ == "__main__":
    tello = Tello()
    tello.takeoff()
    time.sleep(3)
    tello.forward()
    time.sleep(1)
    tello.right()
    time.sleep(1)
    tello.backward()
    time.sleep(1)
    tello.left()
    tello.land()
