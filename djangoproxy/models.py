# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils.timezone import now
from django_countries import CountryField

from pygeoip import GeoIP

ANONYMITY_NONE   = 1
ANONYMITY_LOW    = 4
ANONYMITY_MEDIUM = 8
ANONYMITY_HIGH   = 16


def getsettings(key, default):
    return getattr(settings, key, default)
      
DJANGOPROXY_USER_AGENT = getsettings("DJANGOPROXY_USER_AGENT", 
                                     "Django-Proxy 1.0.0")
DJANGOPROXY_GEOIP_PATH = getsettings("DJANGOPROXY_GEOIP_PATH",
                                     "/usr/share/GeoIP/GeoIP.dat")
DJANGOPROXY_CACHE_TIMEOUT = getsettings("DJANGOPROXY_CACHE_TIMEOUT", 0) # Forever!
DJANGOPROXY_CONNECTION_TIMEOUT = getsettings("DJANGOPROXY_CONNECTION_TIMEOUT", 
                                             30)
DJANGOPROXY_OUTBOUND_IP_CHECK_INTERVAL = getsettings("DJANGOPROXY_OUTBOUND_IP_CHECK_INTERVAL", 
                                                     300)
DJANGOPROXY_MIN_CHECK_INTERVAL = getsettings("DJANGOPROXY_MIN_CHECK_INTERVAL",
                                             300)
DJANGOPROXY_MAX_CHECK_INTERVAL = getsettings("DJANGOPROXY_MAX_CHECK_INTERVAL",
                                             900)
DJANGOPROXY_ERROR_DELAY = getsettings("DJANGOPROXY_ERRORDELAY", 300)

