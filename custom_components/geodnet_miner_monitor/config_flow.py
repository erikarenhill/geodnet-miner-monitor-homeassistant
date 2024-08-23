import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
import aiohttp
import asyncio
from urllib.parse import urlparse

from .const import DOMAIN, CONF_SERIAL_NUMBER, CONF_API_URL

class GeodnetMinerMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Geodnet Miner Monitor."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        # Define default values and placeholders
        defaults = {
            CONF_SERIAL_NUMBER: "",
            CONF_API_URL: "http://",
        }

        if user_input is not None:
            serial_number = user_input[CONF_SERIAL_NUMBER]
            api_url = user_input[CONF_API_URL]
            
            # Validate serial number format
            if not self._is_valid_serial_number(serial_number):
                errors[CONF_SERIAL_NUMBER] = "invalid_serial_number_format"
            # Validate API URL format
            elif not self._is_valid_url(api_url):
                errors[CONF_API_URL] = "invalid_api_url_format"
            else:
                # Test the connection
                connection_result = await self._test_connection(api_url, serial_number)
                if not connection_result['success']:
                    errors["base"] = f"cannot_connect: {connection_result['error']}"
                else:
                    # Create a title that includes the serial number and API URL
                    title = f"Geodnet Miner ({serial_number} - {api_url})"
                    
                    # Check if an entry with this serial number already exists
                    await self.async_set_unique_id(serial_number)
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_SERIAL_NUMBER, default=defaults[CONF_SERIAL_NUMBER]): cv.string,
                vol.Required(CONF_API_URL, default=defaults[CONF_API_URL]): cv.string,
            }),
            errors=errors,
        )

    @staticmethod
    def _is_valid_serial_number(serial_number: str) -> bool:
        """Check if the serial number is valid (last 5 characters, digits and letters)."""
        return len(serial_number) == 5 and serial_number.isalnum()

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Check if the URL is valid and starts with http:// or https://."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except ValueError:
            return False

    async def _test_connection(self, api_url: str, serial_number: str) -> dict:
        """Test if we can connect to the Geodnet server."""
        try:
            session = async_get_clientsession(self.hass)
            url = f"{api_url}/api/listen?key={serial_number}"
            
            async with asyncio.timeout(10):
                async with session.get(url) as response:
                    if response.status == 200:
                        return {"success": True, "error": None}
                    elif response.status == 400:
                        # Check if the error message indicates an already listening browser
                        response_json = await response.json()
                        if response_json.get("error") == "Browser already listening for this key":
                            return {"success": True, "error": None}
                        else:
                            return {"success": False, "error": f"API error: {response_json.get('error', 'Unknown error')}"}
                    else:
                        return {"success": False, "error": f"HTTP error {response.status}"}
        except asyncio.TimeoutError:
            return {"success": False, "error": "Connection timed out"}
        except aiohttp.ClientError as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}