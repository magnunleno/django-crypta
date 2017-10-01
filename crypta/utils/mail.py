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

from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from crypta.conf import settings


class BaseEmail:
    subject = None
    txt_template = None
    html_template = None

    def __init__(self, to, context, *args, **kwargs):
        self.to = to
        self.context = context
        context['site'] = Site.objects.get_current()

        self._html = None
        self._text = None
        self._args = args
        self._kwargs = kwargs

    def get_subject(self):
        return self.subject

    def _render(self, template, context):
        try:
            rendered_template = render_to_string(template, self.context)
        except TemplateDoesNotExist:
            rendered_template = None
        return rendered_template

    def send(self, from_addr=None, fail_silently=False):
        if self.html_template:  # pragma: no coverage
            self._html = self._render(self.html_template, self.context)

        if self.txt_template:
            self._text = self._render(self.txt_template, self.context)

        if self._html is None and self._text is None:  # pragma: no coverage
            raise Exception(
                "Please informe at least one type of template (html or text)."
            )

        if isinstance(self.to, str):
            self.to = [self.to]

        if not from_addr:  # pragma: no coverage
            from_addr = getattr(settings, 'CRYPTA_EMAIL_FROM_ADDR')

        msg = EmailMultiAlternatives(
            self.get_subject(), self._text, from_addr, self.to
        )
        if self._html:  # pragma: no coverage
            msg.attach_alternative(self._html, 'text/html')
        msg.send(fail_silently)


class VaultInviteEmail(BaseEmail):
    subject = _("You've received a invite to join a Vault!")
    txt_template = 'crypta/mail/invite.txt'
    html_template = 'crypta/mail/invite.' + settings.TEMPLATE_EXTENSION


class VaultInviteAcceptedEmail(BaseEmail):
    subject = _("{0} accepted your invite!")
    txt_template = 'crypta/mail/invite_accepted.txt'
    html_template = 'crypta/mail/invite_accepted.' +\
        settings.TEMPLATE_EXTENSION

    def get_subject(self):
        return self.subject.format(
            self._kwargs.get('invitee_name', None)
        )
