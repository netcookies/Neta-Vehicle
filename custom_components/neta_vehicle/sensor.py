import logging
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.components.device_tracker import TrackerEntity
from datetime import datetime, timedelta, date
from typing import Optional, Tuple
from homeassistant.components.zone import in_zone
from .update_coordinator import UpdateCoordinator
from .const import (
    DOMAIN,
    CONF_VIN,
    CONF_NAME,
)

PERCENTAGE_SCALE = 10000  # 百分比转换因子 (0.01%)
VOLTAGE_SCALE = 1000     # 电压转换因子 (mV to V)
CURRENT_SCALE = 1000     # 电流转换因子 (mA to A)
DISTANCE_SCALE = 10      # 距离转换因子 (0.1km to km)
POWER_SCALE = 1000       # 功率转换因子 (W to kW)
SPEED_SCALE = 10        # 速度转换因子 (0.1km/h to km/h)
COORDINATE_SCALE = 1e6   # 坐标转换因子 (1e-6 to degrees)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """设置传感器平台。"""
    _LOGGER.debug("Setting up sensors for Neta Vehicle Status...")
    name = config_entry.data.get(CONF_NAME)
    vin = config_entry.data.get(CONF_VIN)

    coordinator: UpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    # 定义传感器实体
    sensors = [
        BatteryLevelSensor(coordinator, f"{name} Battery Level", vin),
        ChargingStatusSensor(coordinator, name, vin),
        MileageSensor(coordinator, f"{name} Mileage", vin),
        LocationSensor(coordinator, f"{name} Location", vin, hass),
    ]
    sensors = [
        CarStatusSensor(coordinator, name, vin),
        BatteryLevelSensor(coordinator, f"{name} Battery Level", vin),
        FuelLevelSensor(coordinator, f"{name} Fuel Level", vin),  # 添加油量传感器
        ChargingStatusSensor(coordinator, f"{name} Charging Status", vin),
        MileageSensor(coordinator, f"{name} Mileage", vin),
        LocationSensor(coordinator, f"{name} Location", vin, hass),
        EngineStatusSensor(coordinator, f"{name} Engine Status", vin),
        BatteryRange(coordinator, f"{name} Battery Range", vin),
        FuleRange(coordinator, f"{name} Fuel Range", vin),
        Speed(coordinator, f"{name} Speed", vin),
        RemainingEnergyKwh(coordinator, f"{name} Remaining Energy", vin),
        ChargingPowerKw(coordinator, f"{name} Charging Power", vin),
        DischargingPowerKw(coordinator, f"{name} Discharging Power", vin),
        TripEnergyConsumptionKwh(coordinator, f"{name} Trip Energy Consumption", vin),
        EnergyConsumptionPerKm(coordinator, f"{name} Energy Consumption Per Km", vin),
    ]

    async_add_entities(sensors)


class BaseSensor(SensorEntity):
    def __init__(self, coordinator: UpdateCoordinator, name: str, unique_id_base: str):
        self._coordinator = coordinator
        self._name = name
        self._unique_id = f"{unique_id_base}_{name.replace(' ', '_').lower()}"
        self._state = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def available(self) -> bool:
        return self._coordinator.data is not None

    @property
    def state(self):
        return self._state

    async def async_update(self):
        """从 UpdateCoordinator 更新传感器状态。"""
        _LOGGER.debug("Updating sensor: %s", self._name)
        data = self._coordinator.data
        if data:
            self.update_state(data)

    def update_state(self, data):
        """子类实现此方法以更新状态。"""
        raise NotImplementedError


class BatteryLevelSensor(BaseSensor):
    def update_state(self, data):
        """更新电池电量状态。"""
        soc = data.get("vehicleBasic", {}).get("soc")
        self._state = soc
        # 根据电量设置不同的电池图标
        if soc is not None:
            if soc <= 10:
                self._attr_icon = "mdi:battery-10"
            elif soc <= 20:
                self._attr_icon = "mdi:battery-20"
            elif soc <= 30:
                self._attr_icon = "mdi:battery-30"
            elif soc <= 40:
                self._attr_icon = "mdi:battery-40"
            elif soc <= 50:
                self._attr_icon = "mdi:battery-50"
            elif soc <= 60:
                self._attr_icon = "mdi:battery-60"
            elif soc <= 70:
                self._attr_icon = "mdi:battery-70"
            elif soc <= 80:
                self._attr_icon = "mdi:battery-80"
            elif soc <= 90:
                self._attr_icon = "mdi:battery-90"
            else:
                self._attr_icon = "mdi:battery"

    @property
    def device_class(self):
        return SensorDeviceClass.BATTERY

