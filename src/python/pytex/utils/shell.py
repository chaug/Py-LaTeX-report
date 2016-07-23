import os

def safe_mkdir(path):
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise Exception("%s exists but is not a folder" % path)
    else:
        os.mkdir(path)

def safe_mkdir_p(path):
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise Exception("%s exists but is not a folder" % path)
    else:
        os.makedirs(path)

