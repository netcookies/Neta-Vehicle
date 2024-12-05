import logging
from homeassistant import config_entries, core
from homeassistant.helpers import discovery
from homeassistant.const import Platform
from .update_coordinator import UpdateCoordinator
from .config_flow import NetaVehicleStatusConfigFlow

_LOGGER = logging.getLogger(__name__)

DOMAIN = "neta_vehicle_status"
CONF_API_KEY = "api_key"
CONF_VIN = "vin"
CONF_AUTHORIZATION = "authorization"
CONF_SIGN = "sign"
CONF_NAME = "name"
CONF_UPDATE_INTERVAL = "update_interval"

PLATFORMS = [Platform.SENSOR]

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

    # 创建 UpdateCoordinator 实例
    coordinator = UpdateCoordinator(hass, api_key, vin, authorization, sign, update_interval)
    hass.data[DOMAIN][entry.entry_id] = coordinator

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

    # Unload the current platform first
    await async_unload_entry(hass, entry)

    # Reload the platform with new config data
    return await async_setup_entry(hass, entry)