class FuelLevelSensor(BaseSensor):
    def update_state(self, data):
        """更新油量状态。"""
        fuel_level = data.get("enduranceStatus", {}).get("estimateFuelPercent")
        self._state = fuel_level
        if fuel_level is not None:
            if fuel_level <= 10:
                self._attr_icon = "mdi:battery-10"
            elif fuel_level <= 20:
                self._attr_icon = "mdi:battery-20"
            elif fuel_level <= 30:
                self._attr_icon = "mdi:battery-30"
            elif fuel_level <= 40:
                self._attr_icon = "mdi:battery-40"
            elif fuel_level <= 50:
                self._attr_icon = "mdi:battery-50"
            elif fuel_level <= 60:
                self._attr_icon = "mdi:battery-60"
            elif fuel_level <= 70:
                self._attr_icon = "mdi:battery-70"
            elif fuel_level <= 80:
                self._attr_icon = "mdi:battery-80"
            elif fuel_level <= 90:
                self._attr_icon = "mdi:battery-90"
            else:
                self._attr_icon = "mdi:battery"

    @property
    def device_class(self):
        return SensorDeviceClass.BATTERY

class CarStatusSensor(BaseSensor):
    def update_state(self, data):
        """更新车辆状态。"""
        vehicle_status = data.get("vehicleBasic", {}).get("vehicleStatus")
        charge_status = data.get("vehicleBasic", {}).get("chargeStatus")
        engine_status = data.get("vehicleExtend", {}).get("engineStatus")
        # 状态映射字典
        vehicle_status_map = {
            1: "Driving",
            2: "Parked",
            3: "Charging", # AI瞎猜的，没验证
            4: "Starting", # AI瞎猜的，没验证
            5: "PowerOff" # AI瞎猜的，没验证
        }
        
        charge_status_map = {
            1: "Charging",
            2: "ChargingComplete", # AI瞎猜的，没验证
            3: "NotCharging", # AI瞎猜的，没验证
            4: "Connected"
        }
        
        if charge_status in [1, 4]:
            self._state = charge_status_map.get(charge_status, "Unknown")
            self._attr_icon = "mdi:car-electric" if charge_status == 1 else "mdi:power-plug"
        else:
            self._state = vehicle_status_map.get(vehicle_status, "Unknown")
            self._attr_icon = {
                "Driving": "mdi:car-side",
                "Parked": "mdi:parking",
                "Starting": "mdi:car-key",
                "PowerOff": "mdi:car-off"
            }.get(self._state, "mdi:car")

    @property
    def extra_state_attributes(self):
        """ Return other attributes from the API response. """
        data = self._coordinator.data
        lat = data.get("vehicleExtend", {}).get("lat")
        lng = data.get("vehicleExtend", {}).get("lng")
        latitude = lat / 1e6 if lat is not None else None
        longitude = lng / 1e6 if lng is not None else None
        report_time = datetime.fromtimestamp(data.get("vehicleConnection", {}).get("reportTime") / 1000)

        attributes = {
            # chargingStatus
            "power_charge_status": data.get("chargingStatus", {}).get("powerChargeStatus"),
            "power_charge_time": data.get("chargingStatus", {}).get("powerChargeTime"),
            "obc_elect_wire_con_light_sts": data.get("chargingStatus", {}).get("obcElectWireConLightSts"),
            "obc_charge_voltage": data.get("chargingStatus", {}).get("obcChargeVoltage"),
            "obc_charge_voltage_inp": data.get("chargingStatus", {}).get("obcChargeVoltageInp"),
            "obc_charge_current": data.get("chargingStatus", {}).get("obcChargeCurrent"),
            "obc_charge_current_inp": data.get("chargingStatus", {}).get("obcChargeCurrentInp"),
            "obc_cm_state": data.get("chargingStatus", {}).get("obcCmState"),

            # vehicleBasic
            "dc_status": data.get("vehicleBasic", {}).get("dcStatus"),
            "total_current": data.get("vehicleBasic", {}).get("totalCurrent"),
            "charge_status": data.get("vehicleBasic", {}).get("chargeStatus"),
            "total_voltage": data.get("vehicleBasic", {}).get("totalVoltage"),
            "run_mode": data.get("vehicleBasic", {}).get("runMode"),
            "speed": data.get("vehicleBasic", {}).get("speed"),
            "gears": data.get("vehicleBasic", {}).get("gears"),
            "vehicle_status": data.get("vehicleBasic", {}).get("vehicleStatus"),

            # enduranceStatus
            "power_percentage": data.get("enduranceStatus", {}).get("powerPercentage"),
            "power_residue_mileage": data.get("enduranceStatus", {}).get("powerResidueMileage"),
            "estimate_fuel_level": data.get("enduranceStatus", {}).get("estimateFuelLevel"),
            "bms_battery_total_capacity": data.get("enduranceStatus", {}).get("bmsBatteryTotalCapacity"),
            "estimate_fuel_percent": data.get("enduranceStatus", {}).get("estimateFuelPercent"),
            "bms_hds_ah_active_cp_sum": data.get("enduranceStatus", {}).get("bmsHdsAhActiveCpSum"),
            "fuel_mileage_remaining": data.get("enduranceStatus", {}).get("fuelMileageRemaining"),

            # vehicleExtend
            "cellular_net_status": data.get("vehicleExtend", {}).get("cellularNetStatus"),
            "battery_12_voltage": data.get("vehicleExtend", {}).get("battery12Voltage"),
            "bat_electricity": data.get("vehicleExtend", {}).get("batElectricity"),
            "cellular_net_db": data.get("vehicleExtend", {}).get("cellularNetDb"),
            "motor_status": data.get("vehicleExtend", {}).get("motorStatus"),
            "drive_mode": data.get("vehicleExtend", {}).get("driveMode"),
            "bat_voltage": data.get("vehicleExtend", {}).get("batVoltage"),
            "position_status": data.get("vehicleExtend", {}).get("positionStatus"),
            "engine_status": data.get("vehicleExtend", {}).get("engineStatus"),
            "gps_status": data.get("vehicleExtend", {}).get("gpsStatus"),
            "battery_size": data.get("vehicleExtend", {}).get("batterySize"),
            "latitude": latitude,
            "lonngitude": longitude,

            # energyConsumption
            "today_energy_consumption": data.get("energyConsumption", {}).get("todayEnergyConsumption"),
            "total_average_consumption_rate": data.get("energyConsumption", {}).get("totalAverageConsumptionRate"),
            "itinerary_driving_mileage": data.get("energyConsumption", {}).get("itineraryDrivingMileage"),
            "average_consumption_per_km": data.get("energyConsumption", {}).get("averageConsumptionPerKm"),
            "trip_consumes_energy": data.get("energyConsumption", {}).get("tripConsumesEnergy"),
            "itinerary_duration": data.get("energyConsumption", {}).get("itineraryDuration"),

            # vehicleConnection
            "online": data.get("vehicleConnection", {}).get("online"),
            "online_status": data.get("vehicleConnection", {}).get("onlineStatus"),
            "report_time": report_time,
            "last_change_time": data.get("vehicleConnection", {}).get("lastChangeTime"),

            # lampStatus
            "small_light_status": data.get("lampStatus", {}).get("smallLightStatus"),
            "brake_beam_light_status": data.get("lampStatus", {}).get("brakeBeamLightStatus"),
            "high_beam_light_status": data.get("lampStatus", {}).get("highBeamLightStatus"),
            "right_turn_light_status": data.get("lampStatus", {}).get("rightTurnLightStatus"),
            "double_flash_light_status": data.get("lampStatus", {}).get("doubleFlashLightStatus"),
            "left_turn_light_status": data.get("lampStatus", {}).get("leftTurnLightStatus"),
            "mood_light_status": data.get("lampStatus", {}).get("moodLightStatus"),
            "dipped_head_light_status": data.get("lampStatus", {}).get("dippedHeadLightStatus"),

            # seatStatus
             "left_after_seat_heating_status": data.get("seatStatus", {}).get("leftAfterSeatHeatingStatus"),
             "right_after_seat_ventilation_status": data.get("seatStatus", {}).get("rightAfterSeatVentilationStatus"),
             "driver_folding_seat_status": data.get("seatStatus", {}).get("driverFoldingSeatStatus"),
             "right_after_seat_heating_status": data.get("seatStatus", {}).get("rightAfterSeatHeatingStatus"),
             "left_after_seat_ventilation_status": data.get("seatStatus", {}).get("leftAfterSeatVentilationStatus"),
             "co_driver_seat_ventilation_status": data.get("seatStatus", {}).get("coDriverSeatVentilationStatus"),
             "co_driver_folding_seat_status": data.get("seatStatus", {}).get("coDriverFoldingSeatStatus"),
             "co_driver_seat_heating_status": data.get("seatStatus", {}).get("coDriverSeatHeatingStatus"),
             "driver_seat_ventilation_status": data.get("seatStatus", {}).get("driverSeatVentilationStatus"),
             "driver_seat_heating_status": data.get("seatStatus", {}).get("driverSeatHeatingStatus"),
         
             # doorCoverStatus
             "cover_front_status": data.get("doorCoverStatus", {}).get("coverFrontStatus"),
             "slow_charge_cover_status": data.get("doorCoverStatus", {}).get("slowChargeCoverStatus"),
             "left_after_door_status": data.get("doorCoverStatus", {}).get("leftAfterDoorStatus"),
             "driver_size_door_status": data.get("doorCoverStatus", {}).get("driverSizeDoorStatus"),
             "co_driver_size_door_status": data.get("doorCoverStatus", {}).get("coDriverSizeDoorStatus"),
             "fuel_tank_cover_status": data.get("doorCoverStatus", {}).get("fuelTankCoverStatus"),
             "fast_charge_cover_status": data.get("doorCoverStatus", {}).get("fastChargeCoverStatus"),
             "right_after_door_status": data.get("doorCoverStatus", {}).get("rightAfterDoorStatus"),
             "car_boar_status": data.get("doorCoverStatus", {}).get("carBoarStatus"),
         
             # airconditionStatus
             "clm_vent_sts": data.get("airconditionStatus", {}).get("clmVentSts"),
             "defrost_status": data.get("airconditionStatus", {}).get("defrostStatus"),
             "air_filter_element": data.get("airconditionStatus", {}).get("airFilterElement"),
             "thermal_container_status": data.get("airconditionStatus", {}).get("thermalContainerStatus"),
             "air_temp": data.get("airconditionStatus", {}).get("airTemp"),
             "air_wind_level": data.get("airconditionStatus", {}).get("airWindLevel"),
             "lock_car_keep_status": data.get("airconditionStatus", {}).get("lockCarKeepStatus"),
             "air_out_temp": data.get("airconditionStatus", {}).get("airOutTemp"),
             "air_in_temp": data.get("airconditionStatus", {}).get("airInTemp"),
             "thermal_container_temp": data.get("airconditionStatus", {}).get("thermalContainerTemp"),
             "clm_foot_sts": data.get("airconditionStatus", {}).get("clmFootSts"),
             "air_mode": data.get("airconditionStatus", {}).get("airMode"),
             "clm_ac_sts": data.get("airconditionStatus", {}).get("clmAcSts"),
             "air_status": data.get("airconditionStatus", {}).get("airStatus"),
         
             # windowStatus
             "driver_size_win_status": data.get("windowStatus", {}).get("driverSizeWinStatus"),
             "sky_window_status": data.get("windowStatus", {}).get("skyWindowStatus"),
             "right_after_win_lock_status": data.get("windowStatus", {}).get("rightAfterWinLockStatus"),
             "left_after_win_status": data.get("windowStatus", {}).get("leftAfterWinStatus"),
             "co_driver_size_win_status": data.get("windowStatus", {}).get("coDriverSizeWinStatus"),
         
             # tyreStatus
             "tire_right_after_press": data.get("tyreStatus", {}).get("tireRightAfterPress"),
             "tire_right_front_press": data.get("tyreStatus", {}).get("tireRightFrontPress"),
             "tire_left_front_press": data.get("tyreStatus", {}).get("tireLeftFrontPress"),
             "tire_right_front_temp": data.get("tyreStatus", {}).get("tireRightFrontTemp"),
             "tire_left_after_temp": data.get("tyreStatus", {}).get("tireLeftAfterTemp"),
             "tire_left_front_temp": data.get("tyreStatus", {}).get("tireLeftFrontTemp"),
             "tire_right_after_temp": data.get("tyreStatus", {}).get("tireRightAfterTemp"),
             "tire_left_after_press": data.get("tyreStatus", {}).get("tireLeftAfterPress"),
         
             # lockStatus
             "co_driver_size_door_lock_status": data.get("lockStatus", {}).get("coDriverSizeDoorLockStatus"),
             "slow_charge_cover_lock_status": data.get("lockStatus", {}).get("slowChargeCoverLockStatus"),
             "driver_size_door_lock_status": data.get("lockStatus", {}).get("driverSizeDoorLockStatus"),
             "car_boar_lock_status": data.get("lockStatus", {}).get("carBoarLockStatus"),
             "left_after_door_lock_status": data.get("lockStatus", {}).get("leftAfterDoorLockStatus"),
             "fast_charge_cover_lock_status": data.get("lockStatus", {}).get("fastChargeCoverLockStatus"),
             "right_after_door_lock_status": data.get("lockStatus", {}).get("rightAfterDoorLockStatus"),
             "fuel_tank_cover_lock_status": data.get("lockStatus", {}).get("fuelTankCoverLockStatus"),
        }

        return attributes

