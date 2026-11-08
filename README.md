# MS Home Assistant Bridge

Home Assistant custom integration that exposes a small API for the MS ChatGPT MCP server.

## Install

1. Copy `custom_components/ms_smart_home_bridge` into your Home Assistant `config/custom_components/` directory, or publish this repository and install it through HACS as a custom repository.
2. Restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration**.
4. Search for **MS Smart Home Bridge**.
5. Create a strong bridge key when prompted. Save it securely; the MCP server needs the same key.

API endpoints (authenticated with `X-Bridge-Key`):

- `GET /api/ms_smart_home_bridge/states`
- `POST /api/ms_smart_home_bridge/service`

The service endpoint only permits a limited set of domains and services. This is an initial starter allowlist; review it before deploying.

## Security

Do not expose port 8123 directly. For remote access, use a properly secured HTTPS reverse proxy or tunnel. Keep the bridge key private and do not commit it to GitHub.
