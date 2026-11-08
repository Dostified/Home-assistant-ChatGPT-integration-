from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, CONF_BRIDGE_KEY

ALLOWED_DOMAINS = {"light", "switch", "fan", "climate", "cover", "scene", "sensor", "binary_sensor"}
ALLOWED_SERVICES = {
    "light": {"turn_on", "turn_off", "toggle"},
    "switch": {"turn_on", "turn_off", "toggle"},
    "fan": {"turn_on", "turn_off", "toggle", "set_percentage"},
    "climate": {"set_temperature", "set_hvac_mode", "turn_on", "turn_off"},
    "cover": {"open_cover", "close_cover", "stop_cover"},
    "scene": {"turn_on"},
}

class BridgeStatesView(HomeAssistantView):
    url = "/api/ms_smart_home_bridge/states"
    name = "api:ms_smart_home_bridge:states"
    requires_auth = False

    def __init__(self, hass, bridge_key):
        self.hass = hass
        self.bridge_key = bridge_key

    def _authorized(self, request):
        return request.headers.get("X-Bridge-Key", "") == self.bridge_key

    async def get(self, request):
        from aiohttp import web
        if not self._authorized(request):
            return web.json_response({"error": "unauthorized"}, status=401)
        states = []
        for state in self.hass.states.async_all():
            domain = state.entity_id.split(".", 1)[0]
            if domain in ALLOWED_DOMAINS:
                states.append({
                    "entity_id": state.entity_id,
                    "state": state.state,
                    "attributes": dict(state.attributes),
                })
        return web.json_response(states)


class BridgeServiceView(HomeAssistantView):
    url = "/api/ms_smart_home_bridge/service"
    name = "api:ms_smart_home_bridge:service"
    requires_auth = False

    def __init__(self, hass, bridge_key):
        self.hass = hass
        self.bridge_key = bridge_key

    async def post(self, request):
        from aiohttp import web
        if request.headers.get("X-Bridge-Key", "") != self.bridge_key:
            return web.json_response({"error": "unauthorized"}, status=401)
        try:
            data = await request.json()
            domain = str(data.get("domain", ""))
            service = str(data.get("service", ""))
            entity_id = str(data.get("entity_id", ""))
            service_data = data.get("service_data", {})
            if domain not in ALLOWED_SERVICES or service not in ALLOWED_SERVICES[domain]:
                return web.json_response({"error": "service not allowed"}, status=403)
            if not entity_id.startswith(domain + "."):
                return web.json_response({"error": "entity/domain mismatch"}, status=400)
            if not self.hass.states.get(entity_id):
                return web.json_response({"error": "entity not found"}, status=404)
            if not isinstance(service_data, dict):
                return web.json_response({"error": "service_data must be an object"}, status=400)
            await self.hass.services.async_call(
                domain, service, {"entity_id": entity_id, **service_data}, blocking=True
            )
            return web.json_response({"ok": True, "entity_id": entity_id, "service": service})
        except Exception as err:
            return web.json_response({"error": str(err)}, status=400)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    bridge_key = entry.data[CONF_BRIDGE_KEY]
    hass.http.register_view(BridgeStatesView(hass, bridge_key))
    hass.http.register_view(BridgeServiceView(hass, bridge_key))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Home Assistant's HTTP view registry does not provide a simple per-entry
    # unregister API. Restart HA after removing this integration to remove routes.
    return True
