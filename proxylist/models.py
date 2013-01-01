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

from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils.timezone import now
from django_countries import CountryField

from pygeoip import GeoIP

ANONYMITY_NONE   = 0
ANONYMITY_LOW    = 1
ANONYMITY_MEDIUM = 2
ANONYMITY_HIGH   = 3


def getsettings(key, default):
    return getattr(settings, key, default)
      
PROXYLIST_CACHE_TIMEOUT = getsettings("PROXYLIST_CACHE_TIMEOUT", 0) # Forever!
PROXYLIST_CONNECTION_TIMEOUT = getsettings("PROXYLIST_CONNECTION_TIMEOUT", 30)
PROXYLIST_ERROR_DELAY = getsettings("PROXYLIST_ERRORDELAY", 300)
PROXYLIST_GEOIP_PATH = getsettings("PROXYLIST_GEOIP_PATH", "/usr/share/GeoIP/GeoIP.dat")
PROXYLIST_MAX_CHECK_INTERVAL = getsettings("PROXYLIST_MAX_CHECK_INTERVAL", 900)
PROXYLIST_MIN_CHECK_INTERVAL = getsettings("PROXYLIST_MIN_CHECK_INTERVAL", 300)
PROXYLIST_OUTIP_INTERVAL = getsettings("PROXYLIST_OUTIP_INTERVAL", 300)
PROXYLIST_USER_AGENT = getsettings("PROXYLIST_USER_AGENT", "Django-Proxy 1.0.0")

