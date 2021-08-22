#!/usr/bin/python
# -*- coding: ascii -*-
"""
Project build utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
import subprocess
from pathlib import Path


# -->> Definitions <<------------------


# -->> API <<--------------------------
def build_iar(config: str, project: Path) -> None:
    """
    Calls the IAR headless builder on the specified project.

    ::note:

        - IarBuild executable must be in the PATH.

    :param str config:      Build configuration to be used. Ex: Debug, Release.
    :param Path project:    Path to EWARM project.
    """
    cmd = f'IarBuild "{project}" -build "{config}"'
    _execute(cmd=cmd)


def build_cubeide(name: str, config: str, project: Path, workspace: Path) -> None:
    """
    Calls the STM32 CubeIDE headless builder on the specified project.

    ::note:

        - stm32cubeidec executable must be in the PATH.
        - You cannot build if the workspace is already in use.
        - Reference: https://gnu-mcu-eclipse.github.io/advanced/headless-builds/

    :param str name:        Project name.
    :param str config:      Build configuration to be used. Ex: Debug, Release.
    :param Path project:    Path to CubeIDE project.
    :param Path workspace:  Path to CubeIDE workspace.
    """
    cmd = f'stm32cubeidec --launcher.suppressErrors -nosplash ' \
          f'-application org.eclipse.cdt.managedbuilder.core.headlessbuild ' \
          f'-data "{workspace}" -cleanBuild "{name}/{config}" -import "{project}'
    _execute(cmd=cmd)


def _execute(cmd: str) -> None:
    """
    Executed the command on the terminal.

    :param str cmd: Command to be executed.
    """
    print(f'Executing:\n"{cmd}"\nOutput:')
    subprocess.call(cmd, shell=True)
