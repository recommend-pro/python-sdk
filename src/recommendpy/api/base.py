from functools import wraps

from ..exceptions import (
    RecommendAPIError,
    RecommendUnauthorizedError,
)

import logging
log = logging.getLogger('recommendpy')


def check_token(func):
    """Decorator for checking the auth token."""
    @wraps(func)
    def wrapper(api, *args, **kwargs):
        if not api._client.is_auth_token_setted:
            api._client.set_auth_token()

        token = api._client.tokens['auth']
        if token.is_expired:
            api._client.refresh_token()
            api._client.set_auth_token()
        if token.need_refresh:
            try:
                api._client.refresh_token()
                api._client.set_auth_token()
            except RecommendAPIError as e:
                log.exception(e)
        if not api._client.is_auth_token_setted:
            raise RecommendUnauthorizedError('Set auth token')
        return func(api, *args, **kwargs)
    return wrapper


class BaseAPI(object):
    """Base API class."""

    def __init__(self, client, endpoint):
        r"""
        Initialize BaseAPI object.

        :param client: :class:`recommendpy.RecommendAPI` object (required).
        :param endpoint: string path for api endpoint (required).
        """
        self._client = client
        self.endpoint = endpoint

    def get_path(self, identifier=None, method=None, custom=None):
        r"""
        Get relative path.

        :param identifier: identifier of object. Defaults to ``None``.
        :param method: method of api endpoint. Defaults to ``None``.
        :param custom: custom path of api endpoint. Defaults to ``None``.

        :return: the slash-joined string of self.endpoint,
            identifier (if present), method (if present) and custom part.
        """
        url = [self.endpoint]
        if identifier:
            url.append(identifier)
        if method:
            url.append(method)
        if custom and isinstance(custom, list):
            url += custom
        elif custom:
            url.append(custom)
        return '/'.join(map(str, url))


class ReadAPI(BaseAPI):
    """Generic API for read-only operations."""

    def __call__(self, identifier=None, **kw):
        r"""
        Read data from api.

        Calls :func:`.get` if identifier is specified or :func:`.list`
        if not specified or equals to False.

        :param identifier: identifier of object. Defaults to ``None``.
        :param \**kw: additional keyword arguments are passed to requests.

        :raises: :class:`recommendpy.exceptions.RecommendAPIError`.

        :return: result of response.json().
        """
        if identifier:
            return self.get(identifier, **kw)
        return self.list(**kw)

    @check_token
    def get(self, identifier, **kw):
        r"""
        Read data from api by identifier.

        :param identifier: identifier of object (required).
        :param \**kw: additional keyword arguments are passed to requests.

        :raises: :class:`recommendpy.exceptions.RecommendAPIError`.

        :return: result of response.json().
        """
        return self._client.send(
            'get', self.get_path(identifier), **kw
        )

    @check_token
    def list(self, **kw):
        r"""
        Read data from api (all).

        :param \**kw: additional keyword arguments are passed to requests.

        :raises: :class:`recommendpy.exceptions.RecommendAPIError`.

        :return: result of response.json().
        """
        return self._client.send(
            'get', self.get_path(), **kw
        )


class CRUDAPI(ReadAPI):
    """Generic API for CRUD."""

    @check_token
    def create(self, identifier, data, **kw):
        r"""
        Create an object with specified identifier.

        :param identifier: identifier of object (required).
        :param data: data for object (required).
        :param \**kw: additional keyword arguments are passed to requests.

        :raises: :class:`recommendpy.exceptions.RecommendAPIError`.

        :return: result of response.json().
        """
        return self._client.send(
            'post', self.get_path(identifier), data, **kw
        )

    @check_token
    def update(self, identifier, data, **kw):
        r"""
        Update an object by identifier.

        :param identifier: identifier of object (required).
        :param data: data for object (required).
        :param \**kw: additional keyword arguments are passed to requests.

        :raises: :class:`recommendpy.exceptions.RecommendAPIError`.

        :return: result of response.json().
        """
        return self._client.send(
            'put', self.get_path(identifier), data, **kw
        )

    @check_token
    def delete(self, identifier, **kw):
        r"""
        Delete an object by identifier.

        :param identifier: identifier of object (required).
        :param \**kw: additional keyword arguments are passed to requests.

        :raises: :class:`recommendpy.exceptions.RecommendAPIError`.

        :return: result of response.json().
        """
        return self._client.send(
            'delete', self.get_path(identifier), **kw
        )


class SearchAPI(BaseAPI):
    @check_token
    def search(
        self, *args, **kw
    ):
        r"""
        Search data.

        :param \**kw: additional keyword arguments are passed to requests.

        :raises: :class:`recommendpy.exceptions.RecommendAPIError`.

        :return: result of response.json().
        """
        raise NotImplementedError()

    def search_iterator(self, start_skip=0, max_failed=5, **kw):
        r"""
        Iterator for :func:`search`.

        :param start_skip: Start ``skip`` parameter to search.
            Defaults to ``0``.
        :param max_failed: Max attempts count for one search request.
            Defaults to ``5``.
        :param \**kw: additional keyword arguments are passed to
            :func:`search`.

        :raises: :class:`recommendpy.exceptions.RecommendAPIError`
            if ``max_failed`` reached.

        :return: generator for search results.
        :yields: search result
        """
        skip = start_skip
        failed_count = 0
        limit = 3000
        while True:
            try:
                result = self.search(skip=skip, limit=limit, **kw)

                failed_count = 0
                if not isinstance(result, dict):
                    raise RecommendAPIError('Empty result.')

                for item in result.get('data', []):
                    yield item
                limit = result.get('limit', 0)
                if result.get('total', 0) < limit:
                    break
                skip += limit
            except RecommendAPIError as e:
                failed_count += 1
                if failed_count > max_failed:
                    raise e
