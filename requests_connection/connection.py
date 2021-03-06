from functools import partial
import logging
import socket
try:
    from http.client import HTTPConnection, HTTPSConnection
except ImportError:
    from httplib import HTTPConnection, HTTPSConnection

logger = logging.getLogger('requests_connection')


class SocketHTTPConnection(HTTPConnection):
    def __init__(self, *args, socket_conn, **kwargs):
        self.socket_conn = socket_conn
        super(SocketHTTPConnection, self).__init__(*args, **kwargs)

    def _new_conn(self):
        return self.socket_conn


class Connection(object):
    @staticmethod
    def http(host, port=80, **kwargs):
        logger.debug('get http connection')
        factory = partial(HTTPConnection, host=host, port=port, **kwargs)
        connection = factory()
        connection.factory = factory
        return connection

    @staticmethod
    def https(host, port=443, **kwargs):
        logger.debug('get https connection')
        factory = partial(HTTPSConnection, host=host, port=port, **kwargs)
        connection = factory()
        connection.factory = factory
        return connection

    @staticmethod
    def socket(host, port=80, **kwargs):
        logger.debug('get socket http connection')
        socket_conn = socket.create_connection((host, port), **kwargs)
        factory = partial(SocketHTTPConnection, host=host, port=port, socket_conn=socket_conn)
        connection = factory()
        connection.factory = factory
        return connection
