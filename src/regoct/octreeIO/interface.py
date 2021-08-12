import abc
from typing import final
from queue import LifoQueue

from ..Structures import Octree
from .reader import Loader, BuilderHelper
from .saveing import Saver, scanner


class Interface(abc.ABC):
    @staticmethod
    @final
    def load(file_path) -> Octree:
        with open(file_path, "rb") as io:
            build_help = BuilderHelper()
            with build_help.build():
                for command in Loader(io):
                    build_help.route(command)
            return build_help.octree        


    @staticmethod
    @final
    def save(octree:Octree, file_path):
        with open(file_path, "wb") as io:
            saver = Saver(io)
            for command in scanner(octree):
                saver.translate(command)


    @classmethod
    @abc.abstractmethod
    def from_file(cls, loader:Loader):...


    @abc.abstractmethod
    def to_file(self, saver:Saver):...
