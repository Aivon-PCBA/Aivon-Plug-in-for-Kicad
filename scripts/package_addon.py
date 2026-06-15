#!/usr/bin/env python3
"""Build a PCM-compliant addon ZIP archive."""

import hashlib
import json
import os
import shutil
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(ROOT, 'dist')
INCLUDE_DIRS = ('plugins', 'resources')
INCLUDE_FILES = ('metadata.json',)
GITHUB_REPO = 'Aivon-PCBA/Aivon-Plug-in-for-Kicad'


def get_version():
    metadata_path = os.path.join(ROOT, 'metadata.json')
    with open(metadata_path, encoding='utf-8') as metadata_file:
        metadata = json.load(metadata_file)
    return metadata['versions'][0]['version']


def get_archive_name(version):
    return 'KiCadToAivon_v{}.zip'.format(version)


def get_download_url(version):
    return (
        'https://github.com/{}/releases/download/v{}/{}'
        .format(GITHUB_REPO, version, get_archive_name(version)))


def collect_install_size(staging_dir):
    total = 0
    for dirpath, _, filenames in os.walk(staging_dir):
        for filename in filenames:
            total += os.path.getsize(os.path.join(dirpath, filename))
    return total


def build_archive(output_path):
    with tempfile.TemporaryDirectory() as staging_dir:
        for dirname in INCLUDE_DIRS:
            src = os.path.join(ROOT, dirname)
            if not os.path.isdir(src):
                raise FileNotFoundError('Required directory not found: {}'.format(src))
            shutil.copytree(src, os.path.join(staging_dir, dirname))

        for filename in INCLUDE_FILES:
            src = os.path.join(ROOT, filename)
            if not os.path.isfile(src):
                raise FileNotFoundError('Required file not found: {}'.format(src))
            shutil.copy2(src, os.path.join(staging_dir, filename))

        install_size = collect_install_size(staging_dir)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with zipfile.ZipFile(
                output_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for dirpath, _, filenames in os.walk(staging_dir):
                for filename in filenames:
                    full_path = os.path.join(dirpath, filename)
                    archive_name = os.path.relpath(full_path, staging_dir)
                    archive.write(full_path, archive_name)

    with open(output_path, 'rb') as archive_file:
        download_sha256 = hashlib.sha256(archive_file.read()).hexdigest()

    return {
        'path': output_path,
        'download_size': os.path.getsize(output_path),
        'install_size': install_size,
        'download_sha256': download_sha256,
    }


def write_metadata_submission(version, package_info):
    metadata_path = os.path.join(ROOT, 'metadata.json')
    with open(metadata_path, encoding='utf-8') as metadata_file:
        metadata = json.load(metadata_file)

    submission = dict(metadata)
    submission['versions'] = [dict(metadata['versions'][0])]
    submission['versions'][0].update({
        'download_sha256': package_info['download_sha256'],
        'download_size': package_info['download_size'],
        'install_size': package_info['install_size'],
        'download_url': get_download_url(version),
    })

    output_path = os.path.join(
        DIST_DIR, 'metadata-submission-v{}.json'.format(version))
    with open(output_path, 'w', encoding='utf-8') as submission_file:
        json.dump(submission, submission_file, indent=4)
        submission_file.write('\n')

    return output_path


def main():
    version = get_version()
    archive_name = get_archive_name(version)
    output_path = os.path.join(DIST_DIR, archive_name)
    result = build_archive(output_path)
    submission_path = write_metadata_submission(version, result)

    print('Package created: {}'.format(result['path']))
    print('download_size: {}'.format(result['download_size']))
    print('install_size: {}'.format(result['install_size']))
    print('download_sha256: {}'.format(result['download_sha256']))
    print('download_url: {}'.format(get_download_url(version)))
    print()
    print('Metadata submission file: {}'.format(submission_path))
    print('Upload {} to GitHub Release v{}'.format(archive_name, version))
    return 0


if __name__ == '__main__':
    sys.exit(main())
