from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from .const import (
    DOMAIN,
    CONF_VIN,
    CONF_SIGN,
    CONF_NAME,
    CONF_API_KEY,
    CONF_AUTHORIZATION,
    CONF_UPDATE_INTERVAL,
    DEFAULT_SIGN,
    DEFAULT_API_KEY,
)

class NetaVehicleStatusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Neta Vehicle Status."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=self.get_schema())

        # 获取现有配置条目
        existing_entry = await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        # 强制设置不可更改的字段
        user_input[CONF_API_KEY] = DEFAULT_API_KEY  # 锁定API_KEY为默认值
        user_input[CONF_SIGN] = DEFAULT_SIGN  # 锁定SIGN为默认值

        # 更新现有条目的数据
        if existing_entry:
            self.hass.config_entries.async_update_entry(
                existing_entry, data=user_input
            )
            await self.hass.config_entries.async_reload(existing_entry.entry_id)  # 重新加载条目
            return self.async_abort(reason="reconfigured")

        # 如果不存在现有条目，则创建新的条目
        return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

    def get_schema(self, current_data=None):
        """获取配置表单的架构，并在修改时填充现有值。"""
        if current_data is None:
            current_data = {}

        return vol.Schema(
            {
                vol.Optional(CONF_NAME, default=current_data.get(CONF_NAME, "Neta Vehicle Status")): str,
                vol.Required(CONF_VIN, default=current_data.get(CONF_VIN, "")): str,
                vol.Required(CONF_AUTHORIZATION, default=current_data.get(CONF_AUTHORIZATION, "")): str,
                vol.Optional(CONF_UPDATE_INTERVAL, default=current_data.get(CONF_UPDATE_INTERVAL, 60)): vol.All(vol.Coerce(int), vol.Range(min=10)),
                #vol.Optional(CONF_API_KEY, default=current_data.get(CONF_API_KEY, DEFAULT_API_KEY)): str,
                #vol.Optional(CONF_SIGN, default=current_data.get(CONF_SIGN, DEFAULT_SIGN)): str,
            }
        )

    async def async_step_reconfigure(self, user_input=None):
        """处理重新配置的步骤。"""
        # 获取当前条目
        current_entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])

        if user_input is None:
            # 用现有条目数据填充默认值
            return self.async_show_form(
                step_id="reconfigure",
                data_schema=self.get_schema(current_entry.data)
            )

        # 强制设置不可更改的字段
        user_input[CONF_API_KEY] = DEFAULT_API_KEY  # 锁定 API_KEY 为默认值
        user_input[CONF_SIGN] = DEFAULT_SIGN  # 锁定 SIGN 为默认值

        # 更新现有配置条目
        self.hass.config_entries.async_update_entry(current_entry, data=user_input)

        # 调用重新加载条目逻辑
        await self.hass.config_entries.async_reload(current_entry.entry_id)

        return self.async_abort(reason="reconfigured")

