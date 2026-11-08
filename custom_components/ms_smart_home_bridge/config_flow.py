import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_BRIDGE_KEY

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            key = user_input[CONF_BRIDGE_KEY].strip()
            if len(key) < 24:
                errors["base"] = "key_too_short"
            else:
                await self.async_set_unique_id("ms_smart_home_bridge")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="MS Smart Home Bridge",
                    data={CONF_BRIDGE_KEY: key},
                )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_BRIDGE_KEY): str,
            }),
            errors=errors,
            description_placeholders={
                "hint": "Create a random key of at least 24 characters and store it securely."
            },
        )