class ProxyCheckResult(models.Model):
    """The result of a proxy check"""

    mirror = models.ForeignKey('Mirror')

    proxy = models.ForeignKey('Proxy')

    #: Our real outbound IP Address (from worker)
    real_ip_address = models.IPAddressField(blank=True, null=True)

    #: Proxy outbound IP Address (received from mirror)
    ip_address = models.IPAddressField(blank=True, null=True)

    #: True if we found proxy related http headers
    forwarded = models.BooleanField(default=True)

    #: True if `real_ip_address` was found at any field
    ip_reveal = models.BooleanField(default=True)

    #: Check starts 
    check_start = models.DateTimeField()

    #: Request was received at mirror server
    response_start = models.DateTimeField()

    #: Request was send back from the mirror
    response_end = models.DateTimeField()

    #: Check ends
    check_end = models.DateTimeField()

    raw_response = models.TextField(null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super(ProxyCheckResult, self).__init__(*args, **kwargs)
        if self.real_ip_address is None:
            self.real_ip_address = self._get_real_ip()

    def _get_real_ip(self):
        import os
        import socket

        ip_key = '%s.%s.ip' % (socket.gethostname(), os.getpid())

        ip = cache.get(ip_key)
        if ip: return ip

        import pycurl
        import cStringIO
        buf = cStringIO.StringIO()

        try:
            c = pycurl.Curl()
            c.setopt(pycurl.URL, "http://ifconfig.me/ip")
            c.setopt(pycurl.WRITEFUNCTION, buf.write)
            c.setopt(pycurl.CONNECTTIMEOUT, PROXYLIST_CONNECTION_TIMEOUT)
            c.setopt(pycurl.TIMEOUT, PROXYLIST_CONNECTION_TIMEOUT)
            c.setopt(pycurl.USERAGENT, PROXYLIST_USER_AGENT)

            c.perform()

            ip = buf.getvalue().replace('\n', '').replace('\r', '')

            cache.set(ip_key, ip, PROXYLIST_OUTIP_INTERVAL) 
            return ip

        except:
            raise
        finally:
            buf.close()

    def anonymity(self):
        if self.forwarded and self.ip_reveal:
            return ANONYMITY_NONE
        elif not self.forwarded and self.ip_reveal:
            return ANONYMITY_LOW
        elif self.forwarded and not self.ip_reveal:
            return ANONYMITY_MEDIUM
        else:
            return ANONYMITY_HIGH


class Mirror(models.Model):
    """A proxy checker site like. 
    Ex: http://ifconfig.me/all.json
    """


    output_type_choices = (
        ('plm_v1', 'ProxyList Mirror v1.0'),
    )

    url = models.URLField()

    output_type = models.CharField(max_length=10, 
                                   choices=output_type_choices,
                                   default='plm_v1')

    def __unicode__(self):
        return self.url

    def _make_request(self, proxy):
        """Make request to the mirror throught proxy"""

        import pycurl
        import cStringIO
         
        buf = cStringIO.StringIO()

        try:
            import pycurl

            c = pycurl.Curl()
            c.setopt(pycurl.URL, str(self.url))
            c.setopt(pycurl.WRITEFUNCTION, buf.write)
            c.setopt(pycurl.CONNECTTIMEOUT, PROXYLIST_CONNECTION_TIMEOUT)
            c.setopt(pycurl.TIMEOUT, PROXYLIST_CONNECTION_TIMEOUT)
            c.setopt(pycurl.PROXY, str(proxy.ip_address))
            c.setopt(pycurl.PROXYPORT, proxy.port)
            c.setopt(pycurl.PROXYTYPE, proxy.curl_type())
            c.setopt(pycurl.USERAGENT, PROXYLIST_USER_AGENT)

            c.perform()

            return buf.getvalue()
        except:
            raise
        finally:
            buf.close()

    def _parse_plm_v1(self, res, raw_data):
        """ Parse data from a ProxyList Mirror v1.0 output and fill a 
        ProxyCheckResult object """

        import json
        from dateutil.parser import parse

        FORWARD_HEADERS = set((
            'FORWARDED',
            'X_FORWARDED_FOR',
            'X_FORWARDED_BY',
            'X_FORWARDED_HOST',
            'X_FORWARDED_PROTO',
            'VIA',
            'CUDA_CLIIP',
        ))

        data = json.loads(raw_data)

        res.response_start = parse(data['response_start']) 
        res.response_end   = parse(data['response_end']) 

        res.ip_address = data.get('REMOTE_ADDR', None)

        # True if we found proxy related http headers
        headers_keys = set(data['http_headers'].keys())
        res.forwarded = bool(FORWARD_HEADERS.intersection(headers_keys))

        headers_vals = data['http_headers'].values() 

        #: True if `real_ip_address` was found at any field
        res.ip_reveal = any([ x.find(res.real_ip_address)!= -1 for x in headers_vals])


    def is_checking(self, proxy):
        check_key = "proxy.%s.check" % proxy.pk

        return bool(cache.get(check_key))

    def _check(self, proxy):
        """Do a proxy check"""

        check_key = "proxy.%s.check" % proxy.pk

        res = None
        try:
            
            res = ProxyCheckResult()
            res.proxy = proxy
            res.mirror = self
            res.check_start = now()
            raw_data = self._make_request(proxy)
            res.check_end = now()
            res.raw_response = raw_data

            if self.output_type == 'plm_v1':
                self._parse_plm_v1(res, raw_data)
            else:
                raise NotImplemented('Output type not found!')

            proxy.update_from_check(res)

            res.save()

            return res
        except:
            proxy.update_from_error()
            raise
        finally:
            # Task unlock
            cache.delete(check_key)

    def check(self, proxy):
        from proxylist.tasks import async_check

        check_key = "proxy.%s.check" % proxy.pk

        if self.is_checking(proxy):
            return None
        else:
            # Task lock
            cache.add(check_key, "true", PROXYLIST_CACHE_TIMEOUT)

        return async_check.apply_async((proxy, self))


class Proxy(models.Model):
    """A proxy server"""

    _geoip = GeoIP(PROXYLIST_GEOIP_PATH)

    proxy_type_choices = (
        ('http', 'HTTP'), 
        ('https', 'HTTPS'), 
        ('socks4', 'SOCKS4'),
        ('socks5', 'SOCKS5'),
    )

    anonymity_level_choices = (
        # Anonymity can't be determined
        (None, 'Unknown'),

        # No anonymity; remote host knows your IP and knows you are using 
        # proxy.
        (ANONYMITY_NONE, 'None'), 

        # Low anonymity; proxy sent our IP to remote host, but it was sent in
        # non standard way (unknown header).
        (ANONYMITY_LOW, 'Low'), 

        # Medium anonymity; remote host knows you are using proxy, but it does 
        # not know your IP
        (ANONYMITY_MEDIUM, 'Medium'), 

        # High anonymity; remote host does not know your IP and has no direct 
        # proof of proxy usage (proxy-connection family header strings). 
        (ANONYMITY_HIGH, 'High'), 
    )


    ip_address = models.IPAddressField()

    port = models.PositiveIntegerField()

    country = CountryField(blank=True)

    speed = models.PositiveIntegerField(null=True, blank=True)

    connection_time = models.PositiveIntegerField(null=True, blank=True)

    proxy_type = models.CharField(default='http',
                                  max_length=10, 
                                  choices=proxy_type_choices)

    anonymity_level = models.PositiveIntegerField(
                         null=True,
                         default=None,
                         choices = anonymity_level_choices)

    last_check = models.DateTimeField(null=True)

    next_check = models.DateTimeField(null=True)

    errors = models.PositiveIntegerField(default=0)

    def _update_next_check(self):
        """ Calculate and set next check time """

        from random import randint

        delay = randint(PROXYLIST_MIN_CHECK_INTERVAL, 
                        PROXYLIST_MAX_CHECK_INTERVAL)

        delay += PROXYLIST_ERROR_DELAY * self.errors

        if self.last_check:
            self.next_check = self.last_check + timedelta(seconds=delay)
        else:
            self.next_check = now() + timedelta(seconds=delay)


    def update_from_check(self, check):
        """ Update data from a ProxyCheckResult """

        if check.check_start:
            self.last_check = check.check_start
        else:
            self.last_check = now()
        self.errors = 0
        self.anonymity_level = check.anonymity()
        self._update_next_check()
        self.save()

    def update_from_error(self):
        """ Last check was an error """

        self.last_check = now()
        self.errors = self.errors + 1
        self._update_next_check()
        self.save()

    def save(self, *args, **kwargs):
        if not self.country:
            self.country = self._geoip.country_code_by_addr(self.ip_address)

        if not self.next_check:
            self._update_next_check()

        super(Proxy, self).save(*args, **kwargs)

    def curl_type(self):
        import pycurl

        if self.proxy_type == 'http' or self.proxy_type == 'https':
            return pycurl.PROXYTYPE_HTTP
        elif self.proxy_type == 'socks4':
            return pycurl.PROXYTYPE_SOCKS4
        elif self.proxy_type == 'socks5':
            return pycurl.PROXYTYPE_SOCKS5
        else:
            raise NotImplemented('Unknown proxy type')

    class Meta:
        verbose_name = 'Proxy'
        verbose_name_plural = 'Proxies'
        ordering = ('-last_check', )

    def __unicode__(self):
        return "%s://%s:%s" % (self.proxy_type, self.ip_address, self.port)

