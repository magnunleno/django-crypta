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

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import (CreateView, DeleteView, FormView, ListView,
                                  View)

from crypta import forms, models
from crypta.conf import settings
from crypta.mixins import views as mixins
from crypta.mixins.forms import PasswordConfirmFormMixin

try:  # pragma: no cover
    from django.core.urlresolvers import reverse_lazy
except ImportError:  # pragma: no cover
    from django.urls import reverse_lazy


class VaultInviteListView(mixins.LoginRequiredMixin, ListView):
    ''' List all invites for a specific vault '''
    model = models.Invite
    template_name = 'crypta/invite/by_vault.' + settings.TEMPLATE_EXTENSION

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vault'] = self.vault
        return context

    def get_queryset(self):
        self.vault = get_object_or_404(
            models.Vault.objects.owned_by(self.request.user),
            slug=self.kwargs.get('slug', None),
        )
        self.queryset = self.model.objects.filter(
            vault=self.vault,
            vault__membership__member=self.request.user,
            vault__membership__role__in=['owner', 'admin'],
        )
        return super().get_queryset()


class InviteCreateView(mixins.LoginRequiredMixin, CreateView):
    ''' Creates a new Invite '''
    model = models.Invite
    form_class = forms.CreateInviteForm
    template_name = 'crypta/invite/create.' + settings.TEMPLATE_EXTENSION

    def get_success_url(self):
        return self.vault.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vault'] = self.vault
        return context

    def get_initial(self):
        self.vault = get_object_or_404(
            models.Vault.objects.owned_by(self.request.user),
            slug=self.kwargs.get('slug', None),
        )
        initial = super().get_initial()
        initial['vault'] = self.vault
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.model.objects.create(
            inviter=self.request.user,
            inviter_pass=form.cleaned_data['password'],
            invitee=form.cleaned_data['invitee'],
            role=form.cleaned_data['role'],
            vault=self.vault
        )
        return HttpResponseRedirect(self.get_success_url())


class InviteAcceptView(mixins.LoginRequiredMixin, FormView):
    ''' View used by the invitee to accept the invite '''
    form_class = forms.AcceptInviteForm
    template_name = 'crypta/invite/accept.' + settings.TEMPLATE_EXTENSION

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['invite'] = self.invite
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        self.invite = get_object_or_404(
            models.Invite,
            pk=self.kwargs.get('pk', kwargs),
            invitee=self.request.user,
        )
        kwargs['invite'] = self.invite
        return kwargs

    def get_success_url(self):
        return reverse_lazy('vault:detail', args=[self.invite.vault.slug])

    def form_valid(self, form):
        models.Membership.objects.create_from_invite(
            self.invite, form.cleaned_data['token'],
            form.cleaned_data['password'],
        )
        return HttpResponseRedirect(self.get_success_url())


class InviteRevokeView(mixins.LoginRequiredMixin, DeleteView):
    ''' Where the admins and owners can revoke invites '''
    model = models.Invite
    http_method_names = ['post']

    def get_success_url(self):
        return reverse_lazy('invite:by-vault', args=[self.vault.slug])

    def get_object(self, queryset=None):
        obj = get_object_or_404(
            self.model.objects.not_accepted().from_vault_managed_by(
                self.request.user
            ),
            pk=self.request.POST['pk'],
        )
        self.vault = obj.vault
        return obj


class InviteRenewView(mixins.LoginRequiredMixin, View):
    ''' Where the admins and owners can renew invites '''
    model = models.Invite
    http_method_names = ['post']

    def get_success_url(self):
        return reverse_lazy('invite:by-vault', args=[self.vault.slug])

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(
            self.model.objects.not_accepted().from_vault_managed_by(
                self.request.user
            ),
            pk=self.request.POST['pk'],
        )
        self.vault = obj.vault
        obj.renew()
        return HttpResponseRedirect(self.get_success_url())


class InviteResendView(mixins.LoginRequiredMixin, FormView):
    ''' Where the admins and owners can resend invites '''
    model = models.Invite
    form_class = PasswordConfirmFormMixin
    template_name = 'crypta/invite/resend.' + settings.TEMPLATE_EXTENSION

    def get_success_url(self):
        return reverse_lazy('invite:by-vault', args=[self.vault.slug])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.object = get_object_or_404(
            self.model.objects.pending().from_vault_managed_by(
                self.request.user
            ),
            pk=self.kwargs['pk'],
        )

        user_membership = models.Membership.objects.get(
            vault=self.object.vault, member=self.request.user
        )
        if self.object.role == 'owner' and user_membership.role != 'owner':
            raise Http404()

        self.vault = self.object.vault
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.object.resend(
            self.request.user, form.cleaned_data['password']
        )
        return HttpResponseRedirect(self.get_success_url())
