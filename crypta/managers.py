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

from django.db import models

from crypta import querysets
from crypta.utils import crypt


class BaseManager(models.Manager):
    def get_queryset(self):
        return self._queryset_class(self.model, using=self._db)

    def active(self):  # pragma: no cover
        return self.get_queryset().active()

    def excluded(self):  # pragma: no cover
        return self.get_queryset().excluded()


class VaultManager(BaseManager):
    _queryset_class = querysets.VaultQuerySet

    def owned_by(self, user):  # pragma: no cover
        return super().get_queryset().owned_by(user)

    def managed_by(self, user):  # pragma: no cover
        return super().get_queryset().managed_by(user)

    def with_member(self, user):  # pragma: no cover
        return super().get_queryset().with_member(user)
