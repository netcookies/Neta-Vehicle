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

    coordinator: UpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

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
            # chargingStatus - 充电状态相关
            "power_charge_status": data.get("chargingStatus", {}).get("powerChargeStatus"),  # 当前充电状态
            "power_charge_time": data.get("chargingStatus", {}).get("powerChargeTime"),  # 预计充满电时间
            "obc_elect_wire_con_light_sts": data.get("chargingStatus", {}).get("obcElectWireConLightSts"),  # 电缆连接灯状态
            "obc_charge_voltage": data.get("chargingStatus", {}).get("obcChargeVoltage"),  # 车载充电机输出电压
            "obc_charge_voltage_inp": data.get("chargingStatus", {}).get("obcChargeVoltageInp"),  # 车载充电机输入电压
            "obc_charge_current": data.get("chargingStatus", {}).get("obcChargeCurrent"),  # 车载充电机输出电流
            "obc_charge_current_inp": data.get("chargingStatus", {}).get("obcChargeCurrentInp"),  # 车载充电机输入电流
            "obc_cm_state": data.get("chargingStatus", {}).get("obcCmState"),  # OBC（车载充电机）状态码
        
            # vehicleBasic - 车辆基本状态
            "dc_status": data.get("vehicleBasic", {}).get("dcStatus"),  # 直流系统状态
            "total_current": data.get("vehicleBasic", {}).get("totalCurrent"),  # 总电流
            "charge_status": data.get("vehicleBasic", {}).get("chargeStatus"),  # 充电状态
            "total_voltage": data.get("vehicleBasic", {}).get("totalVoltage"),  # 总电压
            "run_mode": data.get("vehicleBasic", {}).get("runMode"),  # 行驶模式
            "speed": data.get("vehicleBasic", {}).get("speed"),  # 当前速度
            "gears": data.get("vehicleBasic", {}).get("gears"),  # 档位状态
            "vehicle_status": data.get("vehicleBasic", {}).get("vehicleStatus"),  # 车辆整体状态
        
            # enduranceStatus - 续航状态
            "power_percentage": data.get("enduranceStatus", {}).get("powerPercentage"),  # 电池电量百分比
            "power_residue_mileage": data.get("enduranceStatus", {}).get("powerResidueMileage"),  # 剩余可行驶里程（电动）
            "estimate_fuel_level": data.get("enduranceStatus", {}).get("estimateFuelLevel"),  # 估算油量（L）
            "bms_battery_total_capacity": data.get("enduranceStatus", {}).get("bmsBatteryTotalCapacity"),  # BMS记录的电池总容量
            "estimate_fuel_percent": data.get("enduranceStatus", {}).get("estimateFuelPercent"),  # 燃油剩余百分比
            "bms_hds_ah_active_cp_sum": data.get("enduranceStatus", {}).get("bmsHdsAhActiveCpSum"),  # 有效容量（Ah）
            "fuel_mileage_remaining": data.get("enduranceStatus", {}).get("fuelMileageRemaining"),  # 剩余可行驶里程（燃油）
        
            # vehicleExtend - 车辆扩展信息
            "cellular_net_status": data.get("vehicleExtend", {}).get("cellularNetStatus"),  # 蜂窝网络状态
            "battery_12_voltage": data.get("vehicleExtend", {}).get("battery12Voltage"),  # 12V电池电压
            "bat_electricity": data.get("vehicleExtend", {}).get("batElectricity"),  # 电池当前电量（估算）
            "cellular_net_db": data.get("vehicleExtend", {}).get("cellularNetDb"),  # 蜂窝信号强度（dB）
            "motor_status": data.get("vehicleExtend", {}).get("motorStatus"),  # 电机状态
            "drive_mode": data.get("vehicleExtend", {}).get("driveMode"),  # 驱动模式（前驱/后驱等）
            "bat_voltage": data.get("vehicleExtend", {}).get("batVoltage"),  # 主电池电压
            "position_status": data.get("vehicleExtend", {}).get("positionStatus"),  # 定位状态
            "engine_status": data.get("vehicleExtend", {}).get("engineStatus"),  # 发动机状态
            "gps_status": data.get("vehicleExtend", {}).get("gpsStatus"),  # GPS状态
            "battery_size": data.get("vehicleExtend", {}).get("batterySize"),  # 电池容量（kWh）
            "latitude": latitude,  # GPS纬度
            "lonngitude": longitude,  # GPS经度
        
            # energyConsumption - 能耗信息
            "today_energy_consumption": data.get("energyConsumption", {}).get("todayEnergyConsumption"),  # 今日能耗
            "total_average_consumption_rate": data.get("energyConsumption", {}).get("totalAverageConsumptionRate"),  # 平均能耗（总）
            "itinerary_driving_mileage": data.get("energyConsumption", {}).get("itineraryDrivingMileage"),  # 行驶里程（行程）
            "average_consumption_per_km": data.get("energyConsumption", {}).get("averageConsumptionPerKm"),  # 单位能耗
            "trip_consumes_energy": data.get("energyConsumption", {}).get("tripConsumesEnergy"),  # 本次出行消耗能量
            "itinerary_duration": data.get("energyConsumption", {}).get("itineraryDuration"),  # 本次出行时长
        
            # vehicleConnection - 车辆连接状态
            "online": data.get("vehicleConnection", {}).get("online"),  # 是否在线
            "online_status": data.get("vehicleConnection", {}).get("onlineStatus"),  # 在线状态
            "report_time": data.get("vehicleConnection", {}).get("reportTime"),  # 数据上报时间
            "last_change_time": data.get("vehicleConnection", {}).get("lastChangeTime"),  # 最后变更时间
        
            # lampStatus - 灯光状态
            "small_light_status": data.get("lampStatus", {}).get("smallLightStatus"),  # 小灯状态
            "brake_beam_light_status": data.get("lampStatus", {}).get("brakeBeamLightStatus"),  # 刹车灯状态
            "high_beam_light_status": data.get("lampStatus", {}).get("highBeamLightStatus"),  # 远光灯状态
            "right_turn_light_status": data.get("lampStatus", {}).get("rightTurnLightStatus"),  # 右转向灯状态
            "double_flash_light_status": data.get("lampStatus", {}).get("doubleFlashLightStatus"),  # 双闪状态
            "left_turn_light_status": data.get("lampStatus", {}).get("leftTurnLightStatus"),  # 左转向灯状态
            "mood_light_status": data.get("lampStatus", {}).get("moodLightStatus"),  # 氛围灯状态
            "dipped_head_light_status": data.get("lampStatus", {}).get("dippedHeadLightStatus"),  # 近光灯状态
        
            # seatStatus - 座椅状态
            "left_after_seat_heating_status": data.get("seatStatus", {}).get("leftAfterSeatHeatingStatus"),  # 后排左座加热状态
            "right_after_seat_ventilation_status": data.get("seatStatus", {}).get("rightAfterSeatVentilationStatus"),  # 后排右座通风状态
            "driver_folding_seat_status": data.get("seatStatus", {}).get("driverFoldingSeatStatus"),  # 主驾折叠座状态
            "right_after_seat_heating_status": data.get("seatStatus", {}).get("rightAfterSeatHeatingStatus"),  # 后排右座加热状态
            "left_after_seat_ventilation_status": data.get("seatStatus", {}).get("leftAfterSeatVentilationStatus"),  # 后排左座通风状态
            "co_driver_seat_ventilation_status": data.get("seatStatus", {}).get("coDriverSeatVentilationStatus"),  # 副驾通风状态
            "co_driver_folding_seat_status": data.get("seatStatus", {}).get("coDriverFoldingSeatStatus"),  # 副驾折叠座状态
            "co_driver_seat_heating_status": data.get("seatStatus", {}).get("coDriverSeatHeatingStatus"),  # 副驾加热状态
            "driver_seat_ventilation_status": data.get("seatStatus", {}).get("driverSeatVentilationStatus"),  # 主驾通风状态
            "driver_seat_heating_status": data.get("seatStatus", {}).get("driverSeatHeatingStatus"),  # 主驾加热状态
        
            # doorCoverStatus - 车门/盖状态
            "cover_front_status": data.get("doorCoverStatus", {}).get("coverFrontStatus"),  # 前舱盖状态
            "slow_charge_cover_status": data.get("doorCoverStatus", {}).get("slowChargeCoverStatus"),  # 慢充口盖状态
            "left_after_door_status": data.get("doorCoverStatus", {}).get("leftAfterDoorStatus"),  # 左后门状态
            "driver_size_door_status": data.get("doorCoverStatus", {}).get("driverSizeDoorStatus"),  # 主驾门状态
            "co_driver_size_door_status": data.get("doorCoverStatus", {}).get("coDriverSizeDoorStatus"),  # 副驾门状态
            "fuel_tank_cover_status": data.get("doorCoverStatus", {}).get("fuelTankCoverStatus"),  # 油箱盖状态
            "fast_charge_cover_status": data.get("doorCoverStatus", {}).get("fastChargeCoverStatus"),  # 快充口盖状态
            "right_after_door_status": data.get("doorCoverStatus", {}).get("rightAfterDoorStatus"),  # 右后门状态
            "car_boar_status": data.get("doorCoverStatus", {}).get("carBoarStatus"),  # 后备箱状态
        
            # airconditionStatus - 空调系统
            "clm_vent_sts": data.get("airconditionStatus", {}).get("clmVentSts"),  # 通风状态
            "defrost_status": data.get("airconditionStatus", {}).get("defrostStatus"),  # 除霜状态
            "air_filter_element": data.get("airconditionStatus", {}).get("airFilterElement"),  # 空调滤芯状态
            "thermal_container_status": data.get("airconditionStatus", {}).get("thermalContainerStatus"),  # 热管理容器状态
            "air_temp": data.get("airconditionStatus", {}).get("airTemp"),  # 空调设定温度
            "air_wind_level": data.get("airconditionStatus", {}).get("airWindLevel"),  # 风速等级
            "lock_car_keep_status": data.get("airconditionStatus", {}).get("lockCarKeepStatus"),  # 锁车维持状态
            "air_out_temp": data.get("airconditionStatus", {}).get("airOutTemp"),  # 出风口温度
            "air_in_temp": data.get("airconditionStatus", {}).get("airInTemp"),  # 进风口温度
            "thermal_container_temp": data.get("airconditionStatus", {}).get("thermalContainerTemp"),  # 热容器温度
            "clm_foot_sts": data.get("airconditionStatus", {}).get("clmFootSts"),  # 脚部送风状态
            "air_mode": data.get("airconditionStatus", {}).get("airMode"),  # 空调模式（自动、手动等）
            "clm_ac_sts": data.get("airconditionStatus", {}).get("clmAcSts"),  # 压缩机状态
            "air_status": data.get("airconditionStatus", {}).get("airStatus"),  # 空调开关状态
        
            # windowStatus - 车窗状态
            "driver_size_win_status": data.get("windowStatus", {}).get("driverSizeWinStatus"),  # 主驾车窗状态
            "sky_window_status": data.get("windowStatus", {}).get("skyWindowStatus"),  # 天窗状态
            "right_after_win_lock_status": data.get("windowStatus", {}).get("rightAfterWinLockStatus"),  # 右后车窗锁定状态
            "left_after_win_status": data.get("windowStatus", {}).get("leftAfterWinStatus"),  # 左后车窗状态
            "co_driver_size_win_status": data.get("windowStatus", {}).get("coDriverSizeWinStatus"),  # 副驾车窗状态
        
            # tyreStatus - 胎压与胎温
            "tire_right_after_press": data.get("tyreStatus", {}).get("tireRightAfterPress"),  # 右后轮胎压
            "tire_right_front_press": data.get("tyreStatus", {}).get("tireRightFrontPress"),  # 右前轮胎压
            "tire_left_front_press": data.get("tyreStatus", {}).get("tireLeftFrontPress"),  # 左前轮胎压
            "tire_right_front_temp": data.get("tyreStatus", {}).get("tireRightFrontTemp"),  # 右前轮胎温
            "tire_left_after_temp": data.get("tyreStatus", {}).get("tireLeftAfterTemp"),  # 左后轮胎温
            "tire_left_front_temp": data.get("tyreStatus", {}).get("tireLeftFrontTemp"),  # 左前轮胎温
            "tire_right_after_temp": data.get("tyreStatus", {}).get("tireRightAfterTemp"),  # 右后轮胎温
            "tire_left_after_press": data.get("tyreStatus", {}).get("tireLeftAfterPress"),  # 左后轮胎压
        
            # lockStatus - 锁状态
            "co_driver_size_door_lock_status": data.get("lockStatus", {}).get("coDriverSizeDoorLockStatus"),  # 副驾门锁状态
            "slow_charge_cover_lock_status": data.get("lockStatus", {}).get("slowChargeCoverLockStatus"),  # 慢充口锁状态
            "driver_size_door_lock_status": data.get("lockStatus", {}).get("driverSizeDoorLockStatus"),  # 主驾门锁状态
            "car_boar_lock_status": data.get("lockStatus", {}).get("carBoarLockStatus"),  # 后备箱锁状态
            "left_after_door_lock_status": data.get("lockStatus", {}).get("leftAfterDoorLockStatus"),  # 左后门锁状态
            "fast_charge_cover_lock_status": data.get("lockStatus", {}).get("fastChargeCoverLockStatus"),  # 快充口锁状态
            "right_after_door_lock_status": data.get("lockStatus", {}).get("rightAfterDoorLockStatus"),  # 右后门锁状态
            "fuel_tank_cover_lock_status": data.get("lockStatus", {}).get("fuelTankCoverLockStatus"),  # 油箱盖锁状态
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
