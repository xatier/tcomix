#!/usr/bin/env python3
"""

Tcomix: A terminal based comic books viewer

License: GNU GPL version 3
Author: xatier



reference:

    https://docs.python.org/3/library/curses.html
    https://github.com/hut/ranger/blob/master/ranger%2Fext%2Fimg_display.py
    http://blog.z3bra.org/2014/01/images-in-terminal.html

"""

import subprocess
import curses

W3MIMGDISPLAY = '/usr/lib/w3m/w3mimgdisplay'
W3M_DISPLAY = "0;1;{x};{y};{w};{h};;;;;{filename}\n4;\n3;\n"
W3M_CLEAR = "6;{x};{y};{w};{h}\n4;\n3;\n"
W3M_GETSIZE = "5;{filename}\n"


class Tcomix:
    """
    Main application class, this handles everything
    """
    def __init__(self):

        # test images
        self.image_list = self.imgfoo().split()
        self.image_idx = 0

        try:
            # initialize curses stuff
            self.win = curses.initscr()
            curses.noecho()
            curses.curs_set(False)
            self.win.keypad(True)

            self.win.erase()
            self.win.border()

            self.filelist_box_width = 20
            self.filelist_box = curses.newwin(
                curses.LINES, self.filelist_box_width, 0, 0
            )
            self.filelist_box.border()

            self.m_y, self.m_x = curses.LINES, curses.COLS
            self.cury, self.curx = self.m_y - 2, 1

            self.fontw, self.fonth = self.get_font_dimensions()

        except Exception:
            print("GG on python curses init!")

        self.max_w = self.get_screen_size()[0] - self.fontw * 23
        self.max_h = self.get_screen_size()[1] - self.fonth * 2

        self.win.refresh()
        self.filelist_box.refresh()

    def execute(self, cmd=""):
        """ shell execution, super dangerous """
        return subprocess.check_output(cmd, shell=True).decode()

    def execute_w3m(self, w3m_cmd=""):
        return self.execute("echo '{}' | {}".format(w3m_cmd, W3MIMGDISPLAY))

    def get_image_size(self, filename):
        w, h = self.execute_w3m(W3M_GETSIZE.format(filename=filename)).split()
        return int(w), int(h)

    def get_screen_size(self):
        w, h = self.execute("{} -test".format(W3MIMGDISPLAY)).split()
        return int(w), int(h)

    def get_font_dimensions(self):
        w, h = self.get_screen_size()
        w += 2
        h += 2
        return (w // curses.COLS), (h // curses.LINES)

    def draw(self, filename, x, y, w, h):
        return self.execute_w3m(
            W3M_DISPLAY.format(
                filename=filename,
                x=int((x - 0.2) * self.fontw),
                y=int(y * self.fonth),
                w=w,
                h=h
            )
        )

    def clear(self, x, y, w, h):
        return self.execute_w3m(
            W3M_CLEAR.format(
                x=int((x - 0.2) * self.fontw),
                y=int(y * self.fonth),
                w=int(w * 1.01),
                h=int(h * 1.01)
            )
        )

    def imgfoo(self):
        return self.execute("ls ~/Pictures/*.jpg")

    def _norm_h(self, w, h, nw=0):
        nw = self.max_w if nw == 0 else nw
        h = int(nw / w * h)
        w = nw
        return w, h

    def _norm_w(self, w, h, nh=0):
        nh = self.max_h if nh == 0 else nh
        w = int(nh / h * w)
        h = nh
        return w, h

    def text(self, txt=""):
        self.win.addstr(self.cury, self.curx, txt)

    def main_loop(self):

        while True:
            w, h = self.get_image_size(self.image_list[self.image_idx])

            if w > self.max_w:
                w, h = self._norm_h(w, h)

            if h > self.max_h:
                w, h = self._norm_w(w, h)

            imgview_x, imgview_y = 21, 1
            self.draw(
                self.image_list[self.image_idx], imgview_x, imgview_y, w, h
            )

            self.text(">" + " " * 50)
            self.text("> {}".format(self.image_list[self.image_idx]))

            c = self.win.getch()
            if c == ord('q'):
                break
            elif c == curses.KEY_UP or c == ord('k'):
                self.image_idx += 1
            elif c == curses.KEY_DOWN or c == ord('j'):
                self.image_idx -= 1

            self.image_idx %= len(self.image_list)
            self.clear(imgview_x, imgview_y, w, h)
            self.win.refresh()
            self.filelist_box.refresh()

    def __del__(self):
        self.win.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()


if __name__ == '__main__':
    TCOMIX = Tcomix()
    TCOMIX.main_loop()
