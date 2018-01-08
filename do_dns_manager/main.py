import os

import tornado.httpserver
import tornado.ioloop
import tornado.options

from .app import get_application
from .htpasswd import load_htpasswd


def main():
    from tornado.options import options, define

    define('port', default=8888, help='run on the given port', type=int)
    define('keyfile', default='htpasswd.txt', help='list of username:password lines that authenticates')
    define('domain', help='the DigitalOcean domain to change')
    api_key = os.environ['DIGITAL_OCEAN_API_KEY']

    tornado.options.parse_command_line()
    tornado.httpserver.HTTPServer(
        get_application(api_key, load_htpasswd(options.keyfile), options.domain)
    ).listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
