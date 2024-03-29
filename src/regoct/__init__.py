from .structures import Octree
from .visualiser import Display
from .reader import LoadingStream
from .saveing import SavingStream
from .interface import Interface


class _Default(Interface):
    def from_file(cls, loader:LoadingStream):
        return loader.convert()

    def to_file(obj, saver:SavingStream):
        saver.convert(obj) 


def load(file_path):
    return _Default.load(file_path)


def save(octree, file_path):
    _Default.save(octree, file_path)