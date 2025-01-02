#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import certificates to terraform code
"""
import subprocess
import json
from utils.utils import to_snake_case, tf_name

def get_certificates(project: str):
    """
    Use gcloud cli to get certificates.
    :param project: GCP Project name
    :return: JSON
    """
    result = subprocess.run([
        'gcloud', 'certificate-manager', 'certificates', 'list',
        '--project', f'{project}', '--format=json'],
        capture_output=True,
        check=False,
        text=True)
    if result.returncode == 0:
        return json.loads(result.stdout)
    return None


def create_certificate(project, certificate_list):
    """
    Create Terraform code from JSON
    :param project: GCP Project name
    :param certificate_list: JSON certificates
    :return:
    """
    importlines = []
    filename = f'certificate_manager_certificate_{tf_name(project)}.tf'
    with open(filename, 'w', encoding='UTF-8') as f:
        for certificate in certificate_list:
            certificate_name = certificate['name'].split('/')[-1]
            f.write(f'resource "google_certificate_manager_certificate" "{tf_name(certificate_name)}" {{\n')
            f.write(f'  project     = "{project}"\n')
            f.write(f'  name        = "{certificate_name}"\n')
            f.write(f'  description = "{certificate.get('description','')}"\n')
            f.write( '  managed {\n')
            f.write('    domains = [\n')
            for domain in certificate['managed']['domains']:
                f.write(f'      "{domain}",\n')
            f.write('    ]\n')
            f.write( '    dns_authorizations = [\n')
            for dns_auth in certificate['managed']['dnsAuthorizations']:
                f.write(f'      "{dns_auth}",\n')
            f.write('    ]\n')
            f.write('  }\n')
            f.write('}\n\n')

            importlines.append('import {\n')
            importlines.append(f'  to = google_certificate_manager_certificate.{tf_name(certificate_name)}\n')
            importlines.append(f'  id = "{certificate['name']}"\n')
            importlines.append('}\n\n')

        f.write("#--Delete statements below after import--\n")
        f.writelines(importlines)



def import_certificate(args):
    certificate_list = get_certificates(args.project)
    if certificate_list:
        create_certificate(args.project, certificate_list)
    else:
        print('ERROR: No certificates found, check authentication & project name.')
