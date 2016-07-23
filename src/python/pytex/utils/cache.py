try:
   import cPickle as pickle
except:
   import pickle

import hashlib
import os

class Cache(object):

    def __init__(self, content, root):
        self.root      = root
        self.content   = content
        self.signature = hashlib.sha224(content).hexdigest()
        self.filename  = os.path.join(self.root, self.signature + ".pickle")
        self.data      = None

    def open(self):
        self.data = None
        if os.path.exists(self.filename):
            with open(self.filename,"rb") as io:
                self.data = pickle.load(io)

    def close(self):
        if os.path.isdir(self.root) and not os.path.exists(self.filename):
            with open(self.filename,"wb") as io:
                pickle.dump(self.data, io)
            with open(self.filename+".content","w") as ioc:
                ioc.write(self.content)

    def persist(self, data):
        self.data = data

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, tb):
        if type is None:
            self.close()
            return True
