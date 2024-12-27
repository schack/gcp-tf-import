#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import DNS authorization to terraform code
"""
import subprocess
import json
import re
from utils.utils import to_snake_case, tf_name

def get_dnsauthzjson(project):
    """
    Use gcloud cli to get dns authorizations
    :param project: GCP Project name
    :return: JSON
    """
    result = subprocess.run([
        'gcloud', 'certificate-manager', 'dns-authorizations', 'list',
        '--project', f'{project}', '--format=json'],
        capture_output=True,
        check=False,
        text=True)
    if result.returncode == 0:
        return json.loads(result.stdout)
    return None

def create_dns_authz(project, dnsauthzlist, filename):
    """
    Create Terraform code from JSON
    :param project: GCP Project name
    :param dnsauthzlist: JSON dns authorizations
    :param filename: Output filename
    :return:
    """
    importlines = []
    if not filename:
        filename = f'dns_authorizations_{to_snake_case(project)}.tf'
    with open(filename, 'w', encoding='UTF-8') as f:
        for dnsauthz in dnsauthzlist:
            # "name": "projects/storytel-148812/locations/global/dnsAuthorizations/mofibo-com-dns-authorization",
            match = re.search(r'locations/([^/]+)/dnsAuthorizations/(.+$)', dnsauthz['name'])
            location = match.group(1)
            dnsauthzid = match.group(2)
            f.write(f'resource "google_certificate_manager_dns_authorization" "{tf_name(dnsauthzid)}" {{\n')
            f.write(f'  project  = "{project}"\n')
            f.write(f'  name     = "{dnsauthzid}"\n')
            f.write(f'  type     = "{dnsauthz['type']}"\n')
            f.write(f'  location = "{location}"\n')
            f.write(f'  domain   = "{dnsauthz['domain']}"\n')

            f.write('}\n')
            f.write('\n')

            f.write(f'output "{tf_name(dnsauthz['domain'])}_record_name" {{\n')
            f.write(f'  value = google_certificate_manager_dns_authorization.{tf_name(dnsauthzid)}.dns_resource_record.0.name\n')
            f.write('}\n')

            f.write(f'output "{tf_name(dnsauthz['domain'])}_record_value" {{\n')
            f.write(f'  value = google_certificate_manager_dns_authorization.{tf_name(dnsauthzid)}.dns_resource_record.0.data\n')
            f.write('}\n')
            f.write('\n\n')

            importlines.append('import {\n')
            importlines.append(f'  to = google_certificate_manager_dns_authorization.{tf_name(dnsauthzid)}\n')
            importlines.append(f'  id = "{dnsauthz['name']}"\n')
            importlines.append('}\n\n')
        f.write("#--Delete statements below after import--\n")
        f.writelines(importlines)



def import_dns_authorization(args):
    dnsauthzlist = get_dnsauthzjson(args.project)
    if dnsauthzlist:
        create_dns_authz(args.project, dnsauthzlist, args.filename)
    else:
        print('ERROR: No indexes found, check authentication, project name & database name.')