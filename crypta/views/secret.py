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
from django.views.generic import (CreateView, DetailView, FormView, UpdateView,
                                  DeleteView)

try:  # pragma: no cover
    from django.core.urlresolvers import reverse_lazy
except ImportError:  # pragma: no cover
    from django.urls import reverse_lazy

from crypta import forms, models
from crypta.utils import crypt, tokens
from crypta.mixins import views as mixins
from crypta.mixins.forms import PasswordConfirmFormMixin
from crypta.conf import settings


class SecretCreateView(mixins.LoginRequiredMixin, CreateView):
    ''' Creates a new secret '''
    model = models.Secret
    form_class = forms.CreateSecretForm
    template_name = 'crypta/secret/create.' + settings.TEMPLATE_EXTENSION

    def get_success_url(self):
        return self.object.vault.get_absolute_url()

    def get_initial(self):
        self.vault = get_object_or_404(
            models.Vault.objects.active().with_member(self.request.user),
            slug=self.kwargs['slug'],
        )
        initial = super().get_initial()
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['vault'] = self.vault
        return kwargs


class SecretDetailView(mixins.LoginRequiredMixin, FormView, DetailView):
    ''' Show a secret details. '''
    template_name = 'crypta/secret/detail.' + settings.TEMPLATE_EXTENSION
    model = models.Secret
    form_class = PasswordConfirmFormMixin

    def get_object(self, queryset=None):
        return get_object_or_404(
            self.model.objects.select_related('vault'),
            vault__members=self.request.user,
            pk=self.kwargs.get('pk', None),
        )

    def get_form_kwargs(self):
        self.object = self.get_object()
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        context = self.get_context_data(object=self.object)
        token = tokens.secret_update_token_generator.make_token(
            self.object, self.request.user
        )
        context['update_url'] = reverse_lazy(
            'secret:update', args=[self.object.pk, token]
        )
        context['clear_text_secret'] = crypt.decrypt(
            models.Membership.objects.get(
                member=self.request.user,
                vault=self.object.vault
            ).priv_key,
            form.cleaned_data['password'],
            self.object.data,
        )
        return self.render_to_response(context)


class SecretUpdateView(mixins.LoginRequiredMixin, UpdateView):
    ''' Updates a secret '''
    form_class = forms.UpdateSecretForm
    model = models.Secret
    http_method_names = ['post']

    def get_success_url(self):
        return reverse_lazy('secret:detail', args=[self.object.pk])

    def get_object(self, queryset=None):
        secret = get_object_or_404(
            self.model.objects.select_related('vault'),
            vault__members=self.request.user,
            vault__membership__role__in=('admin', 'owner'),
            pk=self.kwargs.get('pk', None),
        )
        valid_token = tokens.secret_update_token_generator.check_token(
            secret, self.request.user, self.kwargs['token']
        )
        if not valid_token:
            raise Http404()
        return secret


class SecretDeleteView(mixins.LoginRequiredMixin, DeleteView):
    ''' Deletes a secret '''
    model = models.Secret
    http_method_names = ['post']

    def get_success_url(self):
        return reverse_lazy('vault:detail', args=[self.vault.slug])

    def get_object(self, queryset=None):
        obj = get_object_or_404(
            self.model.objects.select_related('vault'),
            vault__members=self.request.user,
            vault__membership__role__in=('admin', 'owner'),
            pk=self.kwargs.get('pk', None),
        )
        self.vault = obj.vault
        return obj