class EngineStatusSensor(BaseSensor):
    def update_state(self, data):
        """更新引擎状态。"""
        engine_status = data.get("vehicleExtend", {}).get("engineStatus")
        self._state = {1: "on", 0: "off"}.get(engine_status, "unknown")
        # 根据引擎状态更新图标
        if self._state == "on":
            self._attr_icon = "mdi:engine-outline"
        else:
            self._attr_icon = "mdi:engine-off"

    @property
    def extra_state_attributes(self):
        """ Return other attributes from the API response. """
        data = self._coordinator.data
        engine_status = data.get("vehicleExtend", {}).get("engineStatus")

        attributes = {
                "value": engine_status,
                }

        return attributes

class ChargingStatusSensor(BaseSensor):
    def update_state(self, data):
        """更新充电状态。"""
        charge_status = data.get("vehicleBasic", {}).get("chargeStatus")
        self._state = {1: "on", 3: "off"}.get(charge_status, "unknown")
        # 根据充电状态更新图标
        if self._state == "on":
            self._attr_icon = "mdi:battery-charging"
        else:
            self._attr_icon = "mdi:ev-station"

    @property
    def extra_state_attributes(self):
        """ Return other attributes from the API response. """
        data = self._coordinator.data
        charge_status = data.get("vehicleBasic", {}).get("chargeStatus")

        attributes = {
                "value": charge_status,
                }

        return attributes

