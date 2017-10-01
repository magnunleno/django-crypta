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

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import DeleteView, ListView, UpdateView

from crypta import forms, models
from crypta.mixins import views as mixins
from crypta.conf import settings

try:  # pragma: no cover
    from django.core.urlresolvers import reverse_lazy
except ImportError:  # pragma: no cover
    from django.urls import reverse_lazy


class VaultMembershipListView(mixins.LoginRequiredMixin, ListView):
    ''' List vault's membership '''
    model = models.Membership
    template_name = 'crypta/membership/by_vault.' + settings.TEMPLATE_EXTENSION

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vault'] = self.vault
        return context

    def get_queryset(self):
        self.vault = get_object_or_404(
            models.Vault.objects.managed_by(self.request.user),
            slug=self.kwargs.get('slug', None),
        )

        self.queryset = self.model.objects
        if int(self.request.GET.get('excluded', '0')) == 0:
            self.queryset = self.queryset.active()

        self.queryset = self.queryset.filter(vault=self.vault).exclude(
            member=self.request.user
        )
        return super().get_queryset()


class MembershipDeleteView(mixins.LoginRequiredMixin, DeleteView):
    ''' Deletes a membership '''
    model = models.Membership
    http_method_names = ['post']

    def get_success_url(self):
        return reverse_lazy('membership:by-vault', args=[self.vault.slug])

    def get_object(self, queryset=None):
        obj = get_object_or_404(
            self.model.objects,
            pk=self.request.POST['pk'],
            vault__membership__member=self.request.user,
            vault__membership__role__in=('owner', 'admin'),
            vault__excluded=False,
        )
        current_user_membership = self.model.objects.get(
            vault=obj.vault, member=self.request.user
        )

        if obj.member == self.request.user:
            raise Http404()

        if current_user_membership.role != 'owner' and obj.role == 'owner':
            raise Http404()

        self.vault = obj.vault
        return obj


class MembershipUpdateView(mixins.LoginRequiredMixin, UpdateView):
    ''' Updates an existing membership '''
    model = models.Membership
    form_class = forms.UpdateMembershipForm
    template_name = 'crypta/membership/update.' + settings.TEMPLATE_EXTENSION

    def get_success_url(self):
        return reverse_lazy(
            'membership:by-vault', args=[self.object.vault.slug]
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['vault'] = self.object.vault
        return kwargs

    def get_object(self, queryset=None):
        membership = get_object_or_404(
            self.model.objects.from_vault_managed_by(
                self.request.user
            ).active(),
            pk=self.kwargs.get('pk', None),
        )

        # Self promoting/demoting
        if self.request.user.pk == membership.member.pk:
            raise Http404()

        return membership
