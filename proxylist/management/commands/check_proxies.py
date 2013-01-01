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

from celery import group 
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from proxylist.models import Proxy, Mirror
from random import choice

class Command(BaseCommand):
    args = '<proxy list files>'
    help = 'Update proxy list from file(s)'

    def handle(self, *args, **options):
        mirrors = Mirror.objects.all()
        proxies = Proxy.objects.filter(next_check__lte=now())

        for p in proxies:
            m = choice(mirrors)
            if not m.is_checking(p):
                m.check(p)