class MileageSensor(BaseSensor):
    def update_state(self, data):
        """更新总里程数。"""
        self._state = data.get("vehicleBasic", {}).get("mileage")
        self._attr_icon = "mdi:counter"

    @property
    def unit_of_measurement(self):
        return "km"

class BatteryRange(BaseSensor):
    def update_state(self, data):
        """剩余电池里程数。"""
        power_residue_mileage = data.get("enduranceStatus", {}).get("powerResidueMileage")
        self._state = round(float(power_residue_mileage) / 10 , 2)
        self._attr_icon = "mdi:map-marker-distance"

    @property
    def unit_of_measurement(self):
        return "km"

class FuleRange(BaseSensor):
    def update_state(self, data):
        """剩余汽油里程数。"""
        fuel_mileage_remaining = data.get("enduranceStatus", {}).get("fuelMileageRemaining")
        self._state = round(float(fuel_mileage_remaining) / 10 , 2)
        self._attr_icon = "mdi:gas-station-outline"

    @property
    def unit_of_measurement(self):
        return "km"

class Speed(BaseSensor):
    def update_state(self, data):
        """更新时速。"""
        speed  = data.get("vehicleBasic", {}).get("speed")
        self._state = round(float(speed) / SPEED_SCALE, 2)
        self._attr_icon = "mdi:speedometer"

    @property
    def unit_of_measurement(self):
        return "km/h"

