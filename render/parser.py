from constants import SELF_CLOSING_TAGS
from render.element import Element
from render.text import Text


def replace_entities(text: str):
    return text.replace("&lt;", "<").replace("&gt;", ">")


class HTMLParser:
    def __init__(self, body: str):
        self.body = body
        self.unfinished = []

    def parse(self) -> Element:
        if not len(self.body):
            return self.finish()

        text = ""
        in_tag = False

        for c in self.body:
            if c == "<":
                in_tag = True

                if text:
                    self.add_text(replace_entities(text))

                text = ""
            elif c == ">":
                in_tag = False
                self.add_tag(text)
                text = ""
            else:
                text += c

        if not in_tag and text:
            self.add_text(replace_entities(text))

        return self.finish()

    def add_text(self, text: str):
        if text.isspace():
            return

        parent = self.unfinished[-1]
        node = Text(text, parent)

        parent.children.append(node)

    def add_tag(self, tag: str):
        tag, attributes = self.get_attributes(tag)

        if tag.startswith("!"):
            return

        if tag.startswith("/"):
            if len(self.unfinished) == 1:
                return

            node = self.unfinished.pop()
            parent = self.unfinished[-1]

            parent.children.append(node)
        elif tag in SELF_CLOSING_TAGS:
            parent = self.unfinished[-1]
            node = Element(tag, attributes, parent)

            parent.children.append(node)
        else:
            parent = self.unfinished[-1] if self.unfinished else None
            node = Element(tag, attributes, parent)

            self.unfinished.append(node)

    def finish(self) -> Element:
        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent = self.unfinished[-1]

            parent.children.append(node)

        return self.unfinished.pop()

    def get_attributes(self, text: str):
        parts = text.split()
        tag = parts[0].casefold()
        attributes = {}

        for attr_pair in parts[1:]:
            if "=" in attr_pair:
                key, value = attr_pair.split("=", 1)
                attributes[key.casefold()] = value

                if len(value) > 2 and value[0] in ["'", '"']:
                    value = value[1:-1]
            else:
                attributes[attr_pair.casefold()] = ""

        return tag, attributes
