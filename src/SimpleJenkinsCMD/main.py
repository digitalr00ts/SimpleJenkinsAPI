import types
from dataclasses import dataclass, field
from inspect import getmembers, isfunction
from typing import Iterable

from SimpleJenkinsAPI import Jenkins as JenkinsAPI
from SimpleJenkinsCMD import cmds


@dataclass
class CMDs:
    jenkins: JenkinsAPI
    _cmds: Iterable = field(default=None, init=False)

    def __post_init__(self):
        members = getmembers(cmds, isfunction)
        self._cmds = [name for name, _ in members]
        for name, func in members:
            setattr(self, name, types.MethodType(func, self.jenkins))

    @property
    def commands(self) -> Iterable[str]:
        return self._cmds


@dataclass
class SimpleJenkinsCMD(JenkinsAPI):
    cmd: CMDs = field(default=None, init=False, repr=False, hash=False, compare=False)

    def __post_init__(self):
        self.cmd = CMDs(self)
