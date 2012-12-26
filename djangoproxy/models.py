# -*- coding: utf-8 -*-

from datetime import datetime

from django.db import models
from django_countries import CountryField

ANONYMITY_NONE   = 1
ANONYMITY_LOW    = 4
ANONYMITY_MEDIUM = 8
ANONYMITY_HIGH   = 16

class ProxyCheckResult(models.Model):
    """The result of a proxy check"""

    proxy_checker = models.ForeignKey('ProxyChecker')
    proxy = models.ForeignKey('Proxy')

    ip_address = models.IPAddressField(blank=True, null=True)
    remote_host = models.CharField(max_length=255, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    check_time = models.DateTimeField()
    check_delay = models.PositiveIntegerField(null=True)


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
            c.setopt(pycurl.CONNECTTIMEOUT, 30)
            c.setopt(pycurl.TIMEOUT, 30)
            c.setopt(pycurl.PROXY, str(proxy.ip_address))
            c.setopt(pycurl.PROXYPORT, proxy.port)
            c.setopt(pycurl.PROXYTYPE, proxy.curl_type())

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

        return res

    def _check_json(self, proxy):
        """Get info from output like http://ifconfig.me/all.json"""

        import json

        start = datetime.today()
        rawdata = self._raw_check(proxy)
        end = datetime.today()

        data = json.loads(rawdata)

        return self._result_from_data(proxy, data, start, end)

    def check(self, proxy):
        """Do a proxy check"""

        if self.output_type == 'json':
            return self._check_json(proxy)
        else:
            raise NotImplemented('Output type %s not recognized' %
                    self.output_type)


class Proxy(models.Model):
    """A proxy server"""

    proxy_type_choices = (
        ('http', 'HTTP'), 
        ('https', 'HTTPS'), 
        ('socks4', 'SOCKS4'),
        ('socks5', 'SOCKS5'),
    )

    anonymity_level_choices = (
        # No anonymity; remote host knows your IP and knows you are using 
        # proxy.
        (ANONYMITY_NONE, 'No anonymity'), 

        # Low anonymity; remote host does not know your IP, but it knows you 
        # are using proxy.
        (ANONYMITY_LOW, 'Low anonymity'), 

        # Medium anonymity; remote host knows you are using proxy, and thinks 
        # it knows your IP, but this is not yours (this is usually a multihomed 
        # proxy which shows its inbound interface as REMOTE_ADDR for a target 
        # host).
        (ANONYMITY_MEDIUM, 'Medium anonymity'), 

        # High anonymity; remote host does not know your IP and has no direct 
        # proof of proxy usage (proxy-connection family header strings). 
        # If such hosts do not send additional header strings it may be 
        # considered as high-anonymous. If a high-anonymous proxy supports 
        # keep-alive you can consider it to be extremely-anonymous. However, 
        # such a host is highly possible to be a honey-pot.
        (ANONYMITY_HIGH, 'High anonymity'), 
    )

    last_update = models.DateTimeField(auto_now=True)

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

    def __unicode__(self):
        #TODO: Mejorar
        return "%s://%s:%s" % (self.proxy_type, self.ip_address, self.port)




