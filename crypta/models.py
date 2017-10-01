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
import binascii

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from crypta import managers
from crypta.mixins import models as mixins
from crypta.utils import crypt, tokens, mail
from crypta.utils.models import get_invite_expires_on, unique_slugify

try:  # pragma: no cover
    from django.core.urlresolvers import reverse
except ImportError:  # pragma: no cover
    from django.urls import reverse

ROLES = (
    ("owner", _("Owner")),    # Read, Write, Exclude
    ("admin", _("Admin")),    # Read, Write
    ("member", _("Member")),  # Read
)

ROLES_MAP = dict(ROLES)


class Vault(mixins.SoftDeleteMixin):
    name = models.CharField(max_length=100, verbose_name=_("Vault Name"))
    pub_key = models.BinaryField(blank=False, null=False)
    slug = models.SlugField(
        max_length=100, db_index=True, unique=True, blank=False, null=False
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='Membership',
        through_fields=('vault', 'member'),
        related_name="vaults",
        related_query_name="vault",
        blank=False
    )

    objects = managers.VaultManager()

    class Meta:
        default_permissions = ()
        verbose_name = _("Vault")
        verbose_name_plural = _("Vaults")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self.name, type(self))

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('vault:detail', kwargs={'slug': self.slug})

    @property
    def owner(self):
        return self.owners.first()

    @property
    def owners(self):
        return self.members.filter(
            membership__vault=self, membership__role='owner'
        ).order_by('membership__joined_on')

    def __str__(self):
        return _("Vault({0.name}:{0.slug})").format(self)


class Secret(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    data = models.BinaryField(blank=False, null=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    vault = models.ForeignKey(
        Vault, on_delete=models.CASCADE,
        related_name="secrets",
        related_query_name="secret",
    )

    class Meta:
        default_permissions = ()
        verbose_name = _("Secret")
        verbose_name_plural = _("Secrets")

    @property
    def hex_data(self):
        return binascii.hexlify(self.data)

    def get_absolute_url(self):
        return reverse('secret:detail', args=[self.pk])

    def __str__(self):
        return _("Secret({0.name}@{0.vault})").format(self)


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
    temporary_key = models.BinaryField(blank=False, null=True)
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

    def accept(self):
        self.joined_on = timezone.now()
        self.accepted = True
        self.temporary_key = None
        self.save()

        email = mail.VaultInviteAcceptedEmail(
            to=self.inviter.email,
            context={
                'inviter_name': self.inviter.first_name,
                'invitee_name': self.invitee.first_name,
                'vault_name': self.vault.name,
                'role': self.get_role_display(),
            },
            invitee_name=self.invitee.first_name,
        )
        email.send()

    def get_absolute_url(self):
        return reverse('invite:accept', kwargs={'pk': self.pk})

    def renew(self):
        self.expires_on = get_invite_expires_on()
        self.save()

    def resend(self, inviter, password):
        token = tokens.random_token()
        inviter_priv_key = self.vault.memberships.get(
            member=inviter, excluded=False
        ).priv_key

        self.temporary_key = crypt.change_password(
            inviter_priv_key, password, token
        )

        email = mail.VaultInviteEmail(
            to=self.invitee.email,
            context={
                'role': self.role,
                'token': token,
                'invite_pk': self.pk,
                'vault_name': self.vault.name,
                'inviter': self.inviter.first_name,
                'invitee': self.invitee.first_name,
            },
        )
        email.send()
        self.save()

    @property
    def is_expired(self):
        return timezone.now() > self.expires_on

    @property
    def days_to_expire(self):
        if self.accepted:
            return 0

        delta = self.expires_on - timezone.now()
        if delta.days < 0:
            return 0
        return delta.days

    @property
    def status(self):
        if self.accepted:
            return _("Accepted")

        if self.is_expired:
            return _("Expired")

        return _("Pending")

    def __str__(self):
        return _("Invite({0.inviter}->{0.invitee}@{0.vault})").format(self)


class Membership(mixins.SoftDeleteMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    priv_key = models.BinaryField(blank=False, null=False)
    role = models.CharField(choices=ROLES, max_length=50)
    joined_on = models.DateTimeField(auto_now_add=True)

    objects = managers.MembershipManager()

    class Meta:
        default_permissions = ()
        verbose_name = _("Membership")
        verbose_name_plural = _("Memberships")
        unique_together = ('member', 'vault')

    def change_role(self, old_role, user, commit=True):
        if not commit:  # pragma: no cover
            return
        self.save()

        mail_class = mail.MembershipPromotionEmail
        if (old_role == 'owner') \
                or (old_role == 'admin' and self.role == 'member'):
            mail_class = mail.MembershipDemotionEmail

        email = mail_class(
            to=self.member.email,
            context={
                'membership': self,
                'new_role_display': ROLES_MAP[self.role],
                'old_role_display': ROLES_MAP[old_role],
                'user': user,
            },
        )
        email.send()

    def __str__(self):
        return _("Membership({0.member}@{0.vault.slug}:{0.role})").format(self)
