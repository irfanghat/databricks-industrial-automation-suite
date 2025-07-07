import asyncio
from databricks_industrial_automation_suite.integrations.opcua import OPCUAClient


oc = OPCUAClient(
    server_url="opc.tcp://opcua.demo-this.com:51210/UA/SampleServer",
    security_policy="Basic256Sha256",
    message_security_mode="SignAndEncrypt",
    certificate_path="/path/to/client_cert.pem",
    private_key_path="/path/to/client_key.pem",
)


async def main():
    policies = await oc.get_security_policies()
    for policy in policies:
        print(policy)


asyncio.run(main())

#-------------------------------------------------------------------------------------------------
# Expected output
#
# http://opcfoundation.org/UA/SecurityPolicy#Basic256Sha256
# http://opcfoundation.org/UA/SecurityPolicy#Basic256Sha256
# http://opcfoundation.org/UA/SecurityPolicy#Basic256Sha256
# http://opcfoundation.org/UA/SecurityPolicy#Aes128_Sha256_RsaOaep
# http://opcfoundation.org/UA/SecurityPolicy#Aes256_Sha256_RsaPss
# http://opcfoundation.org/UA/SecurityPolicy#Aes128_Sha256_RsaOaep
# http://opcfoundation.org/UA/SecurityPolicy#Aes256_Sha256_RsaPss
#
#-------------------------------------------------------------------------------------------------
