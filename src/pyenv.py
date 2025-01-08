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



PYENV_DIR = Path.home() / Path(".pyenvs") if os.environ.get("PYENV_DIR") is None else Path(os.environ.get("PYENV_DIR"))

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


def get_default_version() -> str:
    """
    get the default python version
    """
    version_numers = os.popen('python3 --version').read().strip().split()[1].split(".")
    if len(version_numers) < 2:
        return version_numers[0] + ".0"
    return version_numers[0] + "." + version_numers[1]
def get_config() -> Config:
    """
    map config dict to dto for sleeker code
    """
    return Config(
        dirs=Directory(install=PYENV_DIR, bin_dir=PYENV_DIR / Path("bin")),
        version=get_default_version(),
        create_bin=True)


def new_env(config: Config, name: str) -> Result:
    """
    genereate new venv
    """
    a = get_names_as_list(config.dirs.bin_dir)
    if name in get_names_as_list(config.dirs.bin_dir) + get_system_bins():
        return error("selected name is already used please choose different name")

    result = os.system(
        "python{} -m venv {}".format(config.version, config.dirs.install / name)
    )
    if result != 0:
        return error("Failed to create virtual environment")
    if config.create_bin:
        full_name = str(name) + "/bin/activate"
        os.symlink(config.dirs.install / full_name, config.dirs.bin_dir / name)
    return ok("created {} successfully".format(name))


def remove_env(config: Config, name: str) -> Result:
    """
    removes env by name
    """
    if not os.path.exists(config.dirs.install / name):
        return error("Given environment to remove does not exist")
    os.unlink(config.dirs.bin_dir / name)
    shutil.rmtree(config.dirs.install / name)  # removes all subcontet plus folder
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
        if args.version is not None:
            config = replace(config, version=args.version)
    if hasattr(args, "path"):
        if args.path is not None:
            if not os.path.exists(args.path):
                return error("Given path does not exist")
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
    config = get_config()
    
    # Create parser with subcommands
    parser = argparse.ArgumentParser(
        description="Python virtual environment manager",
        argument_default=argparse.SUPPRESS,
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # New environment command
    new_parser = subparsers.add_parser('new', help='Create new virtual environment')
    new_parser.add_argument('name', help='Name for the new environment')
    new_parser.add_argument('--version', type=str, help='Python version to use')
    new_parser.add_argument('--path', type=str, help='Custom installation directory')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove virtual environment')
    remove_parser.add_argument('name', help='Name of environment to remove')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List virtual environments')
    list_parser.add_argument('--pattern', help='Filter environments by regex pattern')
    
    args = parser.parse_args()
    
    # Convert subcommand format to current format
    namespace_args = argparse.Namespace()
    if args.command == 'new':
        namespace_args.new = args.name
        if hasattr(args, 'version'):
            namespace_args.version = args.version
        if hasattr(args, 'path'):
            namespace_args.path = args.path
    elif args.command == 'remove':
        namespace_args.remove = args.name
    elif args.command == 'list':
        namespace_args.list = True
    
    result = match_user_input(args=namespace_args, config=config)
    print(result)


if __name__ == "__main__":
    # config = load_config(find_prj_dir())
    main()
    # args = argparse.Namespace(new="test1")
    # result = match_user_input(args=args, config=config.state)
    # print(result)
