import os
import sys

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for Nuitka """
    if hasattr(sys, 'frozen'):
        # The folder where the .exe lives
        base_path = os.path.dirname(sys.executable)
    else:
        # The folder where your main.py lives
        base_path = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
    
    return os.path.normpath(os.path.join(base_path, relative_path))