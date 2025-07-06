import os
import subprocess


# -----------------------------------------------------------------
# The following constants define the paths to the generated
# certificates within the Databricks File System.
# -----------------------------------------------------------------
CERTS_DIR = "/dbfs/FileStore/certs"
CLIENT_CERT = os.path.join(CERTS_DIR, "client_cert.pem")
CLIENT_KEY = os.path.join(CERTS_DIR, "client_key.pem")
CERT_CONFIG = os.path.join(CERTS_DIR, "openssl_opcua.cnf")


os.makedirs(CERTS_DIR, exist_ok=True)


#--------------------------------------------------------------------------
# The following OpenSSL configuration string, is used to create 
# a self-signed X.509 certificate that’s compliant 
# with OPC UA security requirements.
#--------------------------------------------------------------------------
OPENSSL_CONFIG = f"""
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


def generate_certificate(overwrite=False):
    """
    Generates an OPC UA-compliant client certificate and key.
    If cert and key already exist, skips generation unless `overwrite=True`.
    """
    if os.path.exists(CLIENT_CERT) and os.path.exists(CLIENT_KEY) and not overwrite:
        return {
            "message": "Certificate and key already exist — skipping generation.",
            "certificate": CLIENT_CERT,
        }

    try:
        # -------------------------------------
        # Write OpenSSL config
        # -------------------------------------
        with open(CERT_CONFIG, "w") as f:
            f.write(OPENSSL_CONFIG)

        # -------------------------------------
        # Generate private key
        # -------------------------------------
        subprocess.run(
            ["openssl", "genpkey", "-algorithm", "RSA", "-out", CLIENT_KEY], check=True
        )

        # -------------------------------------
        # Generate self-signed certificate
        # -------------------------------------
        subprocess.run(
            [
                "openssl",
                "req",
                "-x509",
                "-new",
                "-key",
                CLIENT_KEY,
                "-out",
                CLIENT_CERT,
                "-days",
                "1825",
                "-config",
                CERT_CONFIG,
            ],
            check=True,
        )

        os.remove(CERT_CONFIG)

        return {
            "message": "Client certificate generated successfully.",
            "certificate": CLIENT_CERT,
        }

    except Exception as e:
        raise RuntimeError(f"Certificate generation failed: {str(e)}")
