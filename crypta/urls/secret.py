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
    from django.conf.urls import url
except ImportError:  # pragma: no cover
    from django.conf.urls import url

from crypta import views

urlpatterns = [
    url(r'^vault/(?P<slug>[\w-]+)/create$',
        views.SecretCreateView.as_view(),
        name="create"
        ),
    url(r'^(?P<pk>[0-9a-f-]+)$',
        views.SecretDetailView.as_view(),
        name="detail"
        ),
    url(r'^secret/(?P<pk>[\w-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.SecretUpdateView.as_view(),
        name="update"
        ),
    url(
        r'^(?P<pk>[0-9a-f-]+)/delete$',
        views.SecretDeleteView.as_view(),
        name="delete"
    ),
]
