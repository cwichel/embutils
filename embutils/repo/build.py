#!/usr/bin/python
# -*- coding: ascii -*-
"""
Project build utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------
from ..utils.path import TPPath, Path
from ..utils.subprocess import execute


# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------
def build_cubeide(name: str, config: str, project: TPPath, workspace: TPPath, indexer: bool = False,
                  log: TPPath = None, pipe: bool = False
                  ) -> None:
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
    :param TPPath log:          Path to store the build logs.
    :param bool pipe:           Enable pipe output to terminal.
    """
    # Validate paths
    workspace   = Path.validate_dir(path=workspace)
    project     = Path.validate_dir(path=project, must_exist=True)
    log         = Path.validate_dir(path=log, none_ok=True)

    # Build
    idx = "-no-indexer" if not indexer else ""
    cmd = f"stm32cubeidec --launcher.suppressErrors -nosplash {idx} " \
          f"-application org.eclipse.cdt.managedbuilder.core.headlessbuild " \
          f"-data '{workspace}' -cleanBuild '{name}/{config}' -import '{project}'"
    res = execute(cmd=cmd, pipe=pipe, log=log)
    if not pipe and res.returncode:
        print(f"Command:\n{cmd}\nFailed with error:\n{res.stderr}")


def build_iar(config: str, project: TPPath,
              log: TPPath = None, pipe: bool = False
              ) -> None:
    """
    Calls the IAR headless builder on the specified project.

    :note:

        - IarBuild executable must be in the PATH.

    :param str config:          Build configuration to be used. Ex: Debug, Release.
    :param TPPath project:      Path to EWARM project.
    :param TPPath log:          Path to store the build logs.
    :param bool pipe:           Enable pipe output to terminal.
    """
    # Validate paths
    project = Path.validate_dir(path=project, must_exist=True)
    log = Path.validate_dir(path=log, none_ok=True)

    # Build
    cmd = f'IarBuild "{project}" -build "{config}"'
    res = execute(cmd=cmd, pipe=pipe, log=log)
    if not pipe and res.returncode:
        print(f"Command:\n{cmd}\nFailed with error:\n{res.stderr}")


# -->> Export <<-----------------------
__all__ = [
    "build_cubeide",
    "build_iar",
    ]
