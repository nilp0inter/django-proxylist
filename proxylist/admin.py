#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2012 Roberto Abdelkader Martínez Pérez
# 
# This file is part of Django-ProxyList.
# 
# Django-ProxyList is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Django-ProxyList is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Django-ProxyList.  If not, see <http://www.gnu.org/licenses/>.

from proxylist.models import Proxy, Mirror, ProxyCheckResult 
from django.contrib import admin

class ProxyAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'port', 'country', 'anonymity_level', 
                    'last_check', 'proxy_type',  )
    list_filter = ('anonymity_level', 'proxy_type', )
    search_fields = ('=ip_address', '=port', 'country', )

admin.site.register(Proxy, ProxyAdmin)
admin.site.register(Mirror)

# Debug
#admin.site.register(ProxyCheckResult)
