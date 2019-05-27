import json

import requests
import uuid

from requests.exceptions import HTTPError

from crunchylib.exceptions import NotFoundError
from crunchylib.utility import deserialize_value, serialize_value


class BaseAPI(object):
    """Simple generic wrapper class for RESTful API's using the Requests module."""

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



class CrunchyAPI(BaseAPI):

    def get_raw_statement(self, uuid_):
        """Fetch a raw statement"""
        raw_statement = self.get('statements/{}'.format(serialize_value(uuid_)))
        return raw_statement

    def find_raw_statements(self, filter_strings=None, join_strings=None):
        """Retrieve multiple statements"""
        params = {}
        if filter_strings is not None:
            params['filter'] = filter_strings
        if join_strings is not None:
            params['join'] = join_strings

        response = self.get('statements', params)
        raw_results = response['results']
        raw_statements = response['statements']
        return raw_results, raw_statements

    def save_raw_statement(self, uuid_, raw_statement):
        """Persist a statement"""
        uuid_str = serialize_value(uuid_)
        self.put('statements/{}'.format(uuid_str), raw_statement)

    def delete_statement(self, uuid_):
        """Delete a statement"""
        uuid_str = serialize_value(uuid_)
        self.delete('statements/{}'.format(uuid_str))