class RemainingEnergyKwh(BaseSensor):
    def update_state(self, data):
        """剩余电能传感器 (kWh)"""
        """更新剩余电能状态"""
        _LOGGER.debug("开始更新剩余电能状态")
        
        self._attr_icon = "mdi:battery-charging-100"
        power_percentage = data.get("enduranceStatus", {}).get("powerPercentage", 0)
        battery_capacity = data.get("enduranceStatus", {}).get("bmsBatteryTotalCapacity", 0)
        battery_voltage = data.get("vehicleExtend", {}).get("batVoltage", 0)

        _LOGGER.debug("获取到的原始数据: power_percentage=%s, battery_capacity=%s, battery_voltage=%s",
                     power_percentage, battery_capacity, battery_voltage)

        # 检查 battery_voltage 是否为列表，如果是则取第一个值
        if isinstance(battery_voltage, list) and battery_voltage:
            battery_voltage = battery_voltage[0]
            _LOGGER.debug("电池电压是列表，使用第一个值: %s", battery_voltage)
        
        if all(v is not None for v in [power_percentage, battery_capacity, battery_voltage]):
            # 使用常量进行单位转换
            percentage = float(power_percentage) / PERCENTAGE_SCALE
            voltage = float(battery_voltage) / VOLTAGE_SCALE
            
            # 计算剩余电量 (kWh)
            wh = percentage * float(battery_capacity) * voltage
            self._state = round(wh / POWER_SCALE, 2)
            _LOGGER.debug("计算结果: percentage=%s, voltage=%s, wh=%s, final_state=%s",
                         percentage, voltage, wh, self._state)
        else:
            self._state = None
            _LOGGER.warning("数据不完整，无法计算剩余电量")

    @property
    def unit_of_measurement(self):
        return "kWh"

class ChargingPowerKw(BaseSensor):
    def update_state(self, data):
        """充电功率传感器 (kW)"""
        """更新充电功率状态"""
        _LOGGER.debug("开始更新充电功率状态")
        
        self._attr_icon = "mdi:transmission-tower-export"
        charge_voltage = data.get("chargingStatus", {}).get("obcChargeVoltage")
        charge_current = data.get("chargingStatus", {}).get("obcChargeCurrent")
        
        _LOGGER.debug("获取到的原始数据: charge_voltage=%s, charge_current=%s",
                     charge_voltage, charge_current)
        
        if charge_voltage is not None and charge_current is not None:
            # 使用常量进行单位转换
            voltage = float(charge_voltage) / VOLTAGE_SCALE
            current = float(charge_current) / CURRENT_SCALE
            watts = voltage * current
            self._state = round(watts / POWER_SCALE, 2)
            _LOGGER.debug("计算结果: voltage=%s, current=%s, watts=%s, final_state=%s",
                         voltage, current, watts, self._state)
        else:
            self._state = None
            _LOGGER.warning("充电数据不完整，无法计算充电功率")

    @property
    def unit_of_measurement(self):
        return "kW"

