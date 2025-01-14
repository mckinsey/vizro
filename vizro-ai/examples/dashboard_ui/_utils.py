"""Utils file."""

import base64
import io
import logging
import socket
import os
import signal
import subprocess
import time

import pandas as pd


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


def format_output(generated_code, port):
    generated_code = generated_code.replace("```python", "")
    generated_code = generated_code.replace("```", "")

    code_lines = generated_code.split("\n")

    for i, line in enumerate(code_lines):
        if line.startswith("import") or line.startswith("from"):
            # Insert the additional import statement right after the first import
            code_lines.insert(i + 1, "from vizro import Vizro")
            code_lines.insert(i + 2, "import os")
            code_lines.insert(i + 3, "import pandas as pd")

            break  # Ensure only one insertion after the first import

    for i, line in enumerate(code_lines):
        if line.startswith("####### Function definitions ######"):
            code_lines.insert(i - 1, "script_directory = os.path.dirname(os.path.abspath(__file__))")
            break

    for i, line in enumerate(code_lines):
        if line.startswith("script_directory"):
            code_lines.insert(i + 1, "all_files = os.listdir(script_directory)")
            code_lines.insert(i + 2, "csv_files = [file for file in all_files if file.endswith('.csv')]")
            code_lines.insert(i + 3, "csv_file = csv_files[0]")
            code_lines.insert(i + 4, "file_path = os.path.join(script_directory, csv_file)")
            code_lines.insert(i + 5, "df = pd.read_csv(file_path)")

    for i, line in enumerate(code_lines):
        if line.startswith("# from vizro.managers "):
            code_lines[i] = line.lstrip("#").strip()
        if line.startswith("# data_manager"):
            code_lines[i] = line.lstrip("#").strip()

    for i, line in enumerate(code_lines):
        if line.startswith("data_manager"):
            code_lines[i] = line.replace("===> Fill in here <===", "df")

    generated_code = "\n".join(code_lines)
    generated_code += "\napp = Vizro().build(model)\n"
    generated_code += '\nif __name__ == "__main__":\n'
    generated_code += f"    app.run(host='0.0.0.0', port={port})\n"

    return generated_code


def check_available_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sk:
        return sk.connect_ex(("127.0.0.1", port)) != 0


def find_available_port(base_port=8051):
    while not check_available_port(base_port):
        base_port += 1
    return base_port

def kill_process_on_port(port):
    """
    Kills any process and its children running on the specified TCP port.
    Uses lsof to find the process and kills it with SIGTERM followed by SIGKILL if necessary.
    
    Args:
        port (int): The port number to kill
        
    Returns:
        bool: True if process was killed successfully, False otherwise
    """
    try:
        # Find process ID using lsof
        cmd = f"lsof -ti :{port}"
        pids = subprocess.check_output(cmd, shell=True).decode().strip().split('\n')
        
        if not pids or pids[0] == '':
            print(f"No process found running on port {port}")
            return False
            
        # Kill each process
        for pid in pids:
            pid = int(pid)
            try:
                # First try SIGTERM
                os.kill(pid, signal.SIGTERM)
                print(f"Sent SIGTERM to process {pid}")
                
                # Give it a moment to terminate
                time.sleep(2)
                
                # Check if it's still running
                try:
                    os.kill(pid, 0)
                    # If we get here, process is still running - use SIGKILL
                    print(f"Process {pid} still running, sending SIGKILL")
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    # Process is already gone
                    pass
                    
            except ProcessLookupError:
                continue
                
        print(f"Successfully killed all processes on port {port}")
        return True
        
    except subprocess.CalledProcessError:
        print(f"No process found running on port {port}")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
