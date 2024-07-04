import hashlib


def hash_file(file_path):
    md5_hash = hashlib.md5()
    with open(file_path, mode="rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()
