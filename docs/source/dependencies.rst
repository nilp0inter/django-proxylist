Dependencies
============

`django-proxylist` depends on:

Packages
--------

* django-celery
* django-countries
* pygeoip
* pycurl

.. todo::

   Add package versions and descriptions


Backend
-------

Cache
~~~~~

The checking machinery uses django's cache backend and the *default* cache but
you can alter this behaviour changing the **PROXYLIST_CACHE** variable.


Database
~~~~~~~~

`django-proxilist` does not depends on any database backend by itself, but if
you have a big list of proxies and you want to check it at sorts intervals
you should avoid `SQLite`.


