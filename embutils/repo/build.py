#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Project build utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

import shutil as su
import subprocess as sp

from ..utils.common import TPPath
from ..utils.path import Path
from ..utils.subprocess import execute


# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------
def get_exec(name: str) -> Path:
    """
    Get executable path.

    :param str name:    Executable name.

    :return: Executable path.
    :rtype: Path

    :raises FileNotFoundError:  Executable not found in PATH.
    """
    find = su.which(name)
    if find is None:
        raise FileNotFoundError(f"Unable to find {name} executable on PATH!")
    return Path(find)


def build_cubeide(
        name: str, config: str, project: TPPath, workspace: TPPath, indexer: bool = False, clean: bool = True,
        log: TPPath = None, pipe: bool = False, cwd: TPPath = None
        ) -> sp.CompletedProcess:
    """
    Calls the STM32 CubeIDE headless builder on the specified project.

    :note:

        - stm32cubeidec executable must be in the PATH.
        - You cannot build if the workspace is already in use.
        - Reference: https://gnu-mcu-eclipse.github.io/advanced/headless-builds/

    :param str name:            Project name.
    :param str config:          Build configuration to be used. Ex: Debug, Release.
    :param TPPath project:      Path to CubeIDE project.
    :param TPPath workspace:    Path to CubeIDE workspace.
    :param bool indexer:        Runs the indexer on build.
    :param bool clean:          Performs a clean build.
    :param TPPath log:          Path to store the build logs.
    :param bool pipe:           Enable pipe output to terminal.
    :param TPPath cwd:          Execution CWD.

    :return: Execution results.
    :rtype: sp.CompletedProcess
    """
    # Validate paths
    wsp = Path.validate_dir(path=workspace)
    prj = Path.validate_dir(path=project, must_exist=True)
    log = Path.validate_dir(path=log, none_ok=True)
    # Prepare
    exe = get_exec(name="stm32cubeidec")
    idx = "" if indexer else "-no-indexer"
    bld = "-cleanBuild" if clean else "-build"
    # Execute
    cmd = f"{exe} --launcher.suppressErrors -nosplash -application org.eclipse.cdt.managedbuilder.core.headlessbuild " \
          f"-data \"{wsp}\" -import \"{prj}\" {bld} \"{name}/{config}\" {idx}"
    res = execute(cmd=cmd, pipe=pipe, log=log, cwd=cwd)
    if not pipe and res.returncode:
        print(f"Command:\n{cmd}\nFailed with error:\n{res.stderr}")
    return res


def build_iar(
        config: str, project: TPPath, clean: bool = True,
        log: TPPath = None, pipe: bool = False, cwd: TPPath = None
        ) -> sp.CompletedProcess:
    """
    Calls the IAR headless builder on the specified project.

    :note:

        - IarBuild executable must be in the PATH.
        -

    :param str config:          Build configuration to be used. Ex: Debug, Release.
    :param TPPath project:      Path to EWARM project.
    :param bool clean:          Performs a clean build.
    :param TPPath log:          Path to store the build logs.
    :param bool pipe:           Enable pipe output to terminal.
    :param TPPath cwd:          Execution CWD.

    :return: Execution results.
    :rtype: sp.CompletedProcess
    """
    # Validate paths
    prj = Path.validate_file(path=project, must_exist=True)
    log = Path.validate_dir(path=log, none_ok=True)
    # Prepare
    bld = "-build" if clean else "-make"
    # Execute
    exe = get_exec(name="IarBuild")
    cmd = f"{exe} \"{prj}\" {bld} \"{config}\""
    res = execute(cmd=cmd, pipe=pipe, log=log, cwd=cwd)
    if not pipe and res.returncode:
        print(f"Command:\n{cmd}\nFailed with error:\n{res.stderr}")
    return res


# -->> Export <<-----------------------
__all__ = [
    "get_exec",
    "build_cubeide",
    "build_iar",
    ]
