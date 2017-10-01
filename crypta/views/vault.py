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

from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView, View)

from crypta import forms, models
from crypta.mixins import views as mixins
from crypta.conf import settings

try:  # pragma: no cover
    from django.core.urlresolvers import reverse_lazy
except ImportError:  # pragma: no cover
    from django.urls import reverse_lazy


class VaultListView(mixins.LoginRequiredMixin, ListView):
    "List all Vaults that has `request.user` as a member."
    model = models.Vault
    template_name = 'crypta/vault/index.' + settings.TEMPLATE_EXTENSION

    def get_queryset(self):
        self.queryset = self.model.objects
        if int(self.request.GET.get('excluded', '0')) == 0:
            self.queryset = self.queryset.active()

        self.queryset = self.queryset.with_member(self.request.user)
        return super().get_queryset()


class VaultCreateView(mixins.LoginRequiredMixin, CreateView):
    "Create a new Vault and add the current user as Owner."
    model = models.Vault
    form_class = forms.CreateVaultForm
    template_name = 'crypta/vault/create.' + settings.TEMPLATE_EXTENSION

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()

        models.Membership.objects.create_ownership(
            owner=self.request.user, vault=self.object,
            password=form.cleaned_data['password']
        )
        return HttpResponseRedirect(self.get_success_url())


class VaultDetailView(mixins.LoginRequiredMixin, DetailView):
    "Show the Vault details for all members"
    template_name = 'crypta/vault/detail.' + settings.TEMPLATE_EXTENSION
    model = models.Vault

    def get_object(self, queryset=None):
        # TODO: Verificar prefetch
        return get_object_or_404(
            self.model.objects.active().with_member(
                self.request.user
            ).prefetch_related(
                'members', 'memberships', 'secrets'
            ),
            slug=self.kwargs.get('slug', None),
        )


class VaultDeleteView(mixins.LoginRequiredMixin, DeleteView):
    "Allow the Owner to delete a Vault"
    success_url = reverse_lazy('vault:list')
    model = models.Vault
    http_method_names = ['post']

    def get_object(self, queryset=None):
        return get_object_or_404(
            self.model.objects.active().owned_by(self.request.user),
            pk=self.request.POST['pk'],
        )


class VaultRestoreView(mixins.LoginRequiredMixin, View):
    "Allow the Owner to restore a previously deleted a Vault"
    success_url = reverse_lazy('vault:list')
    model = models.Vault
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        vault = get_object_or_404(
            self.model.objects.excluded().owned_by(self.request.user),
            pk=request.POST['pk'],
        )

        vault.excluded = False
        vault.save()
        return HttpResponseRedirect(self.success_url)


class VaultUpdateView(mixins.LoginRequiredMixin, UpdateView):
    "Allow the Owner or the Admin to edit the vaults detail."
    model = models.Vault
    form_class = forms.UpdateVaultForm
    template_name = 'crypta/vault/update.' + settings.TEMPLATE_EXTENSION

    def get_success_url(self):
        return reverse_lazy('vault:detail', args=[self.object.slug])

    def get_object(self, queryset=None):
        return get_object_or_404(
            self.model.objects.managed_by(self.request.user).active(),
            slug=self.kwargs.get('slug', None),
        )
