import json

import requests

from requests.exceptions import HTTPError

from .exceptions import NotFoundError


class BaseAPI(object):
    """Simple generic wrapper class for RESTful API's."""

    def __init__(self, url):
        """Make the provided API URL available."""
        self.url = url

    def _raise_from_request(self, r):
        """Call the raise_for_status Requests method and handle result."""
        try:
            r.raise_for_status()
        except HTTPError as e:
            if e.response.status_code == 404:
                raise NotFoundError()
            else:
                raise e

    def get(self, path, params=None):
        """Perform a GET request to a path."""
        r = requests.get('{}/{}'.format(self.url, path), params=params)
        self._raise_from_request(r)
        return r.json()

    def post(self, path, data):
        """Perform a POST request to a path with a JSON-serialized body."""
        r = requests.post('{}/{}'.format(self.url, path),
            data=json.dumps(data))
        self._raise_from_request(r)
        return r.json()

    def put(self, path, data):
        """Perform a PUT request to a path with a JSON-serialized body."""
        r = requests.put('{}/{}'.format(self.url, path),
            data=json.dumps(data))
        self._raise_from_request(r)
        return r.json()

    def delete(self, path, params=None):
        """Perform a DELETE request to a path."""
        r = requests.delete('{}/{}'.format(self.url, path), params=params)
        self._raise_from_request(r)
        return r.json()


class CrunchyAPI(BaseAPI):

    def get_schema(self, schema_uuid):
        schema = self.get('schemas/s:{}'.format(schema_uuid))
        return schema

    def establish_schema(self, schema_uuid, data):
        schema = self.post('schemas/s:{}'.format(schema_uuid), data)
        return schema

    def find_statements(self, filters=None):
        results = self.get('statements', filters)
        return results

    def query_statements(self, filters=None):
        results = self.post('statements/query',
            {'filters': filters if filters else []})
        return results

    def create_statements(self, statements):
        self.post('statements', statements)

    def mutate_files(self, volume_reference, files):
        self.post('volumes/{}/files'.format(volume_reference), files)

    def find_files(self, volume_reference, params):
        results = self.get('volumes/{}/files'.format(volume_reference),
            params)
        return results