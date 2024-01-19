from pymongo import MongoClient
from pymongo.encryption_options import AutoEncryptionOpts
from pymongo.encryption import ClientEncryption
import base64
import os
from bson.codec_options import CodecOptions
from bson.binary import STANDARD, UUID
import pprint

KMIP_KMS_ENDPOINT = os.getenv('KMIP_KMS_ENDPOINT')
MONGODB_URI = os.getenv('MONGODB_URI')
KMIP_TLS_CA_FILE = os.getenv('KMIP_TLS_CA_FILE')
KMIP_TLS_CERT_FILE = os.getenv('KMIP_TLS_CERT_FILE')
SHARED_LIB_PATH = "/app/lib/mongo_crypt_v1.so"

# start-key-vault
key_vault_namespace = "encryption.__keyVault"
# end-key-vault

connection_string = MONGODB_URI

# start-kmsproviders
provider = "kmip"
kms_providers = {provider: {"endpoint": KMIP_KMS_ENDPOINT}}
# end-kmsproviders

# start-schema
# Make All fields random to use json pointer to reference key-id
json_schema = {
    "bsonType": "object",
    "encryptMetadata": {"keyId": "/key-id"},
    "properties": {
        "insurance": {
            "bsonType": "object",
            "properties": {
                "policyNumber": {
                    "encrypt": {
                        "bsonType": "int",
                        "algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512-Random",
                    }
                }
            },
        },
        "medicalRecords": {
            "encrypt": {
                "bsonType": "array",
                "algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512-Random",
            }
        },
        "bloodType": {
            "encrypt": {
                "bsonType": "string",
                "algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512-Random",
            }
        },
        "ssn": {
            "encrypt": {
                "bsonType": "int",
                "algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512-Random",
            }
        },
    },
}

patient_schema = {"medicalRecords.patients": json_schema}
# end-schema

# start-create-tls
tls_options = {
    "kmip": {
        "tlsCAFile": KMIP_TLS_CA_FILE,
        "tlsCertificateKeyFile": KMIP_TLS_CERT_FILE,
    }
}
# end-create-tls

# start-extra-options
extra_options = {"crypt_shared_lib_path": SHARED_LIB_PATH}
# end-extra-options

# start-client
fle_opts = AutoEncryptionOpts(
    kms_providers,
    key_vault_namespace,
    schema_map=patient_schema,
    kms_tls_options=tls_options,
    **extra_options
)
secureClient = MongoClient(connection_string, auto_encryption_opts=fle_opts, tls=True, tlsCAFile='/etc/certs/ca.crt')
# end-client

# start-insert
def insert_patient(
    collection, name, ssn, blood_type, medical_records, policy_number, provider
):
    insurance = {"policyNumber": policy_number, "provider": provider}
    doc = {
        "name": name,
        "ssn": ssn,
        "bloodType": blood_type,
        "medicalRecords": medical_records,
        "insurance": insurance,
        "key-id": "demo-data-key",
    }
    collection.insert_one(doc)


medical_record = [{"weight": 180, "bloodPressure": "120/80"}]
insert_patient(
    secureClient.medicalRecords.patients,
    "Jon Doe",
    241014209,
    "AB+",
    medical_record,
    123142,
    "MaestCare",
)
# end-insert
regularClient = MongoClient(connection_string, tls=True, tlsCAFile='/etc/certs/ca.crt')
# start-find
print("Finding a document with regular (non-encrypted) client.")
result = regularClient.medicalRecords.patients.find_one({"name": "Jon Doe"})
pprint.pprint(result)

print("Finding a document with encrypted client, searching on an encrypted field")
pprint.pprint(secureClient.medicalRecords.patients.find_one({"name": "Jon Doe"}))
# end-find