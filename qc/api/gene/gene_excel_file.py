import os

def save_file(file):
    file_path = os.path.join('excel', file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    return file_path
