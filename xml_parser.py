import re


class XMLAttribute:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return f'{self.name}="{self.value}"'


class XMLText:
    def __init__(self, text: str):
        self.text = text

    def beauty_print(self):
        return [self.text]


class XMLElement:
    def __init__(self, name):
        self.name = name
        self.attributes = {}
        self.children: list[XMLElement] = []
        self.text = ""
        self.tag = ""

    def add_attribute(self, name, value):
        self.attributes[name] = XMLAttribute(name, value)

    def set_tag(self, tag: str):
        if tag is not None:
            self.tag = tag

    def add_child(self, child):
        self.children.append(child)

    def set_text(self, text):
        self.text = text

    @property
    def attributes_tag(self):
        return " ".join([f"{attribute}" for attribute in self.attributes.values()])

    @property
    def init_tag(self):
        return f"<{self.tag}{self.name} {self.attributes_tag}>"

    @property
    def end_tag(self):
        return f"</{self.tag}{self.name}>"

    def beauty_print(self):
        if not self.children:
            return [f"{self.init_tag}{self.text}{self.end_tag}"]

        string_text = [f"{self.init_tag}"]
        for child in self.children:

            string_text.extend([f"\t{i}" for i in child.beauty_print()])

        string_text += [f"{self.end_tag}"]
        return string_text


class XMLDocument:
    def __init__(self):
        self.root = None

    def set_root(self, root):
        self.root: XMLElement = root

    def __str__(self):
        return "\n".join(self.root.beauty_print())

    def save(self, path: str):
        with open(path, "w") as file:
            file.write(str(self))


class XMLTokenizer:
    def __init__(self, xml_string):
        self.xml_string = xml_string
        self.tokens = self.tokenize(xml_string)
        self.current_token_index = 0

    def tokenize(self, xml_string):
        tokens = re.findall(r"<[^>]+>|[^<]+", xml_string)
        return [token.strip() for token in tokens if token.strip()]

    def get_next_token(self):
        if self.current_token_index < len(self.tokens):
            token = self.tokens[self.current_token_index]
            self.current_token_index += 1
            return token
        return None


class XMLParser:
    def __init__(self, xml_string):
        self.tokenizer = XMLTokenizer(xml_string)

    def parse(self):
        document = XMLDocument()
        document.set_root(self.parse_element())
        return document

    def parse_element(self):
        token: str = self.tokenizer.get_next_token()

        if token is None:
            return None

        if not token.startswith("<"):
            return XMLText(token)

        if token.startswith("</"):
            return None

        element_name = re.match(r"<(\w+:)*(\w[-\w]*)", token)
        element = XMLElement(element_name.group(2))
        element.set_tag(element_name.group(1))
        attributes = re.findall(r"(\w+\-*\w+)=\"*([\w\s:\-\.\%]+)\"*", token)
        for name, value in attributes:
            element.add_attribute(name, value)

        if token.endswith("/>"):
            return element
        self.parse_children(element)

        return element

    def parse_children(self, element: XMLElement):
        parsed_element = self.parse_element()
        while parsed_element is not None:
            element.add_child(parsed_element)
            parsed_element = self.parse_element()
