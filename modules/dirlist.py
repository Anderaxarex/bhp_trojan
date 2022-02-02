import os

def run(**args):
    print("dirlist module active")
    files = os.listdir()
    return str(files)
    