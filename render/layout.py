import tkinter.font

from constants import HSTEP, SCROLLBAR_WIDTH, VSTEP, WIDTH
from render.element import Element
from render.text import Text


FONTS = {}


def get_font(size: int, weight: str, style: str) -> tkinter.font.Font:
    key = (size, weight, style)

    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight, slant=style)
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)

    return FONTS[key][0]


class Layout:
    def __init__(self, tree: Element):
        self.display_list = []
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.style = "roman"
        self.weight = "normal"
        self.size = 16
        self.line = []

        self.recurse(tree)
        self.flush()

    def open_tag(self, tag: str):
        if tag == "i":
            self.style = "italic"
        elif tag == "b":
            self.weight = "bold"
        elif tag == "small":
            self.size -= 2
        elif tag == "big":
            self.size += 4
        elif tag == "br":
            self.flush()

    def close_tag(self, tag: str):
        if tag == "/i":
            self.style = "roman"
        elif tag == "/b":
            self.weight = "normal"
        elif tag == "/small":
            self.size += 2
        elif tag == "/big":
            self.size -= 4
        elif tag == "/p":
            self.flush()
            self.cursor_y += VSTEP

    def recurse(self, tree: Element):
        if isinstance(tree, Text):
            for word in tree.text.split():
                self.word(word)
        else:
            self.open_tag(tree.tag)

            for child in tree.children:
                self.recurse(child)

            self.close_tag(tree.tag)

    def word(self, word: str):
        font = get_font(self.size, self.weight, self.style)
        w = font.measure(word)

        if self.cursor_x + w > WIDTH - SCROLLBAR_WIDTH:
            self.flush()

        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w + font.measure(" ")

    def flush(self):
        if not self.line:
            return

        metrics = [font.metrics() for x, word, font in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent

        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))

        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent

        self.cursor_x = HSTEP
        self.line = []
