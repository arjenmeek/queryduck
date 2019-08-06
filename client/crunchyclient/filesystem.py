import datetime
import hashlib
import base64

from pathlib import Path, PurePath

class LocalFile(object):
    """Represents a file on a local filesystem"""

    def __init__(self, path, root):
        self.path = path
        self.root = root
        stat = self.path.stat()
        self.size = stat.st_size
        self.mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
        self.sha256 = None

    def __repr__(self):
        return '<LocalFile path="{}" size={} mtime="{}">'.format(self.get_printable_path(), self.size, self.get_mtime_string())

    def __json__(self):
        fields = {
            'path': str(self.get_relative_path()),
            'size': self.size,
            'sha256': base64.b64encode(self.get_sha256()).decode(),
            'mtime': self.get_mtime_string(),
            'lastverify': datetime.datetime.now().isoformat(),
        }
        return fields

    def get_mtime_string(self):
        mtime_string = self.mtime.isoformat()
        if len(mtime_string) == 19:
            mtime_string += '.000000'
        return mtime_string

    def get_relative_path(self):
        return self.path.relative_to(self.root)

    def get_printable_path(self):
        return str(self.get_relative_path()).encode('utf-8', 'surrogateescape').decode('utf-8', 'replace')

    def get_key(self):
        return str(self.get_relative_path())

    def get_sha256(self):
        if self.sha256 is None:
            with open(str(self.path), 'rb') as f:
                self.sha256 = hashlib.sha256(f.read()).digest()
        return self.sha256


class LocalFileIterator(object):
    """Iterates through all files within a local filetree in a fixed order."""

    def __init__(self, root):
        """Initialize the Iterator based on root, provided as a Path instance"""
        self.root = root
        self.stack = [self.root]

    def __iter__(self):
        return self

    @staticmethod
    def sortkey(entry):
        """Return key for use in sorting functions.

        The key ensures that the sort order across subdirectories will match the order
        that a database would return for full path strings with '/' as separator.
        """
        if entry.is_dir():
            return bytes(entry) + b'/'
        else:
            return bytes(entry)

    def __next__(self):
        try:
            p = self.stack.pop()
            while p.is_dir() or p.is_symlink():
                if p.is_dir():
                    self.stack += sorted(p.iterdir(), key=self.sortkey, reverse=True)
                p = self.stack.pop()
        except IndexError:
            raise StopIteration

        local_file = LocalFile(p, self.root)
        return local_file


class ApiFile(object):

    def __init__(self, data):
        self.id = data['id']
        self.path = PurePath(data['path'])
        self.sha256 = base64.b64decode(data['sha256'].encode('utf-8'))
        self.mtime = datetime.datetime.strptime(data['mtime'], "%Y-%m-%dT%H:%M:%S.%f")
        self.size = data['size']

    def __repr__(self):
        return '<ApiFile  path="{}" size={} mtime="{}">'.format(self.get_printable_path(), self.size, self.get_mtime_string())

    def get_mtime_string(self):
        mtime_string = self.mtime.isoformat()
        if len(mtime_string) == 19:
            mtime_string += '.000000'
        return mtime_string

    def get_relative_path(self):
        return self.path

    def get_printable_path(self):
        return str(self.path).encode('utf-8', 'surrogateescape').decode('utf-8', 'replace')

    def get_key(self):
        return str(self.path)

    def delete_action(self):
        action_data = {
            'action': 'delete',
            'path': str(self.path),
        }
        return action_data



class ApiFileIterator(object):

    preferred_limit = 10000

    def __init__(self, api, reference):
        self.api = api
        self.reference = reference
        self.results = None
        self.idx = 0
        self.prev = PurePath('.')

    def __iter__(self):
        return self

    def _load_next(self):
        if self.results is None:
            params = {'limit': self.preferred_limit}
            response = self.api.find_raw_volume_files(self.reference, params)
        else:
            after = base64.b64encode(os.fsencode(self.results[self.limit-1]['path'])).decode()
            params = {'after': after, 'limit': self.preferred_limit}
            response = self.api.get('volumes/{}/files'.format(self.reference), params=params)
        self.results = response['results']
        self.limit = response['limit']
        self.idx = 0

    def __next__(self):
        if self.results is None or self.idx >= self.limit:
            self._load_next()
        try:
            api_file = ApiFile(self.results[self.idx])
            self.idx += 1
        except IndexError:
            raise StopIteration
        self.prev = api_file.get_relative_path()
        return api_file


