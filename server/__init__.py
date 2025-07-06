import asyncio
import logging

from asyncua import Server, ua
from asyncua.common.methods import uamethod


SERVER_ENDPOINT = "opc.tcp://0.0.0.0:4840/freeopcua/server/"


@uamethod
def func(parent, value):
    return value * 2


async def main():
    _logger = logging.getLogger(__name__)
    # ---------------------
    # Setup OPC UA server
    # ----------------------
    server = Server()
    await server.init()
    server.set_endpoint(SERVER_ENDPOINT)

    # -------------------------------------------------------------------
    # set up our own namespace, not really necessary but should as spec
    # -------------------------------------------------------------------
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    # ----------------------------------------------------------------------------
    # Populate Address Space
    # server.nodes, contains links to very common nodes like [Objects] and [Root]
    # ----------------------------------------------------------------------------
    myobj = await server.nodes.objects.add_object(idx, "MyObject")
    myvar = await myobj.add_variable(idx, "MyVariable", 6.7)

    # --------------------------------------------
    # Set [MyVariable] to be writable by clients
    # ---------------------------------------------
    await myvar.set_writable()
    await server.nodes.objects.add_method(
        ua.NodeId("ServerMethod", idx),
        ua.QualifiedName("ServerMethod", idx),
        func,
        [ua.VariantType.Int64],
        [ua.VariantType.Int64],
    )
    _logger.info("Starting server...")
    async with server:
        while True:
            await asyncio.sleep(1)
            new_val = await myvar.get_value() + 0.1
            _logger.info("Set value of %s to %.1f", myvar, new_val)
            await myvar.write_value(new_val)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main(), debug=True)
