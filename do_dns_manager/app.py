import ipaddress
import logging
import os
import re

from tornado import gen, escape, web, httpclient
from tornado_http_auth import BasicAuthMixin

revalid = re.compile(r'^[\w-]+$')
log = logging.getLogger('do_dns_manager')


class DNSUpdateHandler(BasicAuthMixin, web.RequestHandler):
    def initialize(self, api_key, pw_dict, domain):
        self.api_key = api_key
        self.pw_dict = pw_dict
        self.domain = domain

    def prepare(self):
        self.authed = False
        if self.request.method.lower() == 'post':
            if self.get_authenticated_user(check_credentials_func=self.pw_dict.get, realm='Protected'):
                self.authed = True

    @gen.coroutine
    def get(self):
        self.render('list.html', domain=self.domain, records=(yield self._do_get_domains()))

    @gen.coroutine
    def post(self):
        if not self.authed:
            self.set_status(403)
            raise web.Finish('Forbidden')

        try:
            data = escape.json_decode(self.request.body)
        except ValueError:
            self.set_status(400)
            raise web.Finish('Request is invalid JSON')

        def get_or_fail(key):
            try:
                return data[key]
            except KeyError:
                self.set_status(400)
                raise web.Finish('You must pass key: %s' % (key,))

        domain = str(get_or_fail('domain'))
        if not revalid.match(domain):
            self.set_status(400)
            raise web.Finish('Invalid domain name')
        domain = domain.lower()

        op = str(get_or_fail('op'))
        if op not in ('add', 'del'):
            self.set_status(400)
            raise web.Finish('Invalid operation, must be "add" or "del": %s' % (op,))

        if op == 'del' and 'type' in data:
            if data['type'] in ('A', 'AAAA'):
                ip = ipaddress.ip_address({'A': '127.0.0.1', 'AAAA': '::1'}[data['type']])
            else:
                self.set_status(400)
                raise web.Finish('Invalid DNS type: %s' % (data['type'],))
        else:
            try:
                ip = ipaddress.ip_address(get_or_fail('address'))
            except ValueError:
                self.set_status(400)
                raise web.Finish('Invalid IP address: %s' % (data['address'],))

        if (yield self._do_edit_dns(domain, ip, op == 'add')):
            self.finish('success')
        else:
            self.set_status(500)
            self.finish('failed')

    @gen.coroutine
    def _do_api(self, path, body=None, **kwargs):
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = 'Bearer %s' % (self.api_key,)
        if body:
            kwargs['body'] = escape.json_encode(body)
            headers['Content-Type'] = 'application/json'

        result = yield httpclient.AsyncHTTPClient().fetch(
            'https://api.digitalocean.com/v2/' + path,
            headers=headers,
            **kwargs,
        )
        result.rethrow()
        if result.body:
            return escape.json_decode(result.body)

    @gen.coroutine
    def _do_get_domains(self):
        result = yield self._do_api('domains/%s/records' % (self.domain,))
        return result['domain_records']

    @gen.coroutine
    def _do_edit_dns(self, domain, ip, add):
        type = {4: 'A', 6: 'AAAA'}[ip.version]
        records = [record for record in (yield self._do_get_domains())
                   if record['name'] == domain and record['type'] == type]

        if not add:
            log.info('Removed %s record: %s', type, domain)
            return (yield self._do_remove_entries(records))

        new = {'type': type, 'data': str(ip), 'name': domain}

        if records:
            change = records.pop()
            yield self._do_remove_entries(records)

            try:
                yield self._do_api('domains/%s/records/%d' % (self.domain, change['id']), method='PUT', body=new)
            except Exception:
                log.exception('Error while changing %s record %d (%s) to %s',
                              change['type'], change['id'], change['name'], ip)
                return False
        else:
            try:
                yield self._do_api('domains/%s/records' % (self.domain,), method='POST', body=new)
            except Exception:
                log.exception('Error while creating %s record %s to %s', type, domain, ip)
                return False

        log.info('Added %s record %s to %s', type, domain, ip)
        return True

    @gen.coroutine
    def _do_remove_entries(self, records):
        success = True
        for record in records:
            try:
                yield self._do_api('domains/%s/records/%d' % (self.domain, record['id']), method='DELETE')
            except Exception:
                log.exception('Error while deleting %s record %d: %s',
                              record['type'], record['id'], record['name'])
                success = False
        return success


def get_application(api_key, pw_dict, domain):
    return web.Application([
        (r'/', DNSUpdateHandler, {'api_key': api_key, 'pw_dict': pw_dict, 'domain': domain}),
    ], template_path=os.path.join(os.path.dirname(__file__), 'templates'))
