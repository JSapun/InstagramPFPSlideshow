import sys

def in_venv():
    return sys.prefix != sys.base_prefix

if __name__ == '__main__':
    print("True: " + sys.prefix) if in_venv() else print("False: " + sys.prefix)
