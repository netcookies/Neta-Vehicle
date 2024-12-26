import time
import logging
from homeassistant import config_entries, core
from homeassistant.helpers import discovery
from homeassistant.const import Platform
from homeassistant.core import ServiceCall
from .update_coordinator import UpdateCoordinator
from .config_flow import NetaVehicleStatusConfigFlow
from .const import (
    DOMAIN,
    CONF_VIN,
    CONF_SIGN,
    CONF_NAME,
    CONF_API_KEY,
    CONF_AUTHORIZATION,
    CONF_UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]

async def signin_service(authorization, call: ServiceCall):
    """Call the signin service."""
    token = call.data.get("token", authorization)
    url = "https://appapi-pki.chehezhi.cn:18443/hznz/customer/sign"
    headers = {
        "appId": "HOZON-B-xKrgEvMt",
        "Authorization": f"Bearer {token}",
        "channel": "iOS",
        "nonce": "3846904368",
        "timestamp": str(int(time.time() * 1000)),
        "appVersion": "6.4.2",
        "login_channel": "1",
        "User-Agent": "CHZ/6.4.2 (com.hozon.sales.app; build:1; iOS 17.7.1) Alamofire/5.4.4",
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, data=data) as response:
                response.raise_for_status()
                json_data = await response.json()
                if json_data.get("code") == 200:
                    return json_data.get("data", {})
                else:
                    _LOGGER.error(
                        "API Error: code=%s, description=%s, full_response=%s",
                        json_data.get("code"),
                        json_data.get("description", "No description"),
                        json_data,
                    )
                    return None
    except aiohttp.ClientError as e:
        _LOGGER.error("Client error fetching vehicle data: %s", e)
    except asyncio.TimeoutError:
        _LOGGER.error("Request timeout fetching vehicle data.")
    except Exception as e:
        _LOGGER.error("Unexpected error: %s", e)

async def async_setup_entry(hass: core.HomeAssistant, entry: config_entries.ConfigEntry):
    """Set up Neta Vehicle Status from a config entry."""
    _LOGGER.debug("Setting up Neta Vehicle Status for entry: %s", entry)

    hass.data.setdefault(DOMAIN, {})

    api_key = entry.data.get(CONF_API_KEY)
    vin = entry.data.get(CONF_VIN)
    authorization = entry.data.get(CONF_AUTHORIZATION)
    sign = entry.data.get(CONF_SIGN)
    name = entry.data.get(CONF_NAME, "Neta Vehicle Status")
    update_interval = entry.data.get(CONF_UPDATE_INTERVAL, 60)

    async def signin_service_wrapper(call: ServiceCall):
        await signin_service(authorization, call)

    # 注册自定义服务
    hass.services.async_register( DOMAIN, "signin", signin_service_wrapper)
    _LOGGER.debug("Action of Neta Vehicle regeisted.")

    # 创建 UpdateCoordinator 实例
    coordinator = UpdateCoordinator(hass, api_key, vin, authorization, sign, update_interval)
    hass.data[DOMAIN][entry.entry_id] = coordinator
    _LOGGER.debug("coordinator regeisted.")

    await coordinator.start()

    # Load the sensor platform with the updated config
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.debug("Successfully set up config entry for %s", entry.title)

    return True

async def async_unload_entry(hass: core.HomeAssistant, entry: config_entries.ConfigEntry):
    """Unload a config entry."""
    _LOGGER.debug("Unloading Neta Vehicle Status for entry: %s", entry)

    # 停止协调器
    coordinator = hass.data[DOMAIN].pop(entry.entry_id)
    await coordinator.stop()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    return unload_ok

async def async_reload_entry(hass: core.HomeAssistant, entry: config_entries.ConfigEntry):
    """Handle config changes and reload entry."""
    _LOGGER.debug("Reloading Neta Vehicle Status for entry: %s", entry)

    # 取消注册服务
    hass.services.async_remove(DOMAIN, "signin")

    # Unload the current platform first
    await async_unload_entry(hass, entry)

    # Reload the platform with new config data
    return await async_setup_entry(hass, entry)

