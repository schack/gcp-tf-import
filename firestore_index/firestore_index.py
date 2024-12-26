#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import firestore indexes to terraform code
"""
import subprocess
import json
import re
import argparse


def get_indexjson(project, database):
    """
    Use gcloud cli to get the indexes from Firestore
    :param project: GCP Project name
    :param database: Firestore database name
    :return: JSON
    """
    result = subprocess.run([
        'gcloud', 'firestore', 'indexes', 'composite', 'list',
        '--database', f'{database}', '--project', f'{project}', '--format=json'],
        capture_output=True,
        check=False,
        text=True)
    if result.returncode == 0:
        return json.loads(result.stdout)
    return None


def create_tf_indexes(project, database, indexlist, filename):
    """
    Create Terraform code from JSON index list
    :param project: GCP Project name
    :param database: Firestore database name
    :param indexlist: JSON index list
    :param filename: Output filename
    :return:
    """
    importlines = []
    if not filename:
        filename = f'firestore_index_{re.sub(r'[^a-zA-Z0-9]', '_', database).lower()}_{project}.tf'
    with open(filename, 'w', encoding='UTF-8') as f:
        for index in indexlist:
            match = re.search(r'collectionGroups/([^/]+)/indexes/(.+$)', index['name'])
            collection = match.group(1)
            indexid = match.group(2)
            f.write(f'resource "google_firestore_index" "{indexid}" {{\n')
            f.write(f'  project     = "{project}"\n')
            f.write(f'  database    = "{database}"\n')
            f.write(f'  api_scope   = "{index['apiScope']}"\n')
            f.write(f'  query_scope = "{index['queryScope']}"\n')
            f.write(f'  collection  = "{collection}"\n')
            print(f' Importing index for collection: {collection}')
            for field in index['fields']:
                f.write('  fields {\n')
                f.write(f'    field_path = "{field["fieldPath"]}"\n')
                f.write(f'    order      = "{field["order"]}"\n')
                f.write('  }\n')
            f.write('}\n')
            f.write('\n')
            importlines.append('import {\n')
            importlines.append(f'  to = google_firestore_index.{indexid}\n')
            importlines.append(f'  id = "{index['name']}"\n')
            importlines.append('}\n\n')
        f.writelines(importlines)


def main():
    """
    Main function to parse arguments and create Terraform files.
    """
    parser = argparse.ArgumentParser(description='Create Terraform code from Google Cloud Firestore indexes.')
    parser.add_argument('project', type=str, help='The ID of the Google Cloud project')
    parser.add_argument('--database', type=str, default='(default)',
                        help='The database to import indexes from (default: (default)')
    parser.add_argument('--filename', type=str, default=None,
                        help='The Terraform filename, default is firestore_index_<database>_<project>.tf')
    args = parser.parse_args()

    indexjson = get_indexjson(args.project, args.database)
    if indexjson:
        create_tf_indexes(args.project, args.database, indexjson, args.filename)
    else:
        print('ERROR: No indexes found, check authentication, project name & database name.')


if __name__ == '__main__':
    main()