class DischargingPowerKw(BaseSensor):
    def update_state(self, data):
        """放电功率传感器 (kW)"""
        """更新放电功率状态"""
        _LOGGER.debug("开始更新放电功率状态")
        
        total_voltage = data.get("vehicleBasic", {}).get("totalVoltage")
        total_current = data.get("vehicleBasic", {}).get("totalCurrent")
        speed = data.get("vehicleBasic", {}).get("speed")
        
        _LOGGER.debug("获取到的原始数据: total_voltage=%s, total_current=%s, speed=%s",
                     total_voltage, total_current, speed)
        
        self._attr_icon = "mdi:transmission-tower-import"
        
        # 只在车辆行驶时（速度大于0）计算放电功率
        if all(v is not None for v in [total_voltage, total_current, speed]) and float(speed) > 0:
            # 使用常量进行单位转换
            voltage = float(total_voltage) / VOLTAGE_SCALE
            current = float(total_current) / CURRENT_SCALE
            watts = voltage * current
            self._state = round(watts / POWER_SCALE, 2)
            _LOGGER.debug("计算结果: voltage=%s, current=%s, watts=%s, final_state=%s",
                         voltage, current, watts, self._state)
        else:
            self._state = None
            _LOGGER.warning("放电数据不完整或车辆静止，无法计算放电功率")

    @property
    def unit_of_measurement(self):
        return "kW"

class TripEnergyTracker:
    """行程能耗追踪器"""
    def __init__(self):
        self.samples = []  # [(timestamp, energy_kwh, distance_km)]
        self.charging_detected = False
        self.last_energy = None
        self.last_distance = None
        self.last_sample_time = None
        self.SAMPLE_INTERVAL = 60  # 采样间隔（秒）
        self.CHARGING_THRESHOLD = 0.2  # 充电检测阈值（kWh）
        self.daily_consumption = {}  # 按天统计的能耗 (日期 -> 能量消耗)
        self.total_consumption = 0  # 历史累计能耗
        
    def add_sample(self, timestamp: datetime, energy_kwh: float, distance_km: float) -> None:
        """添加一个采样点"""
        # 检查是否达到采样间隔
        if self.last_sample_time and (timestamp - self.last_sample_time).total_seconds() < self.SAMPLE_INTERVAL:
            _LOGGER.debug("采样间隔未到，跳过本次采样")
            return
            
        _LOGGER.debug(
            "添加采样点 - 时间: %s, 能量: %.2f kWh, 距离: %.2f km",
            timestamp.isoformat(), energy_kwh, distance_km
        )
        
        # 检测是否发生充电（考虑动能回收）
        if self.last_energy is not None:
            energy_diff = energy_kwh - self.last_energy
            if energy_diff > self.CHARGING_THRESHOLD:  # 只有超过阈值才认为是充电
                _LOGGER.debug(
                    "检测到充电 - 当前能量: %.2f kWh, 上次能量: %.2f kWh, 差值: %.2f kWh",
                    energy_kwh, self.last_energy, energy_diff
                )
                self.charging_detected = True
                self.samples = []
            else:
                self.charging_detected = False
                _LOGGER.debug(
                    "能量变化 - 当前能量: %.2f kWh, 上次能量: %.2f kWh, 差值: %.2f kWh",
                    energy_kwh, self.last_energy, energy_diff
                )
                # 更新按天的能耗数据
                day = timestamp.date()
                if day not in self.daily_consumption:
                    self.daily_consumption[day] = 0
                self.daily_consumption[day] += energy_diff

                # 更新历史累计能耗
                self.total_consumption += energy_diff
        
        self.samples.append((timestamp, energy_kwh, distance_km))
        self.last_energy = energy_kwh
        self.last_distance = distance_km
        self.last_sample_time = timestamp
        
        # 只保留最近30分钟的数据
        cutoff_time = timestamp - timedelta(minutes=30)
        original_len = len(self.samples)
        self.samples = [s for s in self.samples if s[0] >= cutoff_time]
        if len(self.samples) != original_len:
            _LOGGER.debug("清理过期数据 - 原始数量: %d, 当前数量: %d", original_len, len(self.samples))
    
    def calculate_consumption(self) -> Optional[Tuple[float, float]]:
        """计算能耗和行驶距离"""
        if len(self.samples) < 2:
            _LOGGER.debug("采样点数量不足: %d", len(self.samples))
            return None
            
        first = self.samples[0]
        last = self.samples[-1]
        
        # 计算时间差（分钟）
        time_diff = (last[0] - first[0]).total_seconds() / 60
        _LOGGER.debug("时间差: %.2f 分钟", time_diff)
        
        # 增加最小时间差和最大时间差的验证
        if time_diff < 2 or time_diff > 60:  # 最小时间差改为2分钟
            _LOGGER.debug("时间差超出有效范围: %.2f 分钟", time_diff)
            return None
            
        # 计算能量差值（kWh）和距离差值（km）
        energy_diff = first[1] - last[1]
        distance_diff = last[2] - first[2]
        _LOGGER.debug("能量差: %.2f kWh, 距离差: %.2f km", energy_diff, distance_diff)
        
        # 增加最小差值阈值验证
        if abs(energy_diff) < 0.05 or distance_diff < 0.2:  # 增加最小阈值
            _LOGGER.debug("差值太小 - 能量差: %.2f kWh, 距离差: %.2f km", energy_diff, distance_diff)
            return None
            
        # 增加异常值验证（允许小幅度能量增加）
        if energy_diff < -0.5 or distance_diff <= 0:  # 允许最多0.5kWh的能量回收
            _LOGGER.debug(
                "异常值检测 - 能量差: %.2f, 距离差: %.2f",
                energy_diff, distance_diff
            )
            return None
        
        # 增加能耗效率合理性验证
        efficiency = energy_diff / distance_diff
        if not (0.05 <= efficiency <= 0.5):  # 调整最小效率阈值
            _LOGGER.debug("能效不合理: %.2f kWh/km", efficiency)
            return None
                
        _LOGGER.debug("计算结果 - 能量消耗: %.2f kWh, 距离: %.2f km", energy_diff, distance_diff)
        return energy_diff, distance_diff

    def get_daily_consumption(self, day: date) -> float:
        """获取指定日期的能耗"""
        return self.daily_consumption.get(day, 0)

    def get_total_consumption(self) -> float:
        """获取历史累计能耗"""
        return self.total_consumption

