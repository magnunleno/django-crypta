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

from django.db import models, transaction

from crypta import querysets
from crypta.utils import crypt, tokens, mail


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


class InviteManager(models.Manager):
    _queryset_class = querysets.InviteQuerySet

    def pending(self):  # pragma: no cover
        return super().get_queryset().pending()

    def not_accepted(self):  # pragma: no cover
        return super().get_queryset().not_accepted()

    def from_vault_managed_by(self, user):  # pragma: no cover
        return super().get_queryset().from_vault_managed_by(user)

    @transaction.atomic
    def create(self, inviter, inviter_pass, invitee, role, vault, **kwargs):
        token = tokens.random_token()
        inviter_priv_key = vault.memberships.get(
            member=inviter, excluded=False
        ).priv_key

        invite = super().create(
            inviter=inviter, invitee=invitee, vault=vault, role=role,
            temporary_key=crypt.change_password(
                inviter_priv_key, inviter_pass, token
            ), **kwargs
        )

        email = mail.VaultInviteEmail(
            to=invitee.email,
            context={
                'role': role,
                'token': token,
                'invite_pk': invite.pk,
                'vault_name': vault.name,
                'inviter': inviter.first_name,
                'invitee': invitee.first_name,
            },
        )
        email.send()
        return invite
