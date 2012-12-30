Advanced configuration
======================

``PROXYLIST_CACHE_TIMEOUT``

  Maximum number of seconds to mantain a lock at the cache framework.

  *Default*: 0


``PROXYLIST_CONNECTION_TIMEOUT``

  Number of seconds to wait for a connection to open, before canceling the
  attempt and generate an error.

  *Default*: 30


``PROXYLIST_ERROR_DELAY``

  Number of seconds to add to each check if the last one produced an error.

  *Default*: 300


``PROXYLIST_GEOIP_PATH`` 

  Path to GeoIP data file.

  *Default*: /usr/share/GeoIP/GeoIP.dat


``PROXYLIST_MAX_CHECK_INTERVAL``

  Maximum number of seconds to the next check if the last one was successful.

  *Default*: 900


``PROXYLIST_MIN_CHECK_INTERVAL``

  Minimum number of seconds to the next check if the last one was successful.

  *Default*: 300


``PROXYLIST_OUTIP_INTERVAL``

  Number of seconds between outbound IP checking (by worker). If you have a 
  fixed IP address you can set this value to 0 (infinity).

  *Default*: 300


``PROXYLIST_USER_AGENT``

  User-Agent for requests.

  *Default*: Django-ProxyList 1.0.0


