#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import certificate map to terraform code
"""
import subprocess
import json
import re
from utils.utils import to_snake_case, tf_name

def get_certificate_maps(project: str):
    """
    Use gcloud cli to get certificate maps
    :param project: GCP Project name
    :return: JSON
    """
    result = subprocess.run([
        'gcloud', 'certificate-manager', 'maps', 'list',
        '--project', f'{project}', '--format=json'],
        capture_output=True,
        check=False,
        text=True)
    if result.returncode == 0:
        return json.loads(result.stdout)
    return None

def get_certificate_map_entries(project : str, certificate_map_name: str):
    """
    Use gcloud cli to get certificate map entries.
    :param project: GCP Project name
    :param certificate_map_name: Certificate map name
    :return: JSON
    """
    result = subprocess.run([
        'gcloud', 'certificate-manager', 'maps', 'entries',
        'list', '--map', f'{certificate_map_name}', '--project', f'{project}', '--format=json'],
        capture_output=True,
        check=False,
        text=True)
    if result.returncode == 0:
        return json.loads(result.stdout)
    return None



def create_certificate_map_and_entries(project, map, map_entries):
    """
    Create Terraform code from JSON
    :param project: GCP Project name
    :param map: JSON certificate map
    :param: map_entries: JSON certificate map entries
    :return:
    """
    importlines = []
    map_name = map['name'].split('/')[-1]
    filename = f'certificate_map_{tf_name(map_name)}_{tf_name(project)}.tf'
    with open(filename, 'w', encoding='UTF-8') as f:
        f.write(f'resource "google_certificate_manager_certificate_map" "{tf_name(map_name)}" {{\n')
        f.write(f'  project     = "{project}"\n')
        f.write(f'  name        = "{map_name}"\n')
        f.write(f'  description = "{map.get('description','')}"\n')
        f.write('}\n\n')
        importlines.append('import {\n')
        importlines.append(f'  id = "{map['name']}"\n')
        importlines.append(f'  to = google_certificate_manager_certificate_map.{tf_name(map_name)}\n')
        importlines.append('}\n\n')

        for entry in map_entries:
            map_entry_name =  entry['name'].split('/')[-1]
            f.write(f'resource "google_certificate_manager_certificate_map_entry" "{tf_name(map_entry_name)}" {{\n')
            f.write(f'  project      = "{project}"\n')
            f.write(f'  name         = "{map_entry_name}"\n')
            f.write(f'  map          = "{map_name}"\n')
            f.write(f'  hostname     = "{entry['hostname']}"\n')
            f.write(f"  certificates = [{', '.join(f'\"{cert}\"' for cert in entry['certificates'])}]\n")
            f.write('}\n')
            f.write('\n')

            importlines.append('import {\n')
            importlines.append(f'  to = google_certificate_manager_certificate_map_entry.{tf_name(map_entry_name)}\n')
            importlines.append(f'  id = "{entry['name']}"\n')
            importlines.append('}\n\n')
        f.write("#--Delete statements below after import--\n")
        f.writelines(importlines)



def import_certificate_maps(args):
    certificate_map_list = get_certificate_maps(args.project)
    if certificate_map_list:
        for certificate_map in certificate_map_list:
            map_entries = get_certificate_map_entries(args.project, certificate_map['name'].split('/')[-1])
            create_certificate_map_and_entries(args.project, certificate_map, map_entries)
    else:
        print('ERROR: No certificate maps found, check authentication & project name.')