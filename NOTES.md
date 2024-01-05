# Notes

- pykmip auth_suite must be set to TLS1.2 for Ubuntu 20.04 due to openssl 1.1.1f changes
- python 3.10+ default TLS libs and pykmip struggle to find a TLS 1.2 cipher to agree on, use pymongo[ocsp] for PyOpenSSL instead
