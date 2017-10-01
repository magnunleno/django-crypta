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
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Django-Crypta. If not, see <http://www.gnu.org/licenses/>.

from django.db import models


class BaseQuerySet(models.QuerySet):
    def active(self):
        return self.filter(excluded=False)

    def excluded(self):
        return self.filter(excluded=True)


class VaultQuerySet(BaseQuerySet):
    def owned_by(self, user):
        return self.filter(
            membership__member=user, membership__role='owner'
        )

    def managed_by(self, user):
        return self.filter(
            membership__member=user, membership__role__in=('owner', 'admin')
        )

    def with_member(self, user):
        return self.filter(
            membership__member=user, membership__excluded=False
        )
