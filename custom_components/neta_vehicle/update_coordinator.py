import asyncio
import logging
import time
import aiohttp
from datetime import timedelta
from typing import Callable, List
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval, async_call_later

_LOGGER = logging.getLogger(__name__)

_LOGGER = logging.getLogger(__name__)

class UpdateCoordinator:
    def __init__(self, hass, api_key, vin, authorization, sign, update_interval=60):
        self.hass = hass
        self._api_key = api_key
        self._vin = vin
        self._authorization = authorization
        self._sign = sign
        self._update_interval = update_interval
        self._data = None
        self._is_running = True
        self._listeners: List[Callable] = []  # 监听器列表
        self._unsub_timer = None  # 用于存储取消定时任务的句柄
        self._max_retries = 5

    def async_add_listener(self, listener: Callable):
        """添加更新监听器。"""
        self._listeners.append(listener)

    async def _notify_listeners(self):
        """通知所有监听器更新数据。"""
        for listener in self._listeners:
            await listener()

    @property
    def data(self):
        """返回最新的车辆状态数据。"""
        return self._data

    async def fetch_vehicle_status(self):
        """执行 API 调用以获取车辆状态。"""
        retries = 0
        url = "https://appapi-pki.chehezhi.cn:18443/pivot/veh-status/vehicle-status-control/1.0/getAppVehicleData"
        headers = {
            "appId": "HOZON-B-xKrgEvMt",
            "Authorization": f"Bearer {self._authorization}",
            "channel": "iOS",
            "nonce": "3846904368",
            "timestamp": str(int(time.time() * 1000)),
            "appVersion": "6.4.2",
            "login_channel": "1",
            "User-Agent": "CHZ/6.4.2 (com.hozon.sales.app; build:1; iOS 17.7.1) Alamofire/5.4.4",
            "appKey": self._api_key,
            "sign": self._sign,
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        }
        data = {"types": "", "vin": self._vin}

        while retries < self._max_retries:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        json_data = await response.json()

                        if json_data.get("code") == 20000:
                            return json_data.get("data", {})
                        else:
                            _LOGGER.error(
                                "API Error: code=%s, description=%s, full_response=%s",
                                json_data.get("code"),
                                json_data.get("description", "No description"),
                                json_data,
                            )
                            await self.handle_error("Token已过期，需要重新配置")
                            return None
            except aiohttp.ClientError as e:
                _LOGGER.error("Client error fetching vehicle data: %s", e)
            except asyncio.TimeoutError:
                _LOGGER.error("Request timeout fetching vehicle data.")
            except Exception as e:
                _LOGGER.error("Unexpected error: %s", e)

            retries += 1
            _LOGGER.info("Retrying... Attempt %d of %d", retries, self._max_retries)
            await asyncio.sleep(self._update_interval / self._max_retries)

        await self.handle_error("API 请求失败，请检查网络或配置")
        return None

    async def handle_error(self, message):
        """处理 API 错误并发送通知。"""
        self._is_running = False
        self.hass.components.persistent_notification.create(
            f"{message}。", title="车辆状态集成错误", notification_id="neta_vehicle_status_error"
        )

    async def start(self):
        """开始定期更新数据。"""
        self._is_running = True

        # 立即触发第一次数据更新
        await self.update_data()

        # 注册定时任务并保存取消句柄
        self._unsub_timer = async_track_time_interval(
            self.hass, self.update_data, timedelta(seconds=self._update_interval)
        )

    async def stop(self):
        """停止定期更新任务并清理资源。"""
        self._is_running = False
        if self._unsub_timer:
            self._unsub_timer()  # 取消定时任务
            self._unsub_timer = None
        _LOGGER.debug("UpdateCoordinator stopped.")

    async def update_data(self, now=None):
        """定期更新数据。"""
        if not self._is_running:
            return
        _LOGGER.debug("Fetching vehicle data from API...")
        self._data = await self.fetch_vehicle_status()
        await self._notify_listeners()

