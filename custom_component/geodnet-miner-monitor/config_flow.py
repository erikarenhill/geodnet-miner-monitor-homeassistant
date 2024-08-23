class GeodnetConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Geodnet."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY]
            ip_address = user_input[CONF_IP_ADDRESS]
            
            # Validate API key format
            if not self.is_valid_api_key(api_key):
                errors[CONF_API_KEY] = "invalid_api_key_format"
            # Validate IP address format
            elif not self.is_valid_ip_address(ip_address):
                errors[CONF_IP_ADDRESS] = "invalid_ip_address_format"
            else:
                # Test the connection
                if not await self.test_connection(ip_address, api_key):
                    errors["base"] = "cannot_connect"
                else:
                    # Create a title that includes the API key and IP address
                    title = f"Geodnet ({api_key} - {ip_address})"
                    
                    # Check if an entry with this API key already exists
                    await self.async_set_unique_id(api_key)
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY): vol.All(str, vol.Length(5)),
                vol.Required(CONF_IP_ADDRESS): str,
            }),
            errors=errors,
        )

    @staticmethod
    def is_valid_api_key(api_key):
        """Check if the API key is valid (5 characters, digits and letters)."""
        return len(api_key) == 5 and api_key.isalnum()

    @staticmethod
    def is_valid_ip_address(ip_address):
        """Check if the IP address is valid."""
        parts = ip_address.split('.')
        if len(parts) != 4:
            return False
        return all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)

    async def test_connection(self, ip_address, api_key):
        """Test if we can connect to the Geodnet server."""
        try:
            session = async_get_clientsession(self.hass)
            async with async_timeout.timeout(10):
                response = await session.get(f"http://{ip_address}:3000/api/listen?key={api_key}")
                return response.status == 200
        except (asyncio.TimeoutError, aiohttp.ClientError):
            return False