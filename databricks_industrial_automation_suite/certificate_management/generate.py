import os
import subprocess
from typing import Optional, Dict


class CertificateManager:
    """
    Manages the creation of OPC UA-compliant self-signed certificates
    using OpenSSL. Certificates are stored in a specified directory.
    """

    DEFAULT_CERTS_DIR = "/tmp/certs"
    DEFAULT_CERT_FILENAME = "client_cert.pem"
    DEFAULT_KEY_FILENAME = "client_key.pem"
    DEFAULT_CONFIG_FILENAME = "openssl_opcua.cnf"

    OPENSSL_CONFIG_TEMPLATE = """
[ req ]
default_bits        = 2048
default_md          = sha256
distinguished_name  = req_distinguished_name
x509_extensions     = v3_req
prompt              = no

[ req_distinguished_name ]
CN                 = OPCUA Client

[ v3_req ]
keyUsage           = critical, digitalSignature, keyEncipherment, dataEncipherment
extendedKeyUsage   = serverAuth, clientAuth
subjectAltName     = @alt_names

[ alt_names ]
DNS.1              = localhost
IP.1               = 127.0.0.1
URI.1              = urn:freeopcua:client
"""

    def __init__(self, certs_dir: Optional[str] = None) -> None:
        """
        Initializes the CertificateManager with paths for certificate files.

        Args:
            certs_dir (Optional[str]): Directory where certificates are stored.
                                       Defaults to DEFAULT_CERTS_DIR.
        """
        self.certs_dir = certs_dir or self.DEFAULT_CERTS_DIR
        self.client_cert = os.path.join(self.certs_dir, self.DEFAULT_CERT_FILENAME)
        self.client_key = os.path.join(self.certs_dir, self.DEFAULT_KEY_FILENAME)
        self.cert_config = os.path.join(self.certs_dir, self.DEFAULT_CONFIG_FILENAME)

        os.makedirs(self.certs_dir, exist_ok=True)

    def generate_certificate(self, overwrite: bool = False) -> Dict[str, str]:
        """
        Generates a self-signed client certificate and private key.

        Args:
            overwrite (bool): Whether to overwrite existing files.

        Returns:
            Dict[str, str]: Message and path to the generated certificate.

        Raises:
            RuntimeError: If OpenSSL operations fail.
        """
        if (
            os.path.exists(self.client_cert)
            and os.path.exists(self.client_key)
            and not overwrite
        ):
            return {
                "message": "Certificate and key already exist — skipping generation.",
                "certificate": self.client_cert,
            }

        try:
            self._write_openssl_config()

            self._run_openssl(["genpkey", "-algorithm", "RSA", "-out", self.client_key])

            self._run_openssl(
                [
                    "req",
                    "-x509",
                    "-new",
                    "-key",
                    self.client_key,
                    "-out",
                    self.client_cert,
                    "-days",
                    "1825",
                    "-config",
                    self.cert_config,
                ]
            )

            os.remove(self.cert_config)

            return {
                "message": "Client certificate generated successfully.",
                "certificate": self.client_cert,
            }

        except Exception as e:
            raise RuntimeError(f"Certificate generation failed: {str(e)}")

    def _write_openssl_config(self) -> None:
        """
        Writes the OpenSSL configuration file.
        """
        with open(self.cert_config, "w") as f:
            f.write(self.OPENSSL_CONFIG_TEMPLATE)

    @staticmethod
    def _run_openssl(command: list) -> None:
        """
        Runs an OpenSSL command with error handling.

        Args:
            command (list): List of OpenSSL command arguments.

        Raises:
            subprocess.CalledProcessError: If OpenSSL command fails.
        """
        subprocess.run(["openssl"] + command, check=True)