class CombinedIterator(object):
    """Combines two iterators, returning pairs based on sort order.

    When the next items for both iterators have different sort values, only the "lowest" value item
    is returned, in a tuple of the form (leftitem, None) or (None, rightitem). This also happens
    when one of the iterators has run out of items.

    When the next item for both iterators have equal sort values, both are returned in a tuple of
    the form (leftitem, rightitem).

    The CombinedIterator ends when both input iterators have run out of items, at which point each
    item from both input iterators will have been returned exactly once.
    """

    def __init__(self, left, right, key):
        self.left = left
        self.right = right
        self.key = key
        self._advance_left()
        self._advance_right()

    def __iter__(self):
        return self

    def _advance_left(self):
        if self.left is not None:
            try:
                self.cur_left = self.left.__next__()
            except StopIteration:
                self.left = None
                self.cur_left = None

    def _advance_right(self):
        if self.right is not None:
            try:
                self.cur_right = self.right.__next__()
            except StopIteration:
                self.right = None
                self.cur_right = None

    def __next__(self):
        if self.left is None and self.right is None:
            raise StopIteration
        elif self.right is None or (self.left is not None and self.key(self.cur_left) < self.key(self.cur_right)):
            retval = (self.cur_left, None)
            self._advance_left()
        elif self.left is None or self.key(self.cur_left) > self.key(self.cur_right):
            retval = (None, self.cur_right)
            self._advance_right()
        else:
            retval = (self.cur_left, self.cur_right)
            self._advance_left()
            self._advance_right()

        return retval


class FileApiWriter(object):

    def __init__(self, api, volume_reference, flush_treshold=1000):
        self.api = api
        self.volume_reference = volume_reference
        self.flush_treshold = 1000
        self.files = {}

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.flush()

    def create_file(self, f):
        print("create file", f.get_printable_path())
        self.files[f.get_key()] = {
            'new': True,
            'size': f.size,
            'sha256': base64.b64encode(f.get_sha256()).decode(),
            'mtime': f.get_mtime_string(),
            'lastverify': datetime.datetime.now().isoformat(),
        }
        self.check()

    def update_file(self, f):
        print("update file", f.get_printable_path())
        self.files[f.get_key()] = {
            'new': False,
            'size': f.size,
            'sha256': base64.b64encode(f.get_sha256()).decode(),
            'mtime': f.get_mtime_string(),
            'lastverify': datetime.datetime.now().isoformat(),
        }
        self.check()

    def delete_file(self, f):
        print("delete file", f.get_printable_path())
        self.files[f.get_key()] = None
        self.check()

    def check(self):
        if len(self.files) >= self.flush_treshold:
            self.flush()

    def flush(self):
        if self.files:
            self.api.mutate_volume_files(self.volume_reference, self.files)
        self.files = {}


class VolumeHandler(object):

    def __init__(self, volume, api):
        self.volume = volume
        self.api = api

    def update(self, path):
        print("updating", self.volume, path)

        combined = CombinedIterator(
            LocalFileIterator(Path(path)),
            ApiFileIterator(self.api, self.volume['reference']),
            lambda f: f.get_relative_path()
        )

        with FileApiWriter(self.api, self.volume['reference']) as writer:
            for local_file, api_file in combined:
                if api_file is None:
                    writer.create_file(local_file)
                elif local_file is None:
                    writer.delete_file(api_file)
                elif local_file.mtime != api_file.mtime or local_file.size != api_file.size:
                    writer.update_file(local_file)