class TripEnergyConsumptionKwh(BaseSensor):
    """单次行程能耗传感器 (kWh)"""
    def __init__(self, coordinator: UpdateCoordinator, name: str, unique_id_base: str):
        super().__init__(coordinator, name, unique_id_base)
        self._attr_icon = "mdi:chart-line"
        self.tracker = TripEnergyTracker()
        
    def update_state(self, data):
        """更新行程能耗状态"""
        _LOGGER.debug("开始更新行程能耗状态")
        
        # 获取当前剩余电量（kWh）
        power_percentage = data.get("enduranceStatus", {}).get("powerPercentage", 0)
        battery_capacity = data.get("enduranceStatus", {}).get("bmsBatteryTotalCapacity", 0)
        battery_voltage = data.get("vehicleExtend", {}).get("batVoltage", 0)
        current_distance = data.get("vehicleBasic", {}).get("mileage")
        
        _LOGGER.debug(
            "原始数据 - 电量百分比: %s, 电池容量: %s, 电压: %s, 里程: %s",
            power_percentage, battery_capacity, battery_voltage, current_distance
        )

        # 检查 battery_voltage 是否为列表
        if isinstance(battery_voltage, list) and battery_voltage:
            battery_voltage = battery_voltage[0]
            _LOGGER.debug("电压是列表，使用第一个值: %s", battery_voltage)
        
        if all(v is not None for v in [power_percentage, battery_capacity, battery_voltage, current_distance]):
            # 使用常量进行单位转换
            percentage = float(power_percentage) / PERCENTAGE_SCALE
            voltage = float(battery_voltage) / VOLTAGE_SCALE
            current_energy = percentage * float(battery_capacity) * voltage / POWER_SCALE
            current_distance = float(current_distance) / DISTANCE_SCALE
            
            _LOGGER.debug(
                "转换后数据 - 百分比: %.2f, 电压: %.2f, 当前能量: %.2f kWh, 当前距离: %.2f km",
                percentage, voltage, current_energy, current_distance
            )
            
            self.tracker.add_sample(datetime.now(), current_energy, current_distance)
            
            result = self.tracker.calculate_consumption()
            if result:
                energy_diff, _ = result
                self._state = round(energy_diff, 2)
                _LOGGER.debug("更新状态成功: %.2f kWh", self._state)
            else:
                self._state = None
                _LOGGER.debug("计算结果为空，状态设为 None")
        else:
            self._state = None
            _LOGGER.debug("数据不完整，状态设为 None")

    @property
    def unit_of_measurement(self):
        return "kWh"

    @property
    def extra_state_attributes(self):
        """传感器的额外状态属性：每日能耗和历史累计能耗"""
        return {
            "daily_consumption": self.tracker.get_daily_consumption(datetime.now().date()),  # 今天的能耗
            "total_consumption": self.tracker.get_total_consumption()  # 总能耗
        }

    def get_daily_consumption(self, day: date) -> float:
        """获取指定日期的能耗"""
        return self.tracker.get_daily_consumption(day)

    def get_total_consumption(self) -> float:
        """获取历史累计能耗"""
        return self.tracker.get_total_consumption()

