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

import json

from django.http import HttpResponse
from django.utils.timezone import now

def mirror(request):
    """
    from dateutil.parser import parse
    parse("2012-12-28 22:22:12.868342+04:00")
    datetime.datetime(2012, 12, 28, 22, 22, 12, 868342, tzinfo=tzoffset(None, 14400))
    """

    start = now()

    SERIALIZABLE = (str, unicode, bool, int, float)

    output = dict()

    output['REMOTE_ADDR'] = request.META.get('REMOTE_ADDR', '')
    output['REMOTE_HOST'] = request.META.get('REMOTE_HOST', '')

    # HTTP Headers
    output['http_headers'] = dict()
    for k, v in request.META.items():
        if k.startswith('HTTP_') and type(v) in SERIALIZABLE:
               output['http_headers'][k[5:]] = v

    # Timing
    output['response_start'] = str(start)
    output['response_end'] = str(now())

    return HttpResponse(json.dumps(output))

