from .base import BaseAPI, ReadAPI, SearchAPI, check_token

__all__ = [
    'MessagingAPI',
    'MessagingChannelBatchAPI',
    'MessagingChannelEmailAPI',
    'MessagingChannelPushAPI',
]


class MessagingAPI(BaseAPI):
    """Messaging API."""

    @check_token
    def smart_campaign(self, **kw):
        r"""
        Return campaigns.

        :param \**kw: additional keyword arguments are passed to requests.

        :raises: :class:`recommendpy.exceptions.RecommendAPIError`.

        :return: result of response.json().
        """
        return self._client.send(
            'get', self.get_path(method='smart_campaign'), **kw
        )


class MessagingChannelBatchAPI(BaseAPI):
    """Messaging Channel Batch API."""

    @check_token
    def email(self, data, **kw):
        r"""
        Upload contacts batch data.

        :param data: data for upload (required).
        :param \**kw: additional keyword arguments are passed to requests.

        :raises: :class:`recommendpy.exceptions.RecommendAPIError`.

        :return: result of response.json().
        """
        return self._client.send(
            'post', self.get_path(method='email'), data, **kw
        )

    @check_token
    def push_token(self, data, **kw):
        r"""
        Upload contacts batch data.

        :param data: data for upload (required).
        :param \**kw: additional keyword arguments are passed to requests.

        :raises: :class:`recommendpy.exceptions.RecommendAPIError`.

        :return: result of response.json().
        """
        return self._client.send(
            'post', self.get_path(method='push_token'), data, **kw
        )


class MessagingChannelEmailAPI(ReadAPI, SearchAPI):
    """Messaging Channel Email API."""

    @check_token
    def search(
        self, from_date=None, to_date=None, skip=None,
        subscription_statuses=None, emails=None, limit=None, **kw
    ):
        r"""
        Search Email channels.

        :param from_date: Filter from date in timestamp (include).
            Defaults to ``None``.
        :param to_date: Filter to date in timestamp. Defaults to ``None``.
        :param skip: Skip documents. Defaults to ``None``.
        :param limit: Limit documents. Defaults to ``None``.
        :param subscription_statuses: list of subscription_statuses.
            Defaults to ``None``.
        :param emails: list of emails. Defaults to ``None``.
        :param \**kw: additional keyword arguments are passed to requests.

        .. note::
                If you want to return all channels without considering their
                status, pass ``"{"subscription_statuses": []}"`` (default)

        :raises: :class:`recommendpy.exceptions.RecommendAPIError`.

        :return: result of response.json().
        """
        params = {}
        if from_date:
            params['from_date'] = from_date
        if to_date:
            params['to_date'] = to_date
        if skip:
            params['skip'] = skip
        if limit:
            params['limit'] = limit

        data = {
            'subscription_statuses': subscription_statuses or [],
        }
        if emails:
            data['emails'] = emails

        return self._client.send(
            'post', self.get_path(method='search'), data, params=params, **kw
        )


class MessagingChannelPushAPI(SearchAPI):
    """Messaging Channel Push API."""

    @check_token
    def search(self, **kw):
        r"""
        Search Push Notifications Subscriptions.

        :param \**kw: additional keyword arguments are passed to requests.

        :raises: :class:`recommendpy.exceptions.RecommendAPIError`.

        :return: result of response.json().
        """
        return self._client.send(
            'post', self.get_path(method='search'), **kw
        )
