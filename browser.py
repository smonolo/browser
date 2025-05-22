import os
import tkinter
import tkinter.font

from constants import WIDTH, HEIGHT, VSTEP, SCROLL_STEP, SCROLLBAR_WIDTH
from render.layout import Layout
from render.parser import HTMLParser
from url import URL


def print_tree(node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)


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
        self.nodes = HTMLParser(body).parse()
        self.display_list = Layout(self.nodes).display_list
        self.draw()

    def draw(self):
        self.canvas.delete("all")

        for x, y, c, f in self.display_list:
            if y > self.scroll + HEIGHT:
                continue
            if y + VSTEP < self.scroll:
                continue

            self.canvas.create_text(x, y - self.scroll, text=c, font=f, anchor="nw")

        if len(self.display_list):
            self.draw_scrollbar()

    def draw_scrollbar(self):
        last_y = self.display_list[-1][1]

        self.canvas.create_rectangle(
            WIDTH - SCROLLBAR_WIDTH,
            (self.scroll * HEIGHT) / last_y,
            WIDTH,
            (self.scroll * HEIGHT) / last_y + (HEIGHT * HEIGHT) / last_y,
            fill="black",
            outline="white",
        )

    def scroll_down(self, event: tkinter.Event):
        if self.scroll + SCROLL_STEP < self.display_list[-1][1]:
            self.scroll += SCROLL_STEP
            self.draw()

    def scroll_up(self, event: tkinter.Event):
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

    # try:
    #     browser.load(URL(url))
    # except Exception as e:
    #     browser.load(URL("about:blank"))

    browser.load(URL(url))

    tkinter.mainloop()
