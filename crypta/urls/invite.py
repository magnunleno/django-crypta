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
    url(
        r'^vault/(?P<slug>[\w-]+)/invite$',
        views.VaultInviteListView.as_view(),
        name="by-vault"
    ),
    url(
        r'^vault/(?P<slug>[\w-]+)/create$',
        views.InviteCreateView.as_view(),
        name="create"
    ),
    url(
        r'^(?P<pk>[0-9a-f-]+)/accept$',
        views.InviteAcceptView.as_view(),
        name="accept"
    ),
    url(
        r'^revoke$',
        views.InviteRevokeView.as_view(),
        name="revoke"
    ),
    url(
        r'^renew$',
        views.InviteRenewView.as_view(),
        name="renew"
    ),
    url(
        r'^(?P<pk>[0-9a-f-]+)/resend$',
        views.InviteResendView.as_view(),
        name="resend"
    ),
]
