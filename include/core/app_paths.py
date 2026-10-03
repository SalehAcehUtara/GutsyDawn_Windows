import os
import sys

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.getcwd()

def get_app_data_dir():
    path = os.path.join(get_base_dir(), 'gddata')
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def get_save_path(username):
    return os.path.join(get_app_data_dir(), f"pos_{username}.dat")

def get_sounds_dir():
    path = os.path.join(get_app_data_dir(), 'Sound')
    if not os.path.exists(path):
        os.makedirs(path)
    return path
