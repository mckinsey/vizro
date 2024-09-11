"""Utils file."""

import base64
import io
import logging

import pandas as pd
from langchain.schema import HumanMessage


def check_file_extension(filename):
    filename = filename.lower()

    # Check if the filename ends with .csv or .xls
    return filename.endswith(".csv") or filename.endswith(".xls") or filename.endswith(".xlsx")


def process_file(contents, filename):
    """Process the uploaded file content based on its extension."""
    if not check_file_extension(filename=filename):
        return {"error_message": "Unsupported file extension.. Make sure to upload either csv or an excel file."}

    try:
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        if filename.endswith(".csv"):
            # Handle CSV file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        else:
            # Handle Excel file
            df = pd.read_excel(io.BytesIO(decoded))

        data = df.to_dict("records")
        return data

    except Exception as e:
        logging.exception(f"Error processing the file '{filename}': {e}")
        logging.exception(e)
        return {"error_message": f"There was an error processing the file '{filename}'."}


def construct_message(images, question):
    """Construct a HumanMessage with a dynamic number of images.

    :param images: List of base64-encoded image data
    :param question: The question to ask about the images
    :return: HumanMessage object
    """
    content = [{"type": "text", "text": question}]
    for img_data in images:
        content.append({"type": "image_url", "image_url": {"url": f"{img_data}"}})
    return HumanMessage(content=content)
