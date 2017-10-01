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
    # Vaults URLs
    url(
        r'^$',
        views.VaultListView.as_view(),
        name="list"
    ),
    url(
        r'^create$',
        views.VaultCreateView.as_view(),
        name="create"
    ),
    url(
        r'^delete$',
        views.VaultDeleteView.as_view(),
        name="delete"
    ),
    url(
        r'^restore$',
        views.VaultRestoreView.as_view(),
        name="restore"
    ),
    url(
        r'^(?P<slug>[\w-]+)/$',
        views.VaultDetailView.as_view(),
        name="detail"
    ),
    url(r'^(?P<slug>[\w-]+)/update$',
        views.VaultUpdateView.as_view(),
        name="update"
        ),
]
