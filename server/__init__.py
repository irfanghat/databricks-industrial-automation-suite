"""

-----------------------------------------------------------------
Simple Industrial Manufacturing Plant OPC UA Server Simulation
-----------------------------------------------------------------

Simulates a beverage/chemical production facility with realistic scenarios:
- Production line monitoring
- Equipment health tracking
- Energy consumption
- Quality control
- Predictive maintenance indicators

Perfect for Databricks hackathon demos!

"""

import asyncio
import random
import time
from asyncua import Server, ua
from asyncua.common.methods import uamethod
from utils.logger import _logger


SERVER_ENDPOINT = "opc.tcp://0.0.0.0:4840/freeopcua/server/"


@uamethod
def emergency_stop(parent):
    """Emergency stop - callable from client"""
    _logger.warning("EMERGENCY STOP ACTIVATED!")
    return True


@uamethod
def start_line(parent, line_id: int):
    """Start production line"""
    _logger.info(f"Starting Line {line_id}")
    return True


async def main():
    # -----------------------------
    # Initialize server
    # -----------------------------
    server = Server()
    await server.init()
    server.set_endpoint(SERVER_ENDPOINT)
    server.set_server_name("Manufacturing Plant Demo")

    uri = "http://industrial.databricks.demo"
    idx = await server.register_namespace(uri)

    # -----------------------------
    # Root object
    # -----------------------------
    plant = await server.nodes.objects.add_object(idx, "ManufacturingPlant")

    # -------------------------------------------------------------------------
    # PRODUCTION LINE 1 (Main Production)
    # -------------------------------------------------------------------------
    line1 = await plant.add_object(idx, "ProductionLine1")
    
    # -----------------------------
    # Production metrics
    # -----------------------------
    l1_status = await line1.add_variable(idx, "Status", "Running")
    l1_rate = await line1.add_variable(idx, "ProductionRate", 85.0)  # units/hour
    l1_target = await line1.add_variable(idx, "TargetRate", 100.0)
    l1_efficiency = await line1.add_variable(idx, "Efficiency", 85.0)  # %
    l1_total = await line1.add_variable(idx, "TotalProduced", 0.0)
    l1_downtime = await line1.add_variable(idx, "DowntimeMinutes", 0.0)
    
    # -----------------------------
    # Equipment on Line 1
    # -----------------------------
    l1_motor_temp = await line1.add_variable(idx, "MotorTemperature", 65.0)  # °C
    l1_motor_vibration = await line1.add_variable(idx, "MotorVibration", 2.5)  # mm/s
    l1_motor_current = await line1.add_variable(idx, "MotorCurrent", 45.0)  # Amps
    l1_speed = await line1.add_variable(idx, "LineSpeed", 15.0)  # m/min
    
    # -------------------------------------------------------------------------
    # PRODUCTION LINE 2 (Secondary Production)
    # -------------------------------------------------------------------------
    line2 = await plant.add_object(idx, "ProductionLine2")
    
    l2_status = await line2.add_variable(idx, "Status", "Running")
    l2_rate = await line2.add_variable(idx, "ProductionRate", 78.0)
    l2_target = await line2.add_variable(idx, "TargetRate", 100.0)
    l2_efficiency = await line2.add_variable(idx, "Efficiency", 78.0)
    l2_total = await line2.add_variable(idx, "TotalProduced", 0.0)
    l2_downtime = await line2.add_variable(idx, "DowntimeMinutes", 0.0)
    
    l2_motor_temp = await line2.add_variable(idx, "MotorTemperature", 68.0)
    l2_motor_vibration = await line2.add_variable(idx, "MotorVibration", 3.2)
    l2_motor_current = await line2.add_variable(idx, "MotorCurrent", 48.0)
    l2_speed = await line2.add_variable(idx, "LineSpeed", 14.0)
    
    # -------------------------------------------------------------------------
    # MIXING SYSTEM
    # -------------------------------------------------------------------------
    mixer = await plant.add_object(idx, "MixingSystem")
    
    mix_tank_level = await mixer.add_variable(idx, "TankLevel", 65.0)  # %
    mix_tank_temp = await mixer.add_variable(idx, "TankTemperature", 45.0)  # °C
    mix_ph = await mixer.add_variable(idx, "pH", 7.2)
    mix_viscosity = await mixer.add_variable(idx, "Viscosity", 120.0)  # cP
    mix_agitator_rpm = await mixer.add_variable(idx, "AgitatorRPM", 150.0)
    mix_agitator_power = await mixer.add_variable(idx, "AgitatorPower", 12.0)  # kW
    
    # -------------------------------------------------------------------------
    # PUMP SYSTEM
    # -------------------------------------------------------------------------
    pumps = await plant.add_object(idx, "PumpSystem")
    
    # -----------------------------
    # Pump 1 - Feed Pump
    # -----------------------------
    pump1 = await pumps.add_object(idx, "Pump1")
    p1_flow = await pump1.add_variable(idx, "FlowRate", 250.0)  # L/min
    p1_pressure = await pump1.add_variable(idx, "DischargePressure", 5.5)  # bar
    p1_rpm = await pump1.add_variable(idx, "RPM", 1450.0)
    p1_power = await pump1.add_variable(idx, "PowerConsumption", 18.0)  # kW
    p1_temp = await pump1.add_variable(idx, "Temperature", 55.0)  # °C
    p1_vibration = await pump1.add_variable(idx, "Vibration", 2.8)  # mm/s
    
    # -----------------------------
    # Pump 2 - Transfer Pump
    # -----------------------------
    pump2 = await pumps.add_object(idx, "Pump2")
    p2_flow = await pump2.add_variable(idx, "FlowRate", 180.0)
    p2_pressure = await pump2.add_variable(idx, "DischargePressure", 4.2)
    p2_rpm = await pump2.add_variable(idx, "RPM", 1200.0)
    p2_power = await pump2.add_variable(idx, "PowerConsumption", 12.0)
    p2_temp = await pump2.add_variable(idx, "Temperature", 52.0)
    p2_vibration = await pump2.add_variable(idx, "Vibration", 2.1)
    
    # -------------------------------------------------------------------------
    # COMPRESSOR (for packaging)
    # -------------------------------------------------------------------------
    compressor = await plant.add_object(idx, "Compressor")
    
    comp_pressure = await compressor.add_variable(idx, "DischargePressure", 7.0)  # bar
    comp_temp = await compressor.add_variable(idx, "Temperature", 75.0)  # °C
    comp_power = await compressor.add_variable(idx, "PowerConsumption", 35.0)  # kW
    comp_runtime = await compressor.add_variable(idx, "RuntimeHours", 0.0)
    
    # -------------------------------------------------------------------------
    # QUALITY CONTROL
    # -------------------------------------------------------------------------
    quality = await plant.add_object(idx, "QualityControl")
    
    qc_pass_rate = await quality.add_variable(idx, "PassRate", 98.5)  # %
    qc_samples = await quality.add_variable(idx, "SamplesTested", 0.0)
    qc_defects = await quality.add_variable(idx, "DefectsFound", 0.0)
    qc_last_batch = await quality.add_variable(idx, "LastBatchQuality", 99.2)  # %
    
    # -------------------------------------------------------------------------
    # ENERGY MANAGEMENT
    # -------------------------------------------------------------------------
    energy = await plant.add_object(idx, "Energy")
    
    total_power = await energy.add_variable(idx, "TotalPowerConsumption", 185.0)  # kW
    power_factor = await energy.add_variable(idx, "PowerFactor", 0.92)
    energy_today = await energy.add_variable(idx, "EnergyTodayKWh", 0.0)
    energy_cost = await energy.add_variable(idx, "CostTodayUSD", 0.0)
    peak_demand = await energy.add_variable(idx, "PeakDemandKW", 185.0)
    
    # -------------------------------------------------------------------------
    # ENVIRONMENTAL
    # -------------------------------------------------------------------------
    env = await plant.add_object(idx, "Environmental")
    
    ambient_temp = await env.add_variable(idx, "AmbientTemperature", 25.0)  # °C
    humidity = await env.add_variable(idx, "Humidity", 60.0)  # %
    
    # -------------------------------------------------------------------------
    # MAINTENANCE INDICATORS
    # -------------------------------------------------------------------------
    maintenance = await plant.add_object(idx, "Maintenance")
    
    # ---------------------------------------------
    # Health scores (0-100, degrading over time)
    # ---------------------------------------------
    m_line1_health = await maintenance.add_variable(idx, "Line1HealthScore", 95.0)
    m_line2_health = await maintenance.add_variable(idx, "Line2HealthScore", 88.0)
    m_pump1_health = await maintenance.add_variable(idx, "Pump1HealthScore", 92.0)
    m_pump2_health = await maintenance.add_variable(idx, "Pump2HealthScore", 85.0)
    
    # ---------------------------------------------
    # Runtime hours (for predictive maintenance)
    # ---------------------------------------------
    m_line1_hours = await maintenance.add_variable(idx, "Line1RuntimeHours", 0.0)
    m_line2_hours = await maintenance.add_variable(idx, "Line2RuntimeHours", 0.0)
    
    # -------------------------------------------------------------------------
    # ALARMS
    # -------------------------------------------------------------------------
    alarms = await plant.add_object(idx, "Alarms")
    
    alarm_count = await alarms.add_variable(idx, "ActiveAlarms", 0.0)
    alarm_last = await alarms.add_variable(idx, "LastAlarmMessage", "No alarms")
    
    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------
    await plant.add_method(
        ua.NodeId("EmergencyStop", idx),
        ua.QualifiedName("EmergencyStop", idx),
        emergency_stop,
        [],
        [ua.VariantType.Boolean],
    )
    
    await plant.add_method(
        ua.NodeId("StartLine", idx),
        ua.QualifiedName("StartLine", idx),
        start_line,
        [ua.VariantType.Int32],
        [ua.VariantType.Boolean],
    )

    _logger.info("•" * 80)
    _logger.info("Manufacturing Plant OPC UA Server")
    _logger.info(f"Endpoint: {SERVER_ENDPOINT}")
    _logger.info("•" * 80)
    _logger.info("Systems Online:")
    _logger.info("   • 2 Production Lines")
    _logger.info("   • Mixing System")
    _logger.info("   • 2 Pumps")
    _logger.info("   • Compressor")
    _logger.info("   • Quality Control")
    _logger.info("   • Energy Management")
    _logger.info("   • Predictive Maintenance")
    _logger.info("•" * 80)

    start_time = time.time()
    iteration = 0
    
    # ----------------------------------------------
    # Simulate gradual equipment degradation
    # ----------------------------------------------
    wear_line1 = 0.002  # health degradation per hour
    wear_line2 = 0.003  # Line 2 degrades faster (needs maintenance)
    wear_pump1 = 0.0015
    wear_pump2 = 0.004  # Pump 2 has issues (predictive maintenance)
    
    async with server:
        while True:
            iteration += 1
            runtime_hours = (time.time() - start_time) / 3600.0
            
            # -----------------------------------------
            # REALISTIC SCENARIOS
            # -----------------------------------------
            
            # ---------------------------------------------------------------------------
            # Scenario 1: Line 2 motor starts overheating (predictive maintenance)
            # ---------------------------------------------------------------------------
            if iteration > 100:
                l2_motor_temp_base = 68.0 + (iteration - 100) * 0.05  # Gradual increase
                l2_motor_vibration_base = 3.2 + (iteration - 100) * 0.01
            else:
                l2_motor_temp_base = 68.0
                l2_motor_vibration_base = 3.2
            
            # ---------------------------------------------------------------------------
            # Scenario 2: Pump 2 showing early failure signs
            # ---------------------------------------------------------------------------
            if iteration > 150:
                p2_vibration_base = 2.1 + (iteration - 150) * 0.008  # Rising vibration
                p2_temp_base = 52.0 + (iteration - 150) * 0.04
            else:
                p2_vibration_base = 2.1
                p2_temp_base = 52.0
            
            # ---------------------------------------------------------------------------
            # Scenario 3: Quality correlates with mixing parameters
            # ---------------------------------------------------------------------------
            optimal_ph = 7.2
            optimal_temp = 45.0
            current_ph = await mix_ph.get_value()
            current_mix_temp = await mix_tank_temp.get_value()
            
            ph_deviation = abs(current_ph - optimal_ph)
            temp_deviation = abs(current_mix_temp - optimal_temp) / 10.0
            quality_impact = 100 - (ph_deviation * 5 + temp_deviation * 2)
            
            # ------------------------------------------------------------------------
            # UPDATE LINE 1 (Normal operation)
            # ------------------------------------------------------------------------
            await l1_status.write_value("Running")
            
            rate1 = await l1_rate.get_value()
            await l1_rate.write_value(max(70.0, min(95.0, rate1 + random.uniform(-3, 3))))
            
            eff1 = (await l1_rate.get_value() / 100.0) * 100.0
            await l1_efficiency.write_value(eff1)
            
            await l1_total.write_value(await l1_total.get_value() + (await l1_rate.get_value() / 3600.0))
            
            await l1_motor_temp.write_value(max(55.0, min(85.0, 65.0 + random.uniform(-3, 3))))
            await l1_motor_vibration.write_value(max(0.5, min(5.0, 2.5 + random.uniform(-0.3, 0.3))))
            await l1_motor_current.write_value(max(35.0, min(55.0, 45.0 + random.uniform(-3, 3))))
            await l1_speed.write_value(max(12.0, min(18.0, 15.0 + random.uniform(-0.5, 0.5))))
            
            # ------------------------------------------------------------------------
            # UPDATE LINE 2 (Degrading - needs maintenance)
            # ------------------------------------------------------------------------
            await l2_status.write_value("Running")
            
            rate2 = await l2_rate.get_value()
            await l2_rate.write_value(max(65.0, min(90.0, rate2 + random.uniform(-3, 3))))
            
            eff2 = (await l2_rate.get_value() / 100.0) * 100.0
            await l2_efficiency.write_value(eff2)
            
            await l2_total.write_value(await l2_total.get_value() + (await l2_rate.get_value() / 3600.0))
            
            # --------------------------------------------------------------
            # Line 2 showing problems - temperature rising
            # --------------------------------------------------------------
            await l2_motor_temp.write_value(max(65.0, min(95.0, l2_motor_temp_base + random.uniform(-2, 4))))
            await l2_motor_vibration.write_value(max(2.0, min(8.0, l2_motor_vibration_base + random.uniform(-0.2, 0.5))))
            await l2_motor_current.write_value(max(40.0, min(60.0, 48.0 + random.uniform(-3, 3))))
            await l2_speed.write_value(max(10.0, min(16.0, 14.0 + random.uniform(-0.5, 0.5))))
            
            # ------------------------------------------------------------------------
            # UPDATE MIXING SYSTEM
            # ------------------------------------------------------------------------
            level = await mix_tank_level.get_value()
            await mix_tank_level.write_value(max(40.0, min(85.0, level + random.uniform(-2, 2))))
            
            temp = await mix_tank_temp.get_value()
            await mix_tank_temp.write_value(max(40.0, min(55.0, temp + random.uniform(-1, 1))))
            
            ph = await mix_ph.get_value()
            await mix_ph.write_value(max(6.5, min(8.0, ph + random.uniform(-0.05, 0.05))))
            
            visc = await mix_viscosity.get_value()
            await mix_viscosity.write_value(max(100.0, min(150.0, visc + random.uniform(-3, 3))))
            
            agit_rpm = await mix_agitator_rpm.get_value()
            await mix_agitator_rpm.write_value(max(120.0, min(180.0, agit_rpm + random.uniform(-5, 5))))
            
            agit_power = (await mix_agitator_rpm.get_value() / 150.0) * 12.0
            await mix_agitator_power.write_value(max(8.0, min(18.0, agit_power + random.uniform(-1, 1))))
            
            # ------------------------------------------------------------------------
            # UPDATE PUMP 1 (Normal)
            # ------------------------------------------------------------------------
            await p1_flow.write_value(max(200.0, min(300.0, 250.0 + random.uniform(-15, 15))))
            await p1_pressure.write_value(max(4.0, min(7.0, 5.5 + random.uniform(-0.3, 0.3))))
            await p1_rpm.write_value(max(1300.0, min(1600.0, 1450.0 + random.uniform(-30, 30))))
            await p1_power.write_value(max(12.0, min(22.0, 18.0 + random.uniform(-2, 2))))
            await p1_temp.write_value(max(45.0, min(70.0, 55.0 + random.uniform(-3, 3))))
            await p1_vibration.write_value(max(1.5, min(5.0, 2.8 + random.uniform(-0.3, 0.3))))
            
            # ------------------------------------------------------------------------
            # UPDATE PUMP 2 (Degrading - Predictive Maintenance)
            # ------------------------------------------------------------------------
            await p2_flow.write_value(max(150.0, min(220.0, 180.0 + random.uniform(-15, 15))))
            await p2_pressure.write_value(max(3.0, min(6.0, 4.2 + random.uniform(-0.3, 0.3))))
            await p2_rpm.write_value(max(1000.0, min(1400.0, 1200.0 + random.uniform(-30, 30))))
            await p2_power.write_value(max(8.0, min(16.0, 12.0 + random.uniform(-2, 2))))
            
            # ------------------------------------------------------------------------
            # Pump 2 problems - temperature and vibration rising
            # ------------------------------------------------------------------------
            await p2_temp.write_value(max(45.0, min(85.0, p2_temp_base + random.uniform(-2, 4))))
            await p2_vibration.write_value(max(1.5, min(10.0, p2_vibration_base + random.uniform(-0.2, 0.6))))
            
            # ------------------------------------------------------------------------
            # UPDATE COMPRESSOR
            # ------------------------------------------------------------------------
            await comp_pressure.write_value(max(6.0, min(8.0, 7.0 + random.uniform(-0.3, 0.3))))
            await comp_temp.write_value(max(65.0, min(90.0, 75.0 + random.uniform(-3, 3))))
            await comp_power.write_value(max(25.0, min(45.0, 35.0 + random.uniform(-3, 3))))
            await comp_runtime.write_value(runtime_hours)
            
            # ------------------------------------------------------------------------
            # UPDATE QUALITY (affected by mixing parameters)
            # ------------------------------------------------------------------------
            pass_rate = max(92.0, min(99.9, quality_impact + random.uniform(-0.5, 0.5)))
            await qc_pass_rate.write_value(pass_rate)
            
            await qc_samples.write_value(await qc_samples.get_value() + random.uniform(1, 3))
            
            if pass_rate < 97:
                await qc_defects.write_value(await qc_defects.get_value() + 1.0)
            
            await qc_last_batch.write_value(max(92.0, min(100.0, pass_rate + random.uniform(-1, 1))))
            
            # ------------------------------------------------------------------------
            # UPDATE ENERGY
            # ------------------------------------------------------------------------
            line1_power = (await l1_rate.get_value() / 100.0) * 45.0
            line2_power = (await l2_rate.get_value() / 100.0) * 45.0
            pump_power = (await p1_power.get_value()) + (await p2_power.get_value())
            comp_power_val = await comp_power.get_value()
            mix_power = await mix_agitator_power.get_value()
            
            total = line1_power + line2_power + pump_power + comp_power_val + mix_power
            await total_power.write_value(max(100.0, min(300.0, total + random.uniform(-10, 10))))
            
            await power_factor.write_value(max(0.85, min(0.95, 0.92 + random.uniform(-0.02, 0.02))))
            
            current_power = await total_power.get_value()
            await energy_today.write_value(await energy_today.get_value() + (current_power / 3600.0))
            await energy_cost.write_value((await energy_today.get_value()) * 0.12)  # $0.12/kWh
            
            peak = await peak_demand.get_value()
            if current_power > peak:
                await peak_demand.write_value(current_power)
            
            # ------------------------------------------------------------------------
            # UPDATE ENVIRONMENTAL
            # ------------------------------------------------------------------------
            amb = await ambient_temp.get_value()
            await ambient_temp.write_value(max(20.0, min(30.0, amb + random.uniform(-0.5, 0.5))))
            
            hum = await humidity.get_value()
            await humidity.write_value(max(40.0, min(80.0, hum + random.uniform(-2, 2))))
            
            # ------------------------------------------------------------------------
            # UPDATE MAINTENANCE (Health Degradation)
            # ------------------------------------------------------------------------
            await m_line1_health.write_value(max(70.0, 100.0 - (runtime_hours * wear_line1)))
            await m_line2_health.write_value(max(60.0, 100.0 - (runtime_hours * wear_line2)))  # Degrades faster
            await m_pump1_health.write_value(max(70.0, 100.0 - (runtime_hours * wear_pump1)))
            await m_pump2_health.write_value(max(50.0, 100.0 - (runtime_hours * wear_pump2)))  # Degrades fastest
            
            await m_line1_hours.write_value(runtime_hours)
            await m_line2_hours.write_value(runtime_hours)
            
            # ------------------------------------------------------------------------
            # UPDATE ALARMS
            # ------------------------------------------------------------------------
            alarms_active = 0.0
            alarm_messages = []
            
            if await l2_motor_temp.get_value() > 85:
                alarms_active += 1.0
                alarm_messages.append("Line 2 motor temperature HIGH")
            
            if await l2_motor_vibration.get_value() > 6:
                alarms_active += 1.0
                alarm_messages.append("Line 2 motor vibration HIGH")
            
            if await p2_vibration.get_value() > 6:
                alarms_active += 1.0
                alarm_messages.append("Pump 2 vibration HIGH - maintenance needed")
            
            if await p2_temp.get_value() > 75:
                alarms_active += 1.0
                alarm_messages.append("Pump 2 temperature HIGH")
            
            if pass_rate < 96:
                alarms_active += 1.0
                alarm_messages.append("Quality below target")
            
            if await m_line2_health.get_value() < 75:
                alarms_active += 1.0
                alarm_messages.append("Line 2 health LOW - schedule maintenance")
            
            if await m_pump2_health.get_value() < 70:
                alarms_active += 1.0
                alarm_messages.append("Pump 2 health CRITICAL - maintenance urgent")
            
            await alarm_count.write_value(alarms_active)
            
            if alarm_messages:
                await alarm_last.write_value("; ".join(alarm_messages))
            else:
                await alarm_last.write_value("No alarms")
            
            # ------------------------------------------------------------------------
            # LOGGING
            # ------------------------------------------------------------------------
            if iteration % 10 == 0:
                _logger.info(
                    f"Iter {iteration:4d} | "
                    f"L1: {await l1_rate.get_value():5.1f} u/h | "
                    f"L2: {await l2_rate.get_value():5.1f} u/h | "
                    f"Quality: {pass_rate:5.1f}% | "
                    f"Power: {current_power:6.1f} kW | "
                    f"Alarms: {int(alarms_active)}"
                )
                
                if alarms_active > 0:
                    _logger.warning(f"{await alarm_last.get_value()}")
            
            await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(main(), debug=False)
    except KeyboardInterrupt:
        _logger.info("•" * 50)
        _logger.info("Server stopped")
        _logger.info("•" * 50)
    except Exception as e:
        _logger.error(f"Server error: {e}", exc_info=True)