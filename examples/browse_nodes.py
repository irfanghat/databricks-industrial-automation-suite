import asyncio
from databricks_industrial_automation_suite.integrations.opcua import OPCUAClient

# ----------------------------------------------------------------------
# Working with Authentication
#-----------------------------------------------------------------------

# oc = OPCUAClient(
#     server_url="opc.tcp://opcua.demo-this.com:51210/UA/SampleServer",
#     security_policy="Basic256Sha256",
#     message_security_mode="SignAndEncrypt",
#     certificate_path="/tmp/certs/client_cert.pem",
#     private_key_path="/tmp/certs/client_key.pem",
# )

oc = OPCUAClient(server_url="opc.tcp://localhost:4840/freeopcua/server/")


async def main():
    await oc.connect()
    nodes = await oc.browse_all()
    print(nodes)


asyncio.run(main())

# ------------------------------------------------------------------------------------------------
# Expected output
#
# [{'id': 'i=87', 'browse_name': "QualifiedName(NamespaceIndex=0, Name='Views')", 'children': []}, # {'id': 'i=85', 'browse_name': "QualifiedName(NamespaceIndex=0, Name='Objects')", 'children':
# [{'error': ''}, {'error': ''}, {'id': 'ns=4;i=1240', 'browse_name': "QualifiedName
# (NamespaceIndex=4, Name='Boilers')", 'children': [{'id': 'ns=4;i=1241', 'browse_name':
# "QualifiedName(NamespaceIndex=4, Name='Boiler #1')", 'children': [{'id': 'ns=4;i=1242',
# 'browse_name': "QualifiedName(NamespaceIndex=4, Name='PipeX001')", 'children': [{'id': 'ns=4;
# i=1243', 'browse_name': "QualifiedName(NamespaceIndex=4, Name='FTX001')", 'children': [{'id':
# 'ns=4;i=1244', 'browse_name': "QualifiedName(NamespaceIndex=4, Name='Output')", 'children':
# [{'id': 'ns=4;i=1247', 'browse_name': "QualifiedName(NamespaceIndex=0, Name='EURange')",
# 'children': []}]}]}, {'id': 'ns=4;i=1250', 'browse_name': "QualifiedNam....]
#
# ------------------------------------------------------------------------------------------------