class EnergyConsumptionPerKm(BaseSensor):
    """单位能耗传感器 (kWh/km)"""
    def __init__(self, coordinator: UpdateCoordinator, name: str, unique_id_base: str):
        super().__init__(coordinator, name, unique_id_base)
        self._attr_icon = "mdi:chart-box"
        self.tracker = TripEnergyTracker()
        
    def update_state(self, data):
        """更新单位能耗状态"""
        _LOGGER.debug("开始更新单位能耗状态")
        
        # 获取当前剩余电量（kWh）
        power_percentage = data.get("enduranceStatus", {}).get("powerPercentage", 0)
        battery_capacity = data.get("enduranceStatus", {}).get("bmsBatteryTotalCapacity", 0)
        battery_voltage = data.get("vehicleExtend", {}).get("batVoltage", 0)
        current_distance = data.get("vehicleBasic", {}).get("mileage")
        
        _LOGGER.debug(
            "原始数据 - 电量百分比: %s, 电池容量: %s, 电压: %s, 里程: %s",
            power_percentage, battery_capacity, battery_voltage, current_distance
        )

        if isinstance(battery_voltage, list) and battery_voltage:
            battery_voltage = battery_voltage[0]
            _LOGGER.debug("电压是列表，使用第一个值: %s", battery_voltage)
        
        if all(v is not None for v in [power_percentage, battery_capacity, battery_voltage, current_distance]):
            percentage = float(power_percentage) / PERCENTAGE_SCALE
            voltage = float(battery_voltage) / VOLTAGE_SCALE
            current_energy = percentage * float(battery_capacity) * voltage / POWER_SCALE
            current_distance = float(current_distance) / DISTANCE_SCALE
            
            _LOGGER.debug(
                "转换后数据 - 百分比: %.2f, 电压: %.2f, 当前能量: %.2f kWh, 当前距离: %.2f km",
                percentage, voltage, current_energy, current_distance
            )
            
            self.tracker.add_sample(datetime.now(), current_energy, current_distance)
            
            result = self.tracker.calculate_consumption()
            if result:
                energy_diff, distance_diff = result
                if distance_diff > 0:
                    self._state = round(energy_diff / distance_diff, 2)
                    _LOGGER.debug("更新状态成功: %.2f kWh/km", self._state)
                else:
                    self._state = None
                    _LOGGER.debug("距离差为0，状态设为 None")
            else:
                self._state = None
                _LOGGER.debug("计算结果为空，状态设为 None")
        else:
            self._state = None
            _LOGGER.debug("数据不完整，状态设为 None")

    @property
    def unit_of_measurement(self):
        return "kWh/km"

class LocationSensor(TrackerEntity):
    def __init__(self, coordinator: UpdateCoordinator, name: str, unique_id_base: str, hass):
        """初始化 LocationSensor"""
        self._coordinator = coordinator
        self._name = name
        self._unique_id = f"{unique_id_base}_{name.replace(' ', '_').lower()}"
        self.hass = hass
        self._state = "not_home"  # 初始状态
        self._unsubscribe_update = None  # 用于存储取消监听的函数
        self._attr_icon = "mdi:map-marker"

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def state(self) -> str:
        return self._state

    @property
    def latitude(self) -> float | None:
        """返回车辆的纬度。"""
        data = self._coordinator.data
        lat = data.get("vehicleExtend", {}).get("lat") if data else None
        return lat / COORDINATE_SCALE if lat is not None else None

    @property
    def longitude(self) -> float | None:
        """返回车辆的经度。"""
        data = self._coordinator.data
        lng = data.get("vehicleExtend", {}).get("lng") if data else None
        return lng / COORDINATE_SCALE if lng is not None else None

    @property
    def battery_level(self) -> int | None:
        """返回车辆的电池电量。"""
        data = self._coordinator.data
        return data.get("vehicleBasic", {}).get("soc") if data else None

    @property
    def gps_accuracy(self) -> int:
        """返回 GPS 精度。"""
        return 10  # 默认的 GPS 精度值

    async def async_added_to_hass(self):
        """实体被添加到 Home Assistant 时调用。"""
        _LOGGER.debug("Location sensor added: %s", self._name)
        self._unsubscribe_update = self._coordinator.async_add_listener(self.async_update)

    async def async_will_remove_from_hass(self):
        """实体从 Home Assistant 中移除时调用。"""
        _LOGGER.debug("Location sensor removed: %s", self._name)
        if self._unsubscribe_update:
            self._unsubscribe_update()

    async def async_update(self):
        """异步更新位置状态。"""
        _LOGGER.debug("Updating location sensor: %s", self._name)
        data = self._coordinator.data

        if data:
            lat = self.latitude
            lng = self.longitude

            if lat is not None and lng is not None:
                # 使用 Home Assistant 的 is_in_zone 方法检查是否在 home 区域
                if in_zone(self.hass.states.get("zone.home"), lat, lng):
                    self._state = "home"
                else:
                    self._state = "not_home"
            else:
                self._state = "not_home"
