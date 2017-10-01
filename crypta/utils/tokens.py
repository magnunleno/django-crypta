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

import os
import binascii

from datetime import datetime
from django.utils.http import base36_to_int, int_to_base36
from django.utils.crypto import constant_time_compare, salted_hmac

from crypta.conf import settings


def random_token(size=settings.TOKEN_SIZE):
    return binascii.b2a_hex(os.urandom(size))


# Based on: django.contrib.auth.tokens.PasswordResetTokenGenerator
class SecretUpdateTokenGenerator():
    key_salt = settings.CRYPTA_KEY
    secret = settings.SECRET_KEY

    def make_token(self, secret_obj, user):
        return self._make_token_with_timestamp(
            secret_obj, user, self._num_seconds(self._now())
        )

    def check_token(self, secret_obj, user, token):
        if not (user and token):
            return False

        try:
            ts_b36, hash = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        if not constant_time_compare(
                self._make_token_with_timestamp(secret_obj, user, ts),
                token
        ):
            return False

        if (self._num_seconds(self._now()) - ts) >=\
                settings.SECRET_TOKEN_TIMEOUT:
            return False

        return True

    def _make_token_with_timestamp(self, secret_obj, user, timestamp):
        ts_b36 = int_to_base36(timestamp)
        return "{}-{}".format(
            ts_b36,
            salted_hmac(
                self.key_salt,
                self._make_hash_value(secret_obj, user, timestamp),
                secret=self.secret,
            ).hexdigest()[::2]
        )

    def _make_hash_value(self, secret_obj, user, timestamp):
        if secret_obj.updated_on is None:
            update_timestamp = ''
        else:
            update_timestamp = secret_obj.updated_on.replace(
                microsecond=0, tzinfo=None
            )

        return str(user.pk) + secret_obj.hex_data.decode() +\
            str(update_timestamp) + str(timestamp)

    def _now(self):
        return datetime.now()

    def _num_seconds(self, dt):
        return int((dt - datetime(2001, 1, 1)).total_seconds())


secret_update_token_generator = SecretUpdateTokenGenerator()
