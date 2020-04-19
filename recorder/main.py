import curses
import time
import random
from curses.textpad import rectangle


# def start():


def main(stdscr):
    curses.curs_set(0)
    draw_squares(stdscr)
    while True:
        selected = random.randint(0, 2)
        wait = random.random() * 2 + 1
        time.sleep(wait)
        draw_squares(stdscr, selected=selected)
        time.sleep(0.7)
        draw_squares(stdscr)
    stdscr.getkey()


def draw_squares(stdscr, selected=-1):
    height, width = list(stdscr.getmaxyx())
    stdscr.clear()
    # Draw the outlines
    rectangle(stdscr, 1, 5, height-2, width-5)
    current = 6
    div = (width-14)//3
    ends = []
    for i in range(3):
        ends.append((2, current, height-3, current+div))
        current += div + 1
        rectangle(stdscr, ends[i][0], ends[i][1], ends[i][2], ends[i][3])

    # Fill the selected square
    if selected > -1:
        i = selected
        for k in range(ends[i][0], ends[i][2]):
            rectangle(stdscr, ends[i][0], ends[i][1], k, ends[i][3])

    stdscr.refresh()


curses.wrapper(main)
