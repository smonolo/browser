import os
import tkinter

from url import URL


WIDTH, HEIGHT = 800, 600


def lex(body: str):
    in_tag = False
    text = ""

    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            text += c

    text = text.replace("&lt;", "<").replace("&gt;", ">")

    return text


class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.canvas.pack()

    def load(self, url: URL):
        body = url.request()
        text = lex(body)
        HSTEP, VSTEP = 13, 18
        cursor_x, cursor_y = HSTEP, VSTEP

        for c in text:
            self.canvas.create_text(cursor_x, cursor_y, text=c)
            cursor_x += HSTEP
            
            if cursor_x >= WIDTH - HSTEP:
                cursor_y += VSTEP
                cursor_x = HSTEP


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        url = "file://" + os.path.abspath(sys.argv[0])
    else:
        url = sys.argv[1]

    Browser().load(URL(url))
    tkinter.mainloop()
