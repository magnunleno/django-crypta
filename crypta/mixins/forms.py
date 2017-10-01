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
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class SlugFormMixin(forms.Form):
    slug = forms.CharField(required=False)

    def save(self, commit=True):
        # Hack for Django-1.9
        obj = super().save(commit=False)
        obj.slug = self.cleaned_data['slug']
        obj.save()
        return obj


class PasswordConfirmFormMixin(forms.Form):
    password = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data['password']
        if self.user.check_password(password):
            return password
        raise ValidationError(
            _("Please, inform your password correctly!")
        )
