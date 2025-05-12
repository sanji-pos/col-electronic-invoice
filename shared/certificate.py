import os
import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import pkcs12
from typing import NamedTuple

from .config import Config

_config = Config()

class CertificateData(NamedTuple):
    private_key: object
    firmante: object
    emisor: object
    ca_raiz: object
    politica_file: object

class CertificateLoader:
    def __init__(self, sign_password, sign_file_b64):
        self._sign_password =  sign_password
        self._security = None
        self._sign_file_b64 = sign_file_b64
        self.load()

    def load(self):
        pfx_data = base64.b64decode(self._sign_file_b64)
        private_key, firmante, additional_certs = pkcs12.load_key_and_certificates(
            pfx_data,
            self._sign_password.encode(),
            default_backend()
        )

        data = {
            'private_key': private_key, 
            'firmante': firmante, 
            'emisor': additional_certs[0],
            'ca_raiz': additional_certs[1],
            'politica_file': ''
        }

        self._security = CertificateData(**data)

    @property
    def security(self):
        if not self._security:
            raise ValueError("Certificate data has not been loaded.")
        return self._security