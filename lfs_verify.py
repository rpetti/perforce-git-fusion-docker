#!/usr/bin/env python3

import subprocess
import hashlib
import argparse
import marshal


def decode_dict(d):
    newd = {}
    for k, v in d.items():
        key = k
        if isinstance(k, bytes):
            key = k.decode('utf-8', errors='replace')
        if isinstance(v, bytes):
            newd[key] = v.decode('utf-8', errors='replace')
        elif isinstance(v, dict):
            newd[key] = decode_dict(v)
    return newd


def get_filelogs(args):
    prefix = f"//.git-fusion/objects/repos/{args.repo}/lfs/sha256/"
    p = subprocess.Popen(["p4", "-G", "filelog", f"{prefix}..."], stdout=subprocess.PIPE)
    while True:
        data = None
        try:
            data = marshal.load(p.stdout)
        except EOFError:
            break
        if not data:
            break
        data = decode_dict(data)
        if 'code' in data and data['code'] == 'error':
            raise Exception(f"Error: {data['data']}")
        data['storedSha256'] = data['depotFile'].removeprefix(prefix).replace('/', '')
        yield data


def is_potentially_bad_filelog(filelog):
    # was potentially branched from the wrong revision
    if 'erev0,0' in filelog and filelog['erev0,0'] != "#1":
        return True
    return False


def _calculate_sha256_of_filepath(filepath):
    p = subprocess.Popen(["p4", "print", "-k", "-q", filepath], stdout=subprocess.PIPE)
    sha256_hash = hashlib.sha256()
    for block in iter(lambda: p.stdout.read(4096), b""):
        sha256_hash.update(block)
    return sha256_hash.hexdigest()


def _calculate_sha256_of_lfs_object(filelog):
    return _calculate_sha256_of_filepath(filelog['depotFile'])


def verify(filelog):
    sha256 = _calculate_sha256_of_lfs_object(filelog)
    if sha256 != filelog['storedSha256']:
        return False
    return True


def _find_matching_revision(filelog, sha256):
    source_path = filelog['file0,0']
    end_rev = int(filelog['erev0,0'].removeprefix('#'))
    for revision in range(1, end_rev):
        if _calculate_sha256_of_filepath(f"{source_path}#{revision}") == sha256:
            return (source_path, revision)
    return None


def _sync(filepath):
    data = subprocess.run(["p4","-G", "sync", filepath], check=True, capture_output=True).stdout
    data = marshal.loads(data)
    data = decode_dict(data)
    if 'code' in data and data['code'] == 'error':
        if 'file(s) up-to-date' not in data['data']:
            raise Exception(data['data'])


def _copy(from_filepath, to_file):
    data = subprocess.run(["p4","-G", "copy", "-v", from_filepath, to_file], check=True, capture_output=True).stdout
    data = marshal.loads(data)
    data = decode_dict(data)
    if 'code' in data and data['code'] == 'error':
        if 'File(s) up-to-date' not in data['data']:
            raise Exception(data['data'])


def fix(filelog):
    filepath = _find_matching_revision(filelog, filelog['storedSha256'])
    if not filepath:
        print(f"{filelog['depotFile']} ERROR")
        return
    _sync(f"{filepath[0]}#{filepath[1]}")
    _copy(f"{filepath[0]}#{filepath[1]}", filelog['depotFile'])
    print(f"{filelog['depotFile']} FIXED")


def print_success_verify(filelog):
    print(f"{filelog['depotFile']} OK")


def print_failed_verify(filelog):
    print(f"{filelog['depotFile']} BAD")


def main():
    parser = argparse.ArgumentParser(description="Verify and fix LFS lazy copies in git-fusion")
    parser.add_argument("repo", help="repository name to verify")
    parser.add_argument("-a", "--all", action="store_true", help="verify all files, otherwise, only verify files that appear to have been copied incorrectly")
    parser.add_argument("-f", "--fix", action="store_true", help="attempt to fix any bad lazy copies")
    parser.add_argument("-q", "--quiet", action="store_true", help="only print bad files")

    args = parser.parse_args()

    filelogs = get_filelogs(args)
    if not args.all:
        filelogs = [f for f in filelogs if is_potentially_bad_filelog(f)]

    for filelog in filelogs:
        if not verify(filelog):
            print_failed_verify(filelog)
            if args.fix:
                fix(filelog)
        elif not args.quiet:
            print_success_verify(filelog)


if __name__ == "__main__":
    main()
