#!/usr/bin/env python
##
# @file       aes.py
# @author     cwichel
# @date       2021
# @copyright  The MIT License (MIT)
# @brief      Simple AES encryption/decryption utilities.
# =============================================================================

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from typing import Type, Union


class AES:
    """Simple AES encryption / decryption utility.
    """
    def __init__(self, key: bytearray, iv: bytearray) -> None:
        """Class constructor.

        Args:
            key (bytearray): AES key
            iv (bytearray): Initialization vector.
        """
        self.cipher = Cipher(
            algorithm=algorithms.AES(key=key),
            mode=modes.CBC(initialization_vector=iv),
            backend=default_backend()
            )

    def encrypt(self, data: Union[str, bytearray], size: int) -> bytearray:
        """Encrypt data.

        Args:
            data (Union[str, bytearray]): Data to be encrypted.
            size (int): Define the output size in bytes.

        Returns
            bytearray: Encrypted data.
        """
        # Prepare data
        if isinstance(data, str):
            data = bytearray(data.encode(encoding='utf-8'))

        # Apply padding (if needed)
        padded = data[0:size] + bytearray(size - len(data))

        # Encrypt
        encryptor = self.cipher.encryptor()
        enc = encryptor.update(data=padded) + encryptor.finalize()
        return enc

    def decrypt(self, data: bytearray, dtype: Type[Union[str, bytearray]] = bytearray) -> Union[str, bytearray]:
        """Decrypt data.

        Args:
            data (bytearray): Data to be decrypted.
            dtype (Type[Union[str, bytearray]]): Define the output type.

        Returns
            Union[str, bytearray]: Decrypted data.
        """
        # Decrypt
        decryptor = self.cipher.decryptor()
        dec = decryptor.update(data) + decryptor.finalize()
        dec = dec.split(b'\x00')[0]
        if dtype == str:
            dec = dec.decode(encoding='utf-8', errors='ignore')
        return dec
