# File: custom_components/geodnet/config_flow.py

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY

from .const import DOMAIN

class GeodnetConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Geodnet."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY]
            
            # Validate API key format
            if not self.is_valid_api_key(api_key):
                errors[CONF_API_KEY] = "invalid_api_key_format"
            else:
                # Create a title that includes the entire API key
                title = f"Geodnet ({api_key})"
                
                # Check if an entry with this API key already exists
                await self.async_set_unique_id(api_key)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY): vol.All(str, vol.Length(5))
            }),
            errors=errors,
        )

    @staticmethod
    def is_valid_api_key(api_key):
        """Check if the API key is valid (5 characters, digits and letters)."""
        return len(api_key) == 5 and api_key.isalnum()