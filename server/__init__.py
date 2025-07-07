import asyncio
import logging
import random
from asyncua import Server, ua
from asyncua.common.methods import uamethod

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

SERVER_ENDPOINT = "opc.tcp://0.0.0.0:4840/freeopcua/server/"


@uamethod
def multiply(parent, value):
    return value * 2


async def main():
    server = Server()
    await server.init()
    server.set_endpoint(SERVER_ENDPOINT)

    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    # ---------------------------
    # Root object
    # ---------------------------
    plant = await server.nodes.objects.add_object(idx, "IndustrialPlant")

    # -----------------------------------
    # Simulate multiple subsystems
    # -----------------------------------
    boiler = await plant.add_object(idx, "BoilerSystem")
    pump = await plant.add_object(idx, "PumpSystem")
    tank = await plant.add_object(idx, "TankSystem")

    # -----------------------------------
    # BoilerSystem variables
    # -----------------------------------
    boiler_temp = await boiler.add_variable(idx, "Temperature", 100.0)
    boiler_pressure = await boiler.add_variable(idx, "Pressure", 15.0)

    # -----------------------------------
    # PumpSystem variables
    # -----------------------------------
    pump_rpm = await pump.add_variable(idx, "RPM", 1200)
    pump_flow = await pump.add_variable(idx, "FlowRate", 75.0)

    # -----------------------------------
    # TankSystem variables
    # -----------------------------------
    tank_level = await tank.add_variable(idx, "Level", 55.0)
    tank_ph = await tank.add_variable(idx, "pH", 7.0)

    # -----------------------------------
    # Set all variables to be writable
    # -----------------------------------
    for var in [boiler_temp, boiler_pressure, pump_rpm, pump_flow, tank_level, tank_ph]:
        await var.set_writable()

    # -----------------------------------
    # Add a demo method
    # -----------------------------------
    await plant.add_method(
        ua.NodeId("ServerMethod", idx),
        ua.QualifiedName("Multiply", idx),
        multiply,
        [ua.VariantType.Int64],
        [ua.VariantType.Int64],
    )

    _logger.info("Starting industrial OPC UA simulation server...")
    async with server:
        while True:
            # -------------------------------------------
            # Update each variable independently
            # -------------------------------------------
            await boiler_temp.write_value(
                await boiler_temp.get_value() + random.uniform(-0.5, 0.5)
            )
            await boiler_pressure.write_value(
                await boiler_pressure.get_value() + random.uniform(-0.1, 0.1)
            )

            await pump_rpm.write_value(
                await pump_rpm.get_value() + random.randint(-50, 50)
            )
            await pump_flow.write_value(
                await pump_flow.get_value() + random.uniform(-1.0, 1.0)
            )

            await tank_level.write_value(
                await tank_level.get_value() + random.uniform(-0.2, 0.2)
            )
            await tank_ph.write_value(
                max(
                    0.0,
                    min(14.0, await tank_ph.get_value() + random.uniform(-0.05, 0.05)),
                )
            )

            _logger.info("Updated plant variables...")
            await asyncio.sleep(1)  # Loop every second


if __name__ == "__main__":
    asyncio.run(main(), debug=True)
