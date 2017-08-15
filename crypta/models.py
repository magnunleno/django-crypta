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

import uuid
from django.utils import timezone

from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from crypta.utils.models import get_invite_expires_on, unique_slugify
from crypta import managers


ROLES = (
    ("owner", _("Owner")),    # Read, Write, Exclude
    ("admin", _("Admin")),    # Read, Write
    ("member", _("Member")),  # Read
)


class Vault(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Vault Name"))
    slug = models.SlugField(max_length=100, db_index=True, unique=True,
                            blank=False, null=False)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='Membership',
        through_fields=('vault', 'member'),
        related_name="vaults",
        related_query_name="vault",
        blank=False
    )
    excluded = models.BooleanField(default=False)

    objects = managers.VaultManager()

    class Meta:
        default_permissions = ()
        verbose_name = _("Vault")
        verbose_name_plural = _("Vaults")

    def __str__(self):
        return _("{0.name} ({0.slug})").format(self)

    def get_absolute_url(self):
        return reverse(
            'vault-detail', kwargs={'slug': self.slug}
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self.name, Vault)

        super().save(*args, **kwargs)

    @property
    def owner(self):
        return self.members.get(
            membership__vault=self, membership__role='owner'
        )

    def delete(self):
        if not self.excluded:
            self.excluded = True
            self.save()


class Secret(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, db_index=True)
    data = models.BinaryField(blank=False, null=False)
    vault = models.ForeignKey(
        Vault, on_delete=models.CASCADE,
        related_name="secrets",
        related_query_name="secret",
    )

    class Meta:
        default_permissions = ()
        verbose_name = _("Secret")
        verbose_name_plural = _("Secrets")

    def __str__(self):
        return _("{0.name} (from {0.vault})").format(self)


class Invite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="vault_inviters",
        related_query_name="vault_inviter",
    )
    invitee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="vault_invitees",
        related_query_name="vault_invitee",
    )
    vault = models.ForeignKey(
        Vault, on_delete=models.CASCADE,
        related_name="invites",
        related_query_name="invite",
    )
    temporary_key = models.BinaryField(blank=False, null=False)
    invited_on = models.DateTimeField(auto_now_add=True)
    joined_on = models.DateTimeField(null=True)
    role = models.CharField(choices=ROLES, max_length=10)
    expires_on = models.DateTimeField(default=get_invite_expires_on)
    accepted = models.BooleanField(default=False)

    objects = managers.InviteManager()

    class Meta:
        default_permissions = ()
        verbose_name = _("Invite")
        verbose_name_plural = _("Invites")
        unique_together = ('vault', 'invitee')

    @property
    def is_expired(self):
        return timezone.now() > self.expires_on

    @property
    def status(self):
        if self.accepted:
            return _("Accepted")

        if self.is_expired:
            return _("Expired")

        return _("Pending")

    def __str__(self):
        return _("{0.invitee} invited for {0.vault} (by {0.inviter})").format(
            self
        )


class Membership(models.Model):
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="memberships",
        related_query_name="membership",
    )
    vault = models.ForeignKey(
        Vault, on_delete=models.CASCADE,
        related_name="memberships",
        related_query_name="membership",
    )
    pub_key = models.BinaryField(blank=False, null=False)
    priv_key = models.BinaryField(blank=False, null=False)
    role = models.CharField(choices=ROLES, max_length=50)
    excluded = models.BooleanField(default=False)

    objects = managers.MembershipManager()

    class Meta:
        default_permissions = ()
        verbose_name = _("Membership")
        verbose_name_plural = _("Memberships")
        unique_together = ('member', 'vault')

    def __str__(self):
        return _("{0.vault} ({0.member} as {0.role})").format(self)
