``do-dns-manager`` |pypi|
=========================

A DNS record manager using DigitalOcean as backend, with its own authentication.
Best suited when you just need something that changes the DNS, but you don't want it
to have access to other APIs, for example, APIs that can cost you money.

I find this particularly useful for assigning DNS records in a DHCP lease hook.
An example hook is included as ``dnsmasq-hook`` for ``dnsmasq`` users.

Installation
------------

::

  pip install do-dns-manager

Configuration
-------------

Create `htpasswd.txt` somewhere containing lines of username and password pairs
separated by ``:``, for example:

::

  spam:password
  ham:hunter2

We will call this file ``$HTPASSWD``.

Run the DNS manager as follows:

::

  DIGITAL_OCEAN_API_KEY='(api key)' do-dns-manager --domain=example.com --keyfile=$HTPASSWD --port=8888 --address=127.0.0.1

Change ``(api key)``, ``example.com``, ``$HTPASSWD``, ``8888`` and ``127.0.0.1``
to fit your situation.

We will use ``curl`` examples:

::

  # Add A record for spam.example.com
  curl -u 'spam:password' http://127.0.0.1:8888 -d @- <<EOF
  {"op": "add", "address": "127.0.0.1", "domain": "spam"}
  EOF
  
  # Add AAAA record for spam.example.com
  curl -u 'spam:password' http://127.0.0.1:8888 -d @- <<EOF
  {"op": "add", "address": "::1", "domain": "spam"}
  EOF
  
  # Remove A record for spam.example.com
  curl -u 'spam:password' http://127.0.0.1:8888 -d @- <<EOF
  {"op": "del", "address": "127.0.0.1", "domain": "spam"}
  EOF
  
  # Remove AAAA record for spam.example.com
  # Using "address": "::1" instead of "type": "AAAA" also works
  curl -u 'spam:password' http://127.0.0.1:8888 -d @- <<EOF
  {"op": "del", "type": "AAAA", "domain": "spam"}
  EOF

.. |pypi| image:: https://img.shields.io/pypi/v/do-dns-manager.svg
   :target: https://pypi.python.org/pypi/do-dns-manager
