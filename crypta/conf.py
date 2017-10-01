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

from appconf import AppConf
from django.conf import settings  # NOQA


class CryptaConf(AppConf):
    __secret_adpater_class = None

    TEMPLATE_EXTENSION = "html"
    TOKEN_SIZE = 16
    DAYS_TO_EXPIRE_INVITE = 30
    SECRET_ADAPTER = 'crypta.adapters.JsonSecretAdapter'
    KEY = "crypta.utils.crypt.SecretUpdateTokenGenerator"
    SECRET_TOKEN_TIMEOUT = 3 * 60

    @classmethod
    def get_secret_adapter(kls):  # pragma: no cover
        if kls.__secret_adpater_class:
            return kls.__secret_adpater_class

        class_name = kls.SECRET_ADAPTER.split('.')[-1]
        module_name = '.'.join(kls.SECRET_ADAPTER.split('.')[:-1])
        try:
            mod = __import__(module_name, fromlist=[class_name])
        except ImportError:
            raise ImportError("Couldn't find the following adapter: {}".format(
                kls.SECRET_ADAPTER
            ))
        kls.__secret_adpater_class = getattr(mod, class_name)
        return kls.__secret_adpater_class

    class Meta:
        proxy = True

settings = CryptaConf()  # NOQA
