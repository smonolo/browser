import tkinter.font

from constants import HSTEP, SCROLLBAR_WIDTH, VSTEP, WIDTH
from render.tag import Tag
from render.text import Text


class Layout:
    def __init__(self, tokens: list[Text | Tag]):
        self.display_list = []
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.style = "roman"
        self.weight = "normal"

        for tok in tokens:
            self.token(tok)

    def token(self, tok: Text | Tag):
        if isinstance(tok, Text):
            for word in tok.text.split():
                self.word(word)
        elif tok.tag == "i":
            self.style = "italic"
        elif tok.tag == "/i":
            self.style = "roman"
        elif tok.tag == "b":
            self.weight = "bold"
        elif tok.tag == "/b":
            self.weight = "normal"

    def word(self, word: str):
        font = tkinter.font.Font(size=16, weight=self.weight, slant=self.style)
        w = font.measure(word)
        self.display_list.append((self.cursor_x, self.cursor_y, word, font))
        self.cursor_x += w + font.measure(" ")

        if self.cursor_x + w >= WIDTH - SCROLLBAR_WIDTH:
            self.cursor_y += font.metrics("linespace") * 1.25
            self.cursor_x = HSTEP
