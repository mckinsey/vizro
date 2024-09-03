"""Utils file."""


def check_file_extension(filename):
    filename = filename.lower()

    # Check if the filename ends with .csv or .xls
    return filename.endswith(".csv") or filename.endswith(".xls") or filename.endswith(".xlsx")
