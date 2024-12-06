import logging
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.components.device_tracker import TrackerEntity
from datetime import timedelta
from homeassistant.components.zone import in_zone
from .update_coordinator import UpdateCoordinator
from .const import (
    DOMAIN,
    CONF_VIN,
    CONF_NAME,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """设置传感器平台。"""
    _LOGGER.debug("Setting up sensors for Neta Vehicle Status...")
    name = config_entry.data.get(CONF_NAME)
    vin = config_entry.data.get(CONF_VIN)

    coordinator: UpdateCoordinator = hass.data["neta_vehicle_status"][config_entry.entry_id]


    # 定义传感器实体
    sensors = [
        BatteryLevelSensor(coordinator, f"{name} Battery Level", vin),
        ChargingStatusSensor(coordinator, name, vin),
        MileageSensor(coordinator, f"{name} Mileage", vin),
        LocationSensor(coordinator, f"{name} Location", vin, hass),
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
        self._state = data.get("vehicleBasic", {}).get("soc")

    @property
    def device_class(self):
        return SensorDeviceClass.BATTERY


class ChargingStatusSensor(BaseSensor):
    def update_state(self, data):
        """更新充电状态。"""
        self._state = data.get("vehicleExtend", {}).get("engineStatus")

    @property
    def extra_state_attributes(self):
        """ Return other attributes from the API response. """
        data = self._coordinator.data
        lat = data.get("vehicleExtend", {}).get("lat")
        lng = data.get("vehicleExtend", {}).get("lng")
        latitude = lat / 1e6 if lat is not None else None
        longitude = lng / 1e6 if lng is not None else None

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
            "report_time": data.get("vehicleConnection", {}).get("reportTime"),
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
        }

        return attributes

class MileageSensor(BaseSensor):
    def update_state(self, data):
        """更新总里程数。"""
        self._state = data.get("vehicleBasic", {}).get("mileage")

    @property
    def unit_of_measurement(self):
        return "km"

class LocationSensor(TrackerEntity):
    def __init__(self, coordinator: UpdateCoordinator, name: str, unique_id_base: str, hass):
        """初始化 LocationSensor"""
        self._coordinator = coordinator
        self._name = name
        self._unique_id = f"{unique_id_base}_{name.replace(' ', '_').lower()}"
        self.hass = hass
        self._state = "not_home"  # 初始状态
        self._unsubscribe_update = None  # 用于存储取消监听的函数

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
        return lat / 1e6 if lat is not None else None

    @property
    def longitude(self) -> float | None:
        """返回车辆的经度。"""
        data = self._coordinator.data
        lng = data.get("vehicleExtend", {}).get("lng") if data else None
        return lng / 1e6 if lng is not None else None

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
