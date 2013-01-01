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

import os

from django.core.management.base import BaseCommand, CommandError
from proxylist.models import Proxy

class Command(BaseCommand):
    args = '<hidemyass proxy list files>'
    help = 'Update proxy list from file(s)'

    def handle(self, *args, **options):
        for filename in args:
            if not os.path.isfile(filename):
                self.stderr.write("File %s does not exists!\n" % filename)
                continue
           
            self.stdout.write("Loading %s...\n" % filename)
            
            with open(filename, 'r') as f:
                for proxy in f:

                    proxy = proxy.replace('\n','').replace('\r','')

                    try:
                        ip_address, port = proxy.split(':', 2)
                    except ValueError:
                        self.stderr.write("Invalid format %s. ip:port" % proxy)
                        continue

                    try:
                        port = int(port)
                    except ValueError:
                        self.stderr.write("Invalid port %s value" % port)
                        continue

                    p, created = Proxy.objects.get_or_create(ip_address=ip_address, 
                                                             port=port)
