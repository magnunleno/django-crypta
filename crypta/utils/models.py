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

import datetime
import re

from django.utils import timezone
from django.utils.text import slugify

from crypta.conf import settings


def get_invite_expires_on():
    return timezone.now() + datetime.timedelta(
        days=settings.DAYS_TO_EXPIRE_INVITE
    )


def unique_slugify(name, model):
    slug = slugify(name)

    if not model.objects.filter(slug=slug).exists():
        return slug

    occurences = list(model.objects.filter(
        slug__startswith=slug
    ).values_list('slug', flat=True))

    occurences.remove(slug)

    if len(occurences) == 0:
        return slug + '-1'

    slug_re = re.compile('^' + slug + '-[0-9]+$')
    occurences = sorted([int(o.split(slug)[-1].split('-')[-1])
                         for o in occurences if slug_re.match(o)])
    last = occurences[-1]
    last += 1
    return '{}-{}'.format(slug, last)
