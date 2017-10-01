#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of Django-Crypta.
#
# Django-Crypta is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Django-Crypta is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Django-Crypta.  If not, see <http://www.gnu.org/licenses/>.

import binascii
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from crypta.conf import settings


def gen_keys(passphrase):
    if isinstance(passphrase, str):  # pragma: no cover
        passphrase = passphrase.encode()

    priv_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    priv_key_bin = priv_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.BestAvailableEncryption(passphrase),
    )

    pub_key = priv_key.public_key()
    pub_key_bin = pub_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.PKCS1,
    )
    return (priv_key_bin, pub_key_bin)


# def extract_pub_key(private_key, password):
#     if isinstance(private_key, str):  # pragma: no cover
#         private_key = private_key.encode()
# 
#     if isinstance(password, str):  # pragma: no cover
#         password = password.encode()
# 
#     priv_key = serialization.load_pem_private_key(
#         private_key, password, default_backend()
#     )
#     pub_key = priv_key.public_key()
#     pub_key_bin = pub_key.public_bytes(
#         encoding=serialization.Encoding.PEM,
#         format=serialization.PublicFormat.PKCS1,
#     )
#     return pub_key_bin


def encrypt(public_key, secret):
    if isinstance(public_key, str):  # pragma: no cover
        public_key = public_key.encode()

    if isinstance(secret, str):  # pragma: no cover
        secret = secret.encode()

    pub_key = serialization.load_pem_public_key(
        public_key, default_backend()
    )

    return pub_key.encrypt(
        secret, padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


def decrypt(private_key, passphrase, ciphertext):
    if isinstance(private_key, str):  # pragma: no cover
        private_key = private_key.encode()

    if isinstance(passphrase, str):  # pragma: no cover
        passphrase = passphrase.encode()

    if isinstance(ciphertext, str):  # pragma: no cover
        ciphertext = ciphertext.encode()

    priv_key = serialization.load_pem_private_key(
        private_key, passphrase, default_backend()
    )

    return priv_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    ).decode()


def test_private_key_password(private_key, password):
    if isinstance(private_key, str):  # pragma: no cover
        private_key = private_key.encode()

    if isinstance(password, str):  # pragma: no cover
        password = password.encode()

    success = True
    try:
        serialization.load_pem_private_key(
            private_key, password, default_backend()
        )
    except ValueError:
        success = False
    return success


def change_password(private_key, old_password, new_password):
    if isinstance(private_key, str):  # pragma: no cover
        private_key = private_key.encode()

    if isinstance(old_password, str):  # pragma: no cover
        old_password = old_password.encode()

    if isinstance(new_password, str):  # pragma: no cover
        new_password = new_password.encode()

    priv_key = serialization.load_pem_private_key(
        private_key, old_password, default_backend()
    )
    return priv_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.BestAvailableEncryption(
            new_password
        ),
    )
