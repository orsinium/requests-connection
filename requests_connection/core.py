import logging
from requests import Session as _Session
from requests.adapters import HTTPAdapter as _HTTPAdapter
from requests.exceptions import ConnectionError

from .pool import PoolManager

logger = logging.getLogger('requests_connection')


class HTTPAdapter(_HTTPAdapter):
    connection = None

    def mount(self, connection):
        if connection is None:
            logger.warning("mounted empty connection")
        else:
            logger.debug("mount connection")
        self.connection = connection
        self.init_poolmanager(
            self._pool_connections,
            self._pool_maxsize,
            block=self._pool_block,
        )
        return self

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        if self.connection is not None:
            logger.debug("get pool manager")
            self.poolmanager = PoolManager(
                connection=self.connection, num_pools=connections,
                maxsize=maxsize, block=block, strict=True, **pool_kwargs,
            )
        else:
            logger.debug("connection not mounted")
            super(HTTPAdapter, self).init_poolmanager(
                connections=connections, maxsize=maxsize,
                block=block, **pool_kwargs,
            )


class Session(_Session):
    def __init__(self, connection=None):
        super(Session, self).__init__()
        self.connect(connection)

    def connect(self, connection=None):
        logger.debug("mount connection to session")

        # create connection via factory
        if connection is None:
            if self.connection is None:
                raise ConnectionError("no existing connection")
            if not hasattr(self.connection, 'factory'):
                raise ConnectionError("can not recreate connection: factory not found")
            logger.debug("make new connection via factory")
            factory = connection.factory
            connection = factory()
            connection.factory = factory

        self.connection = connection
        self.mount('https://', HTTPAdapter().mount(connection))
        self.mount('http://', HTTPAdapter().mount(connection))
        return self

    def send(self, *args, **kwargs):
        logger.debug("make request")
        try:
            return super(Session, self).send(*args, **kwargs)
        except ConnectionError:
            # try to reconnect and repeat request
            logger.warning("connection failed, try to reconnect")
            self.connect()
            return super(Session, self).send(*args, **kwargs)
