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
            curses.curs_set(0)
            stdscr.addstr(2, 4, "BCI Brain Controller", curses.A_BOLD)
            stdscr.addstr(
                4, 3, "[t]Take-Off   [l]Land    [e]Emergency-Stop    [s]Start-Scanning  [q]Quit")
            stdscr.addstr(6, 3, "Command Queue: <F,U,D>")
            stdscr.addstr(8, 3, "Mode:            Test-mode")
            stdscr.addstr(9, 3, "Current State:   " +
                          str(self.controller.state))
            stdscr.addstr(10, 3, "Current Command: " +
                          self.controller.tello.current_command)
            stdscr.addstr(11, 3, "Last Brain Read: Forward")

            rectangle(stdscr, 1, 2, 3, 80)
            rectangle(stdscr, 1, 2, 5, 80)
            rectangle(stdscr, 1, 2, 7, 80)
            rectangle(stdscr, 1, 2, 12, 80)

            stdscr.nodelay(True)
            c = stdscr.getch()
            if c == ord('t'):
                self.controller.tello_decode_code(4)
            elif c == ord('l'):
                self.controller.tello_decode_code(5)
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