class ProxyCheckResult(models.Model):
    """The result of a proxy check"""

    proxy_checker = models.ForeignKey('ProxyChecker')
    proxy = models.ForeignKey('Proxy')

    real_ip_address = models.IPAddressField(blank=True, null=True)
    ip_address = models.IPAddressField(blank=True, null=True)
    remote_host = models.CharField(max_length=255, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    # CSV of forwarded family headers
    forwarded = models.CharField(max_length=255, blank=True, null=True)

    check_time = models.DateTimeField()
    check_delay = models.PositiveIntegerField(null=True)

    def __init__(self, *args, **kwargs):
        super(ProxyCheckResult, self).__init__(*args, **kwargs)
        if self.real_ip_address is None:
            self.real_ip_address = self._get_real_ip()

    def _get_real_ip(self):
        import os
        import socket
        import pycurl
        import cStringIO

        ip_key = '%s.%s.ip' % (socket.gethostname(), os.getpid())

        ip = cache.get(ip_key)
        if ip: return ip
         
        buf = cStringIO.StringIO()

        try:
            c = pycurl.Curl()
            c.setopt(pycurl.URL, "http://ifconfig.me/ip")
            c.setopt(pycurl.WRITEFUNCTION, buf.write)
            c.setopt(pycurl.CONNECTTIMEOUT, DJANGOPROXY_CONNECTION_TIMEOUT)
            c.setopt(pycurl.TIMEOUT, DJANGOPROXY_CONNECTION_TIMEOUT)
            c.setopt(pycurl.USERAGENT, DJANGOPROXY_USER_AGENT)

            c.perform()

            ip = buf.getvalue().replace('\n', '').replace('\r', '')

            cache.set(ip_key, ip, DJANGOPROXY_OUTBOUND_IP_CHECK_INTERVAL) 
            return ip

        except:
            raise
        finally:
            buf.close()

    def anonymity(self):
        if self.ip_address == self.real_ip_address or \
           self.forwarded == self.real_ip_address:
            return ANONYMITY_NONE
        elif self.forwarded and \
             self.forwarded.find(self.real_ip_address) != -1 and \
             len(self.forwarded.split(','))>1:
            return ANONYMITY_LOW
        elif self.forwarded and \
             self.forwarded.find(self.real_ip_address) == -1 and \
             len(self.forwarded.split(',')) == 1:
            return ANONYMITY_MEDIUM
        elif not self.forwarded:
            return ANONYMITY_HIGH
        else:
            raise ValueError('Anonymity type not defined')


class ProxyChecker(models.Model):
    """A proxy checker site like. 
    Ex: http://ifconfig.me/all.json
    """

    output_type_choices = (
        ('json', 'JSON'),
        # ('xml', 'XML'),
        # ('plain', 'PLAIN'),
    )

    url = models.URLField()

    output_type = models.CharField(max_length=10, 
                                   choices=output_type_choices,
                                   default='json')


    def __unicode__(self):
        return self.url

    def _raw_check(self, proxy):
        """Actually execute the check"""

        import pycurl
        import cStringIO
         
        buf = cStringIO.StringIO()

        try:
            import pycurl

            c = pycurl.Curl()
            c.setopt(pycurl.URL, str(self.url))
            c.setopt(pycurl.WRITEFUNCTION, buf.write)
            c.setopt(pycurl.CONNECTTIMEOUT, DJANGOPROXY_CONNECTION_TIMEOUT)
            c.setopt(pycurl.TIMEOUT, DJANGOPROXY_CONNECTION_TIMEOUT)
            c.setopt(pycurl.PROXY, str(proxy.ip_address))
            c.setopt(pycurl.PROXYPORT, proxy.port)
            c.setopt(pycurl.PROXYTYPE, proxy.curl_type())
            c.setopt(pycurl.USERAGENT, DJANGOPROXY_USER_AGENT)

            c.perform()

            return buf.getvalue()
        except:
            raise
        finally:
            buf.close()

    def _result_from_data(self, proxy, data, start, end):
        """ Convert parsed data into a ProxyCheckResult object (not saved)"""

        res = ProxyCheckResult()
        res.check_time = start
        res.check_delay = (end - start).seconds
        res.proxy = proxy

        res.ip_address  = data.get('ip_addr', None)
        res.remote_host = data.get('remote_host', None)
        res.user_agent  = data.get('user_agent', None)
        res.forwarded   = data.get('forwarded', None)

        return res

    def _check_json(self, proxy):
        """Get info from output like http://ifconfig.me/all.json"""

        import json

        start = now()
        rawdata = self._raw_check(proxy)
        end = now()

        data = json.loads(rawdata)

        return self._result_from_data(proxy, data, start, end)

    def is_checking(self, proxy):
        check_key = "proxy.%s.check" % proxy.pk

        return bool(cache.get(check_key))

    def _check(self, proxy):
        """Do a proxy check"""

        check_key = "proxy.%s.check" % proxy.pk

        res = None
        try:
            if self.output_type == 'json':
                res = self._check_json(proxy)
            else:
                raise NotImplemented('Output type %s not recognized' %
                                     self.output_type)

            proxy.update_from_check(res)
            return res
        except:
            proxy.update_from_error()
            raise
        finally:
            # Task unlock
            cache.delete(check_key)

    def check(self, proxy):
        from djangoproxy.tasks import async_check

        check_key = "proxy.%s.check" % proxy.pk

        if self.is_checking(proxy):
            return None
        else:
            # Task lock
            cache.add(check_key, "true", DJANGOPROXY_CACHE_TIMEOUT)

        return async_check.apply_async((proxy, self))


class Proxy(models.Model):
    """A proxy server"""

    _geoip = GeoIP(DJANGOPROXY_GEOIP_PATH)

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

        # Low anonymity; remote host does not know your IP, but it knows you 
        # are using proxy.
        (ANONYMITY_LOW, 'Low'), 

        # Medium anonymity; remote host knows you are using proxy, and thinks 
        # it knows your IP, but this is not yours (this is usually a multihomed 
        # proxy which shows its inbound interface as REMOTE_ADDR for a target 
        # host).
        (ANONYMITY_MEDIUM, 'Medium'), 

        # High anonymity; remote host does not know your IP and has no direct 
        # proof of proxy usage (proxy-connection family header strings). 
        # If such hosts do not send additional header strings it may be 
        # considered as high-anonymous. If a high-anonymous proxy supports 
        # keep-alive you can consider it to be extremely-anonymous. However, 
        # such a host is highly possible to be a honey-pot.
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

        delay = randint(DJANGOPROXY_MIN_CHECK_INTERVAL, 
                        DJANGOPROXY_MAX_CHECK_INTERVAL)

        delay += DJANGOPROXY_ERROR_DELAY * self.errors

        if self.last_check:
            self.next_check = self.last_check + timedelta(seconds=delay)
        else:
            self.next_check = now() + timedelta(seconds=delay)


    def update_from_check(self, check):
        """ Update data from a ProxyCheckResult """

        if check.check_time:
            self.last_check = check.check_time
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
        #TODO: Mejorar
        return "%s://%s:%s" % (self.proxy_type, self.ip_address, self.port)

