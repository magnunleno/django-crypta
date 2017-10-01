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

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView

try:
    login = auth_views.LoginView.as_view()
except AttributeError:
    login = auth_views.login

try:
    from django.conf.urls import url, include
except ImportError:
    from django.conf.urls import url, include

admin.autodiscover()

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='base.html')),
    url(r'^accounts/profile/$',
        TemplateView.as_view(template_name='profile.html'), name="profile"),
    url(r'^accounts/login/$', login, name='login'),
    url(r'^accounts/logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^crypta/', include('crypta.urls')),
    url(r'^admin/', admin.site.urls),
]
