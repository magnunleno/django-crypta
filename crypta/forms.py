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
    a passowrd '''
    pass


class CreateInviteForm(mixins.PasswordConfirmFormMixin, forms.ModelForm):
    ''' Form that creates a new invite. '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['invitee'].queryset = User.objects.exclude(pk=self.user.pk)

    class Meta:
        model = models.Invite
        localized_fields = ('__all__')
        fields = [
            'invitee',
            'role',
        ]


class AcceptInviteForm(mixins.PasswordConfirmFormMixin):
    ''' Form that accepts a invite. '''
    token = forms.CharField(label=_('Token'), max_length=100)

    def __init__(self, *args, **kwargs):
        self.invite = kwargs.pop('invite', None)
        super().__init__(*args, **kwargs)

    def clean_token(self):
        token = self.cleaned_data['token']
        if crypt.test_private_key_password(self.invite.temporary_key, token):
            return token
        raise ValidationError(
            _("Sorry, but this token is invalid!")
        )


class UpdateMembershipForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.vault = kwargs.pop('vault', None)
        self.user_membership = self.user.memberships.get(
            vault=self.vault, member=self.user
        )
        super().__init__(*args, **kwargs)

    def clean_role(self):
        new_role = self.cleaned_data['role']

        if self.user_membership.role == 'owner':
            return new_role

        if self.user_membership.role == 'member':  # pragma: no cover
            raise ValidationError(_(
                "Sorry, but Members can't promote/demote other users."
            ))

        # User role is Admin
        if self.instance.role == 'owner':
            raise ValidationError(_(
                "Sorry, but only owners can update other owner's membership."
            ))

        if new_role == 'owner':
            raise ValidationError(_(
                "Sorry, but only owners can promote other members to owner."
            ))

        return new_role

    def save(self, commit=True):
        if 'role' not in self.changed_data:  # pragma: no cover
            return self.instance

        self.instance.change_role(self.initial['role'], self.user, commit)
        return self.instance

    class Meta:
        model = models.Membership
        localized_fields = ('__all__')
        fields = ['role']


class BaseSecretForm(forms.Form):
    data = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        self.vault = kwargs.pop('vault', None)
        super().__init__(*args, **kwargs)

    def clean_data(self):
        data = self.cleaned_data['data']
        if not SecretAdapter.validate(data):
            raise ValidationError(_("Invalid secret format."))

        encrypted_data = crypt.encrypt(self.vault.pub_key, data)
        return encrypted_data

    def save(self, commit=True):
        if 'data' not in self.changed_data:  # pragma: no cover
            return self.instance

        if getattr(self.instance, 'vault', None) is None:
            self.instance.vault = self.vault

        self.instance.data = self.cleaned_data['data']

        if commit:  # pragma: no cover
            self.instance.save()

        return self.instance


class CreateSecretForm(BaseSecretForm, forms.ModelForm):
    class Meta:
        model = models.Secret
        localized_fields = ('__all__')
        fields = [
            'name',
        ]


class UpdateSecretForm(BaseSecretForm, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs['vault'] = kwargs['instance'].vault
        super().__init__(*args, **kwargs)

    class Meta:
        model = models.Secret
        localized_fields = ('__all__')
        fields = []


class SecretPasswordForm(mixins.PasswordConfirmFormMixin, forms.ModelForm):
    class Meta:
        model = models.Secret
        localized_fields = ('__all__')
        fields = ['vault']
