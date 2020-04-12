import base64
import uuid

from collections import defaultdict

from .exceptions import CVValueError


class Statement:

    def __init__(self, uuid_str=None, uuid_=None, id_=None, triple=None, attribute_loader=None):
        self.uuid = uuid.UUID(uuid_str) if uuid_ is None else uuid_
        self.id = id_
        self.attributes = defaultdict(list)
        self.triple = triple
        self.attribute_loader = attribute_loader

    def __getitem__(self, attr):
        """Make Statement subscriptable"""
        if self.attribute_loader is None:
            raise CVValueError("Attempted to access Statement attribute but no loader is present")
        return self.attribute_loader(self, attr)

    def __hash__(self):
        if self.uuid is None:
            raise CVValueError("Attempted to use Statement without known UUID as hashable")
        return hash(self.uuid)

    def __json__(self, request):
        data = {
            'uuid': 'uuid:{}'.format(self.uuid),
            '_ref': 's:{}'.format(self.uuid),
        }
        for k, vlist in self.attributes.items():
            data[k] = []
            for v in vlist:
                data[k].append(v.serialize())
        return data

    def __repr__(self):
        parts = ['{}={}'.format(k, getattr(self, k))
            for k in ('uuid', 'id')
            if getattr(self, k) is not None
        ]
        if self.triple:
            parts.append('complete')
        return '<Statement {}>'.format(' '.join(parts))


class Blob:

    def __init__(self, sha256_str=None, sha256=None, id_=None):
        self.sha256 = base64.b64decode(sha256_str) if sha256 is None else sha256
        self.id = id_

    def encoded_sha256(self):
        r = None if self.sha256 is None else base64.b64encode(self.sha256).decode('utf-8')
        return r

    def __repr__(self):
        return '<Blob id={} sha256={}>'.format(self.id, None if self.sha256 is None else self.encoded_sha256())
