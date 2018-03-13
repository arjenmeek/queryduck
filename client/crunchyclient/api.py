import json

import requests

from requests.exceptions import HTTPError

from crunchylib.exceptions import NotFoundError
from crunchylib.utility import deserialize_value, serialize_value


class API(object):
    """Simplistic generic wrapper class for RESTful API's using the Requests module."""

    def __init__(self, url):
        """Make the provided API URL available."""
        self.url = url

    def _raise_from_request(self, r):
        """Call the raise_for_status Requests method and try to handle what happens."""
        try:
            r.raise_for_status()
        except HTTPError as e:
            if e.response.status_code == 404:
                raise NotFoundError()
            else:
                raise e

    def get(self, path, params=None):
        """Perform a GET request to a path with optional query parameters."""
        r = requests.get('{}/{}'.format(self.url, path), params=params)
        self._raise_from_request(r)
        return r.json()

    def post(self, path, data):
        """Perform a POST request to a path with a JSON-serialized body."""
        r = requests.post('{}/{}'.format(self.url, path), data=json.dumps(data))
        self._raise_from_request(r)
        return r.json()

    def put(self, path, data):
        """Perform a PUT request to a path with a JSON-serialized body."""
        r = requests.put('{}/{}'.format(self.url, path), data=json.dumps(data))
        self._raise_from_request(r)
        return r.json()

    def delete(self, path, params=None):
        """Perform a DELETE request to a path with optional query parameters."""
        r = requests.delete('{}/{}'.format(self.url, path), params=params)
        self._raise_from_request(r)
        return r.json()


class StatementAPI(API):
    """Provides a Statement-specific wrapper around the API. Statements are represented by quads of values."""

    def _process_raw_statement(self, raw_statement):
        """Deserialize a set of raw values"""
        elements = [deserialize_value(v) for v in raw_statement]
        return elements

    def get_statement(self, uuid_):
        """Fetch a statement"""
        raw_statement = self.get('statements/{}'.format(serialize_value(uuid_)))
        quad = [deserialize_value(v) for v in raw_statement]
        return quad

    def find_statements(self):
        """Retrieve multiple statements"""
        raw_statements = self.get('statements')
        processed_statements = [self._process_raw_statement(s) for s in raw_statements]
        return processed_statements

    def save_statement(self, quad):
        """Persist a statement"""
        raw_quad = [serialize_value(v) for v in quad]
        self.put('statements/{}'.format(raw_quad[0]), raw_quad)

    def delete_statement(self, uuid_):
        """Delete a statement"""
        uuid_str = serialize_value(uuid_)
        self.delete('statements/{}'.format(uuid_str))
