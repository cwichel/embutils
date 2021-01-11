import os
from pathlib import Path
from typing import Union
from embutils.utils.base import path_check_file


class BinaryFile:
    """Define a simple binary file utilities.
    """
    FMT_ERR:    str = 'BinaryFile: {}'

    def __init__(self, path: Union[None, str, Path] = None):
        """Initializes the binary file.

        Args:
            path (Union[None, str, Path]): Path to the target file.
        """
        # Initialize attribute
        self._path: Union[None, Path] = None
        self.path = path

    def __repr__(self) -> str:
        """Class representation string.

        Returns:
            str: Class representation.
        """
        msg = '<{}: path={}>'.format(self.__class__.__name__, self._path)
        return msg

    # Properties ================================
    @property
    def exist(self) -> bool:
        """Return if the file is set and exists.

        Returns:
            bool: True if file available, false otherwise.
        """
        check, _ = path_check_file(path=self._path, required=True)
        return check

    @property
    def path(self) -> Union[None, Path]:
        """Binary file path.

        Returns:
            Union[None, Path]: Path to the target file.
        """
        return self._path

    @path.setter
    def path(self, path: Union[None, str, Path]) -> None:
        """Set the binary file path.

        Args:
            path (Union[None, str, Path]): Path to the target file.
        """
        # Empty path
        if path is None:
            self._path = None
            return

        # Process path
        path = Path(path)
        check, msg = path_check_file(path=path)
        if not check:
            raise ValueError(self.FMT_ERR.format(msg))
        self._path = path

    # API =======================================
    def read(self) -> bytearray:
        """Read the contents of the file.

        Returns:
            bytearray: File content.
        """
        # Check if the file is available...
        check, msg = path_check_file(path=self._path, required=True)
        if not check:
            raise ValueError(self.FMT_ERR.format(msg))

        # Read the file data
        with self._path.open('rb') as file:
            data = bytearray(file.read())
        return data

    def write(self, data: bytearray) -> int:
        """Write the data on the file.

        NOTE: This operation overwrites the file contents.

        Args:
            data (bytearray): Bytes to be stored on the file.

        Returns:
            int: Number of bytes that had been written.
        """
        # Check if the file is available...
        check, msg = path_check_file(path=self._path)
        if not check:
            raise ValueError(self.FMT_ERR.format(msg))

        # Write the data on the file (overwrite)
        with self._path.open('wb') as file:
            byte_num = file.write(data)
        return byte_num

    def truncate(self, mod: int = 16) -> None:
        """Alter the file to have a size multiple of mod.

        NOTE: This method don't remove data. It increases the file.

        Args:
            mod (int): Module. The size of the file will be a multiple of this number.
        """
        # Check if the file is available...
        check, msg = path_check_file(path=self._path)
        if not check:
            raise ValueError(self.FMT_ERR.format(msg))

        # Truncate the file
        with self._path.open('ab') as file:
            file_size = file.tell()
            diff_size = file_size % mod
            new_size  = file_size + (mod - diff_size) if diff_size else 0
            file.truncate(new_size)

    def remove(self) -> None:
        """Remove (delete) the file.
        """
        if self.exist:
            os.remove(self._path)

    def get_bytes(self, size: int, offset: int = 0) -> bytearray:
        """Get 'size' number of bytes starting on position
        'offset' from the file.

        Args:
            size (int): Number of bytes to be retrieved from the file.
            offset (int): Reading process starting position.

        Returns:
            bytearray: Bytes read from the file.
        """
        # Check the file contents
        d_buff = self.read()
        d_size = len(d_buff)
        if d_size == 0:
            raise BufferError(self.FMT_ERR.format('File is empty!'))

        # Check if the sufficient data is available
        if (size + offset - 1) > d_size:
            msg = 'Not enough data on file. Required data indexes exceed the buffer size.'
            raise BufferError(self.FMT_ERR.format(msg))

        # Return the data
        return d_buff[offset:(offset + size)]

    def set_bytes(self, data: bytearray, offset: int = 0) -> int:
        """Set the bytes on offset with the contents of data.

        Args:
            data (int): Bytes to be stored / set on file.
            offset (int): Reading process starting position.

        Returns:
            bytearray: Number of bytes that had been written.
        """
        # Check data size
        size = len(data)
        if size != 0:
            # Get the bytes from file
            buff = self.read()
            if len(buff) < offset:
                msg = 'The specified offset exceed the file size. The data cant be write.'
                raise BufferError(self.FMT_ERR.format(msg))

            # Set the new bytes and update the file
            buff[offset:(offset + size)] = data
            self.write(buff)
        return size
