import asyncio
from databricks_industrial_automation_suite.integrations.opcua import OPCUAClient

# ----------------------------------------------------------------------
# Working with Authentication
# -----------------------------------------------------------------------

# oc = OPCUAClient(
#     server_url="opc.tcp://opcua.demo-this.com:51210/UA/SampleServer",
#     security_policy="Basic256Sha256",
#     message_security_mode="SignAndEncrypt",
#     certificate_path="/tmp/certs/client_cert.pem",
#     private_key_path="/tmp/certs/client_key.pem",
# )

oc = OPCUAClient(server_url="opc.tcp://localhost:4840/freeopcua/server/")


TARGET_NODE_ID = "ns=2;i=2"  # Replace with the correct node from your server


async def main():
    await oc.connect()
    await oc.subscribe_to_node(TARGET_NODE_ID)

    async for event in oc.stream():
        print(event.strip())  # strip to remove \n\n
        # Optionally: break after N updates or add timeout


asyncio.run(main())
