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

try:  # pragma: no cover
    from django.conf.urls import url, include
except ImportError:  # pragma: no cover
    from django.conf.urls import url, include

urlpatterns = [
    url(r'^vault/', include('crypta.urls.vault', namespace="vault")),
    url(r'^invite/', include('crypta.urls.invite', namespace="invite")),
    url(r'^secret/', include('crypta.urls.secret', namespace="secret")),
    url(r'^membership/', include('crypta.urls.membership',
                                 namespace="membership")),
]

__all__ = ["secret", "vault", "invite", "membership"]
