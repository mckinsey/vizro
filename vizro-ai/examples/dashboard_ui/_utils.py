"""Utils file."""
from langchain.schema import HumanMessage


def check_file_extension(filename):
    filename = filename.lower()

    # Check if the filename ends with .csv or .xls
    return filename.endswith(".csv") or filename.endswith(".xls") or filename.endswith(".xlsx")


def construct_message(images, question):
    """Construct a HumanMessage with a dynamic number of images.

    :param images: List of base64-encoded image data
    :param question: The question to ask about the images
    :return: HumanMessage object
    """
    content = [{"type": "text", "text": question}, {"type": "image_url", "image_url": {"url": f"{images}"}}]

    return HumanMessage(content=content)
