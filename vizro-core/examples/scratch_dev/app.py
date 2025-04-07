"""Scratchpad for testing."""

import vizro.models as vm
from vizro import Vizro
import random


def generate_lorem_ipsum(length=None):
    lorem_ipsum = """
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam sed elementum ligula, in pharetra velit.
            In ultricies est ac mauris vehicula fermentum. Curabitur faucibus elementum lectus, vitae luctus libero fermentum.
            Name ut ipsum tortor. Praesent ut nulla risus. Praesent in dignissim nulla. In quis blandit ipsum.
        """
    words = lorem_ipsum.split()
    length = random.randint(100, 500) if length is None else length
    while len(" ".join(words)) < length:
        words += words  # repeat the words to extend the length
    return " ".join(words)[:length]


page3 = vm.Page(
    title="Flex - default",
    layout=vm.Flex(),
    components=[vm.Card(text=generate_lorem_ipsum()) for i in range(6)],
)


page4 = vm.Page(
    title="Flex - gap",
    layout=vm.Flex(gap="40px"),
    components=[vm.Card(text=generate_lorem_ipsum()) for i in range(6)],
)

page5 = vm.Page(
    title="Flex - row - unequal content",
    layout=vm.Flex(direction="row"),
    components=[vm.Card(text=generate_lorem_ipsum()) for i in range(6)],
)

page6 = vm.Page(
    title="Flex - row/wrap - unequal content",
    layout=vm.Flex(direction="row", wrap=True),
    components=[vm.Card(text=generate_lorem_ipsum()) for i in range(6)],
)

page7 = vm.Page(
    title="Flex - row - unequal content - same width",
    layout=vm.Flex(direction="row"),
    components=[vm.Card(text=generate_lorem_ipsum(), extra={"style": {"width": "200px"}}) for i in range(6)],
)

page8 = vm.Page(
    title="Flex - row/wrap - unequal content - same width",
    layout=vm.Flex(direction="row", wrap=True),
    components=[vm.Card(text=generate_lorem_ipsum(), extra={"style": {"width": "200px"}}) for i in range(6)],
)

page9 = vm.Page(
    title="Flex - row - equal content - no width",
    layout=vm.Flex(direction="row"),
    components=[vm.Card(text=generate_lorem_ipsum(300)) for i in range(6)],
)

page10 = vm.Page(
    title="Flex - row/wrap - equal content - same width",
    layout=vm.Flex(direction="row", wrap=True),
    components=[vm.Card(text=generate_lorem_ipsum(300), extra={"style": {"width": "200px"}}) for i in range(6)],
)


dashboard = vm.Dashboard(
    pages=[page3, page4, page5, page6, page7, page8, page9, page10],
    title="Test out Card inside Flex",
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
