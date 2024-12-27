import argparse

from importers.firestore_index import import_firestore_index
from importers.dns_authorization import import_dns_authorization

def main():
    """
    Main function to parse arguments and execute importers.
    """
    parser = argparse.ArgumentParser(description='Create Terraform code from Google Cloud resources.')
    subparsers = parser.add_subparsers(dest="command", required=True)

    firestore_index_parser = subparsers.add_parser("firestore-index", help="Import Firestore indexes")
    dns_authz_parser = subparsers.add_parser("dns-authz", help="Import DNS authorizations")


    firestore_index_parser.add_argument('project', type=str,
                                        help='The ID of the Google Cloud project')
    firestore_index_parser.add_argument('--database', type=str, default='(default)',
                                        help='The database to import indexes from (default: (default)')
    firestore_index_parser.add_argument('--filename', type=str, default=None,
                                        help='The Terraform filename, default is firestore_index_<database>_<project>.tf')

    dns_authz_parser.add_argument('project', type=str,
                                        help='The ID of the Google Cloud project')
    dns_authz_parser.add_argument('--filename', type=str, default=None,
                                        help='The Terraform filename, default is dns_authorization_<project>.tf')


    args = parser.parse_args()

    if args.command == 'firestore-index':
        import_firestore_index(args)
    elif args.command == 'dns-authz':
        import_dns_authorization(args)




if __name__ == '__main__':
    main()