from curses.textpad import rectangle
import curses
import time
import threading
from bci_controller import controller


class main:
    def __init__(self):
        self.running = True
        self.current_command = "NaN"
        self.controller = controller("./model.h5")

    def run(self):
        controller = threading.Thread(
            target=lambda: self.controller.start(True), daemon=True)
        controller.start()
        gui = threading.Thread(target=lambda: self.gui_loop())
        gui.start()

    def gui_loop(self):
        while self.running:
            stdscr = curses.initscr()
            stdscr.refresh()
            curses.noecho()
            curses.cbreak()
            curses.curs_set(0)
            stdscr.addstr(2, 4, "BCI Brain Controller", curses.A_BOLD)
            stdscr.addstr(
                4, 3, "[t]Take-Off   [l]Land    [e]Emergency-Stop   [q]Quit")
            stdscr.addstr(6, 3, "From Tello:      " +
                          self.controller.tello.from_tello)
            stdscr.addstr(7, 3, "Mode:            Test-mode")
            stdscr.addstr(8, 3, "Current State:   " +
                          str(self.controller.state))
            stdscr.addstr(9, 3, "Current Command: " +
                          self.controller.tello.current_command)
            stdscr.addstr(10, 3, "Last Brain Read: " +
                          self.controller.last_read)

            rectangle(stdscr, 1, 2, 3, 56)
            rectangle(stdscr, 1, 2, 5, 56)
            rectangle(stdscr, 1, 2, 11, 56)

            stdscr.nodelay(True)
            c = stdscr.getch()
            if c == ord('t'):
                self.controller.tello_decode_code(6)
            elif c == ord('l'):
                self.controller.tello_decode_code(7)
            elif c == ord('e'):
                self.controller.emergency_land()
            elif c == ord('s'):
                break
            elif c == ord('q'):
                curses.endwin()
                break


if __name__ == "__main__":
    m = main()
    m.run()
