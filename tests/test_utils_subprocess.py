#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Subprocess usage test.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

import os
import unittest

from io import StringIO
from unittest.mock import patch

from embutils.utils import execute


# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------
class TestSubprocess(unittest.TestCase):
    """
    Test subprocess utilities.
    """
    def test_01_execute(self):
        """
        Check if the execute command works correctly.
        """
        cmd = "python --version"

        # Execute
        ret = execute(cmd=cmd, pipe=False)
        assert "Python" in ret.stdout

        ret = execute(cmd="unknown_command", pipe=False)
        assert (ret.returncode != 0) and (len(ret.stderr) > 0)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            execute(cmd=cmd, pipe=True)
            assert f"Executing:\nCWD: {os.getcwd()}\nCMD: {cmd}\nOutput:" in fake_out.getvalue()


# -->> Execute <<----------------------
if __name__ == '__main__':
    unittest.main()
