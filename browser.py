import os
import tkinter

from url import URL


WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100
SCROLLBAR_WIDTH = 10


def lex(body: str):
    text = ""

    if not len(body):
        return text

    in_tag = False

    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            text += c

    text = text.replace("&lt;", "<").replace("&gt;", ">")

    return text


def layout(text: str):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP

    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP

        if cursor_x >= WIDTH - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP

    return display_list


class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.canvas.pack()

        self.scroll = 0
        self.window.bind("<Down>", self.scroll_down)
        self.window.bind("<Up>", self.scroll_up)
        self.window.bind("<MouseWheel>", self.scroll_wheel)

    def load(self, url: URL):
        body = url.request()
        text = lex(body)
        self.display_list = layout(text)
        self.draw()

    def draw(self):
        self.canvas.delete("all")

        for x, y, c in self.display_list:
            if y > self.scroll + HEIGHT:
                continue
            if y + VSTEP < self.scroll:
                continue

            self.canvas.create_text(x, y - self.scroll, text=c)

        if len(self.display_list):
            self.draw_scrollbar()

    def draw_scrollbar(self):
        last_y = self.display_list[-1][1]

        self.canvas.create_rectangle(
            WIDTH - SCROLLBAR_WIDTH,
            (self.scroll * HEIGHT) / last_y,
            WIDTH,
            (self.scroll * HEIGHT) / last_y + (HEIGHT * HEIGHT) / last_y,
        )

    def scroll_down(self, _):
        if self.scroll + SCROLL_STEP < self.display_list[-1][1]:
            self.scroll += SCROLL_STEP
            self.draw()

    def scroll_up(self, _):
        if self.scroll >= SCROLL_STEP:
            self.scroll -= SCROLL_STEP
            self.draw()

    def scroll_wheel(self, event: tkinter.Event):
        if event.delta > 0:
            self.scroll_up(None)
        else:
            self.scroll_down(None)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        url = "file://" + os.path.abspath(sys.argv[0])
    else:
        url = sys.argv[1]

    browser = Browser()

    try:
        browser.load(URL(url))
    except Exception as e:
        browser.load(URL("about:blank"))

    tkinter.mainloop()
