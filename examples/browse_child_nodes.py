import asyncio
from databricks_industrial_automation_suite.integrations.opcua import OPCUAClient


oc = OPCUAClient(
    server_url="opc.tcp://opcua.demo-this.com:51210/UA/SampleServer",
    security_policy="Basic256Sha256",
    message_security_mode="SignAndEncrypt",
    certificate_path="/tmp/certs/client_cert.pem",
    private_key_path="/tmp/certs/client_key.pem",
)


async def main():
    await oc.connect()
    nodes = await oc.browse_children("ns=4;i=1241")
    print(nodes)


asyncio.run(main())
