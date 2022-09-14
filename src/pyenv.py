#!/usr/bin/python3

"""
little wrapper around the venv
"""
from abc import abstractmethod
import argparse
from posixpath import islink
import re
from sys import exec_prefix
from typing import Union
import itertools
from typing import Callable, Optional, Tuple
from dataclasses import dataclass, replace
from pathlib import Path
import pathlib
import os
import shutil


try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


@dataclass(frozen=True)
class Directory:
    """
    dto to store dirs
    """

    install: Path
    bin_dir: Path

    @abstractmethod
    def from_dict(_dict):
        return Directory(install=Path(_dict["install"]), bin_dir=Path(_dict["bin_dir"]))


@dataclass(frozen=True)
class Config:
    """
    config dto
    """

    dirs: Directory
    version: Optional[str]
    create_bin: bool

    @abstractmethod
    def from_dict(_dict):
        return Config(
            dirs=Directory.from_dict(_dict["dirs"]),
            version=str(_dict["version"]),
            create_bin=bool(_dict["create_bin"]),
        )


@dataclass(frozen=True)
class Error:
    description: str

    def __str__(self):
        return "Error: {}".format(self.description)


@dataclass(frozen=True)
class Result:
    """
    simple result type functional programming style
    """

    state: Union[object, Error]

    def __bool__(self) -> bool:
        return isinstance(self.state, Error)

    def __str__(self):
        if not isinstance(self.state, Error):
            return "Successfull: {}".format(self.state)
        return str(self.state)


def ok(arg: object) -> Result:
    return Result(state=arg)


def error(arg: str) -> Result:
    return Result(state=Error(arg))


def load_config(dir: Result) -> Directory:
    """
    parse config from toml.
    """
    if dir:
        return dir
    dir = dir.state
    with open(dir, mode="rb") as fp:
        config = tomllib.load(fp)
    return ok(map_config_to_obj(config))


def map_config_to_obj(dict_conf: dict) -> Config:
    """
    map config dict to dto for sleeker code
    """
    return Config.from_dict(dict_conf)


def new_env(config: Config, name: str) -> Result:
    """
    genereate new venv
    """
    a = get_names_as_list(config.dirs.bin_dir)
    if name in get_names_as_list(config.dirs.bin_dir) + get_system_bins():
        return error("selected name is already used please choose different name")

    _ = os.system(  # check res
        "python{} -m venv {}".format(config.version, config.dirs.install / name)
    )
    if config.create_bin:
        os.symlink(config.dirs.install / name, config.dirs.bin_dir / name)
    return ok("created {} successfully".format(name))


def remove_env(config: Config, name: str) -> Result:
    """
    removes env by name
    """
    if not os.path.exists(config.dirs.install / name):
        return error("Given environment to remove does not exist")
    shutil.rmtree(config.dirs.install / name)  # removes all subcontet plus folder
    os.remove(config.dirs.bin_dir / name)
    return ok("removed {} successfully".format(name))


def get_names_as_list(path: Path) -> tuple[str]:
    return tuple(os.listdir(path))


def get_system_bins() -> Tuple[str]:
    """
    messy onliner to get all bin names stored in PATH
    """
    return tuple(
        itertools.chain.from_iterable(
            (
                os.listdir(_path)
                for _path in os.environ["PATH"].split(":")
                if os.path.exists(_path)
            )
        )
    )


def list_envs(config: Config) -> Result:
    bin_names = get_names_as_list(config.dirs.bin_dir)
    print("Environment names:")
    for i, n in enumerate(bin_names):
        print("{}: {}".format(i, n))
    return ok("listed_dirs")


def match_user_input(args: argparse.Namespace, config: Config) -> Result:
    """
    Matches the namespace obj into a curried functions
    """
    # modding vars
    if hasattr(args, "version"):  # args.version:
        config = replace(config, version=args.version)
    if hasattr(args, "path"):
        config = replace(config, dirs=replace(config.dirs, install=args.path))

    # matching usecase
    match args:
        case argparse.Namespace(list=True):  # args.list if args.list:
            return list_envs(config)
        case argparse.Namespace(new=name):
            return new_env(config, name)
        case argparse.Namespace(remove=name):
            return remove_env(config, name)
        case _:
            return error("Not able to parse user input. used -h to get help")


def find_prj_dir():
    execution_path = pathlib.Path(__file__).absolute()
    if os.path.islink(execution_path):
        execution_path = Path(os.readlink(execution_path))
    if os.path.exists(execution_path):
        return ok(execution_path.parent.parent / Path("config.toml"))
    return error(
        "config file not found. Make sure to place config.toml in project folder"
    )


def main() -> None:
    config = load_config(find_prj_dir())
    if bool(config):
        print(config)
        return
    config = config.state
    parser = argparse.ArgumentParser(
        description="Create new python virtual environment",
        argument_default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--new",
        metavar="N",
        type=str,
        help="name new for venv",
    )
    parser.add_argument(
        "--remove",
        metavar="R",
        type=str,
        help="name of venv to be removed",
    )
    parser.add_argument(
        "--version",
        metavar="V",
        type=float,
        help="install venv with given python version",
    )
    parser.add_argument(
        "--path",
        metavar="P",
        type=str,
        help="install in custom dir. If not given std path defined in config.toml is used ",
    )
    parser.add_argument(
        "--list", help="list all envs by given regex", action="store_true"
    )
    args = parser.parse_args()
    result = match_user_input(args=args, config=config)

    print(result)
    return


if __name__ == "__main__":
    # config = load_config(find_prj_dir())
    main()
    # args = argparse.Namespace(new="test1")
    # result = match_user_input(args=args, config=config.state)
    # print(result)
