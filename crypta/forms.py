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

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from crypta import models
from crypta.utils import crypt
from crypta.conf import settings
from crypta.mixins import forms as mixins

User = get_user_model()
SecretAdapter = settings.get_secret_adapter()


class UpdateVaultForm(mixins.SlugFormMixin, forms.ModelForm):
    ''' Form that updates an existing Vault '''
    class Meta:
        model = models.Vault
        localized_fields = ('__all__')
        fields = [
            'name',
            'slug',
        ]


class CreateVaultForm(mixins.PasswordConfirmFormMixin, UpdateVaultForm):
    '''
    Form creates a Vault. Similar to UpdateVaultForm, but it requires
    a passowrd
    '''
    pass
