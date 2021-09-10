import abc
from typing import final
from queue import LifoQueue

from ..Structures import Octree
from .reader import Loader, LoadingStream, BuilderHelper
from .saveing import Saver, SavingStream, scanner


class Interface(abc.ABC):
    @classmethod
    @final
    def load(cls, file_path) -> Octree:
        with open(file_path, "rb") as io:
            build_help = BuilderHelper()
            with build_help.build():
                for command in Loader(io, cls):
                    build_help.route(command)
            return build_help.octree        


    @classmethod
    @final
    def save(cls, octree:Octree, file_path):
        with open(file_path, "wb") as io:
            saver = Saver(io, cls)
            for command in scanner(octree):
                saver.translate(command)


    @classmethod
    @abc.abstractmethod
    def from_file(cls, loader:LoadingStream):...


    @staticmethod
    @abc.abstractmethod
    def to_file(obj, saver:SavingStream):...
