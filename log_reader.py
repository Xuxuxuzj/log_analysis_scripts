import os

def read_lines(file_path):
    with open(file_path, 'r', encoding='latin-1') as file:
        lines = file.readlines()
    return lines