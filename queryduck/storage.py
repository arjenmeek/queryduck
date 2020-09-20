import hashlib
import os

from base64 import urlsafe_b64encode
from functools import partial
from datetime import datetime as dt
from pathlib import Path

from .types import File

from .utility import (
    CombinedIterator,
    safe_string,
)


class VolumeFileAnalyzer:
    def __init__(self, volume_config):
        self.volumes = {k: Path(v["path"]) for k, v in volume_config.items()}

    def analyze(self, path):
        if path.is_dir():
            raise UserError("Cannot process directory: {}".format(real))
        for volume_reference, volume_path in self.volumes.items():
            if volume_path in path.parents:
                subpath = path.relative_to(volume_path)
                file_ = File(volume=volume_reference, path=bytes(subpath))
                break
        else:
            raise UserError("No volume found for {}".format(path))
        return file_


class VolumeProcessor:
    def __init__(self, conn, reference, path=None, exclude=None):
        self.conn = conn
        self.reference = reference
        self.root = Path(path)
        self.exclude = exclude

    def update(self):
        tfi = TreeFileIterator(self.root, self.exclude)
        afi = ApiFileIterator(self.conn, self.reference)
        ci = CombinedIterator(
            tfi, afi, lambda x: str(x.relative_to(tfi.root)), lambda x: x["path"]
        )
        with FileUpdater(self.conn, self.reference) as updater:
            for local, remote in ci:
                k, v = self._update_file_status(local, remote)
                if k:
                    updater.add(k, v)

    def _update_file_status(self, local, remote):
        if local is None:
            print("DELETED", safe_string(remote["path"]))
            return remote["path"], None
        elif (
            remote is None
            or local.stat().st_size != remote["size"]
            or dt.fromtimestamp(local.stat().st_mtime)
            != dt.fromisoformat(remote["mtime"])
        ):
            relpath = str(local.relative_to(self.root))
            print(
                "NEW" if remote is None else "CHANGED",
                relpath.encode("utf-8", errors="replace"),
            )
            return relpath, self._process_file(local)
        else:
            return None, remote

    def _get_file_sha256(self, path):
        s = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(partial(f.read, 256 * 1024), b""):
                s.update(chunk)
        return s.digest()

    def _process_file(self, path):
        try:
            file_info = {
                "mtime": dt.fromtimestamp(path.stat().st_mtime).isoformat(),
                "size": path.stat().st_size,
                "lastverify": dt.now().isoformat(),
                "sha256": urlsafe_b64encode(self._get_file_sha256(path)).decode(
                    "utf-8"
                ),
            }
        except PermissionError:
            print("Permission error, ignoring:", path)
            file_info = None
        return file_info


class FileUpdater(object):
    def __init__(self, conn, reference, num_treshold=1000, size_treshold=1073741824):
        self.conn = conn
        self.reference = reference
        self.num_treshold = num_treshold
        self.size_treshold = size_treshold
        self.batch = {}

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.flush()

    def add(self, key, value):
        self.batch[key] = value
        self.check()

    def check(self):
        total_size = sum(
            [v["size"] for v in self.batch.values() if v is not None and "size" in v]
        )
        if len(self.batch) >= self.num_treshold or total_size >= self.size_treshold:
            self.flush()

    def flush(self):
        if len(self.batch):
            print("[{},{}] Send file batch...", end="")
            self.conn.mutate_files(self.reference, self.batch)
            print(" done.")
            self.batch = {}


class TreeFileIterator:
    def __init__(self, root, exclude=None):
        self.root = root
        self.stack = [self.root]
        self.exclude = exclude

    def __iter__(self):
        return self

    @staticmethod
    def sortkey(entry):
        if entry.is_dir():
            return bytes(entry) + b"/"
        else:
            return bytes(entry)

    def _is_excluded(self, path):
        if self.exclude is not None:
            for e in self.exclude:
                if path.match(e):
                    return True
        return False

    def __next__(self):
        try:
            p = self.stack.pop()
            while True:
                if p.is_symlink() or self._is_excluded(p):
                    p = self.stack.pop()
                elif p.is_dir():
                    self.stack += sorted(p.iterdir(), key=self.sortkey, reverse=True)
                    p = self.stack.pop()
                else:
                    break
        except IndexError:
            raise StopIteration

        return p


class ApiFileIterator:

    preferred_limit = 10000

    def __init__(self, api, reference, without_statements=None):
        self.api = api
        self.reference = reference
        self.without_statements = without_statements
        self.results = None
        self.idx = 0

    def __iter__(self):
        return self

    def _load_next(self):
        if self.results is None:
            params = {"limit": self.preferred_limit}
            if self.without_statements:
                params["without_statements"] = 1
            response = self.api.get(
                "volumes/{}/files".format(self.reference), params=params
            )
        else:
            after = urlsafe_b64encode(
                os.fsencode(self.results[self.limit - 1]["path"])
            ).decode()
            params = {"after": after, "limit": self.preferred_limit}
            if self.without_statements:
                params["without_statements"] = 1
            response = self.api.get(
                "volumes/{}/files".format(self.reference), params=params
            )
        self.results = response["results"]
        self.limit = response["limit"]
        self.idx = 0

    def __next__(self):
        if self.results is None or self.idx >= self.limit:
            self._load_next()
        try:
            api_file = self.results[self.idx]
            self.idx += 1
        except IndexError:
            raise StopIteration
        return api_file
