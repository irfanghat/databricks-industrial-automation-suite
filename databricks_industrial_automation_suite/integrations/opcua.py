import asyncio
from typing import Optional, List, Dict, AsyncGenerator
from datetime import datetime, timezone

from asyncua import Client
from databricks_industrial_automation_suite.utils.logger import _logger


class OPCUAClient:
    def __init__(
        self,
        server_url: str,
        security_policy: str = "None",
        message_security_mode: str = "None",
        certificate_path: Optional[str] = None,
        private_key_path: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.server_url = server_url
        self.security_policy = security_policy
        self.message_security_mode = message_security_mode
        self.certificate_path = certificate_path
        self.private_key_path = private_key_path
        self.username = username
        self.password = password
        self.node_metadata: Dict[str, str] = {}  # node_id → browse_name

        self.client = Client(url=self.server_url)
        self.subscription = None
        self.subscribed_nodes = set()
        self.queue: asyncio.Queue[Dict] = asyncio.Queue()


    async def connect(self) -> None:
        if self.security_policy != "None":
            security_string = f"{self.security_policy},{self.message_security_mode}"
            if self.certificate_path and self.private_key_path:
                security_string += f",{self.certificate_path},{self.private_key_path}"
            await self.client.set_security_string(security_string)

        if self.username and self.password:
            self.client.set_user(self.username)
            self.client.set_password(self.password)

        await self.client.connect()
        _logger.info(f"Connected to OPC UA server: {self.server_url}")


    async def disconnect(self) -> None:
        if self.subscription:
            await self.subscription.delete()
        await self.client.disconnect()
        _logger.info("Disconnected from OPC UA server")


    async def subscribe_to_node(self, node_id: str) -> None:
        node = self.client.get_node(node_id)
        browse_name = str(await node.read_browse_name())

        if not self.subscription:
            handler = self._SubHandler(self)
            self.subscription = await self.client.create_subscription(1000, handler)

        await self.subscription.subscribe_data_change(node)
        self.subscribed_nodes.add(node_id)
        self.node_metadata[node_id] = browse_name

        _logger.info(f"Subscribed to node: {node_id} ({browse_name})")


    async def stream(self) -> AsyncGenerator[Dict, None]:
        while True:
            update = await self.queue.get()
            yield update


    async def browse_all(self) -> List[Dict]:
        root = self.client.nodes.root
        children = await root.get_children()
        return [await self._browse_node_recursive(node) for node in children]


    async def browse_children(self, node_id: str) -> List[Dict]:
        node = self.client.get_node(node_id)
        children = await node.get_children()
        return [
            {
                "id": child.nodeid.to_string(),
                "browse_name": str(await child.read_browse_name()),
            }
            for child in children
        ]


    async def get_security_policies(self) -> List[str]:
        await self.connect()
        endpoints = await self.client.get_endpoints()
        await self.disconnect()
        return [ep.SecurityPolicyUri for ep in endpoints]


    async def _browse_node_recursive(self, node) -> Dict:
        try:
            children = await node.get_children()
            return {
                "id": node.nodeid.to_string(),
                "browse_name": str(await node.read_browse_name()),
                "children": [
                    await self._browse_node_recursive(child) for child in children
                ],
            }
        except Exception as e:
            return {"error": str(e)}


    class _SubHandler:
        def __init__(self, outer: "OPCUAClient"):
            self.outer = outer


        def datachange_notification(self, node, val, data):
            node_id = node.nodeid.to_string()
            browse_name = self.outer.node_metadata.get(node_id, "UNKNOWN NODE ID")
            event = {
                "node_id": node_id,
                "browse_name": browse_name,
                "value": val,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            self.outer.queue.put_nowait(event)


"""
# OPC UA Security Policies:
- None: No security (no encryption or signing).
- Basic128Rsa15: Uses RSA-1024 and AES-128 for encryption. (Deprecated)
- Basic256: Uses RSA-2048 and AES-256 for encryption.
- Basic256Sha256: Uses RSA-2048 and SHA-256 for stronger security.
- Aes128_Sha256_RsaOaep: Uses AES-128 and SHA-256 with RSA-OAEP encryption.
- Aes256_Sha256_RsaPss: Uses AES-256 and SHA-256 with RSA-PSS encryption.

# OPC UA Message Security Modes:
- None: No security (plain communication).
- Sign: Signs messages to ensure integrity but does not encrypt.
- SignAndEncrypt: Signs and encrypts messages for full security.
"""
