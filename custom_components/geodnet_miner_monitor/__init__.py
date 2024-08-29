import asyncio
import logging
from datetime import timedelta
from typing import Any, Dict

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS
from .const import CONF_SERIAL_NUMBER, CONF_API_URL
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Geodnet component."""
    hass.data[DOMAIN] = {}
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Geodnet from a config entry."""
    api_key = entry.data[CONF_SERIAL_NUMBER]
    ip_address = entry.data[CONF_API_URL]
    
    session = async_get_clientsession(hass)
    
    # Make the initial request to /api/listen
    try:
        async with async_timeout.timeout(10):
            await session.get(f"{ip_address}/api/listen?key={api_key}")
    except (asyncio.TimeoutError, aiohttp.ClientError) as err:
        _LOGGER.error(f"Error making initial request to /api/listen: {err}")
        return False
    
    # Wait for 10 seconds
    await asyncio.sleep(10)
    
    coordinator = GeodnetCoordinator(hass, api_key, ip_address)
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Register the device
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, api_key)},
        name=f"Geodnet Miner {api_key}",
        manufacturer="Hyfix",
        model="MobileCM",
    )

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

class GeodnetCoordinator(DataUpdateCoordinator):
    """Geodnet coordinator."""

    def __init__(self, hass, api_key, ip_address):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Geodnet",
            update_interval=timedelta(minutes=1),
        )
        self.api_key = api_key
        self.ip_address = ip_address
        self.session = async_get_clientsession(hass)


    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from API endpoint."""
        try:
            async with async_timeout.timeout(45):
                response = await self.session.get(f"{self.ip_address}/api/stats?key={self.api_key}&autostart=true")
                response.raise_for_status()
                data = await response.json()
                
                # Check if the response indicates bad/no data
                if data == {"effective_satellites":0, "satInfo":[], "hourlyData":None}:
                    _LOGGER.warning("Received bad/no data from the Geodnet API. Using default values.")
                    return self._get_default_data()
                
                # Process hourly data
                self.hourly_data = data.get('hourlyData', [])
                
                return data
        except asyncio.TimeoutError as err:
            raise UpdateFailed("Timeout error") from err
        except aiohttp.ClientResponseError as err:
            if err.status == 401:
                raise ConfigEntryAuthFailed("Invalid API key") from err
            raise UpdateFailed(f"Error response from API: {err}") from err
        except (aiohttp.ClientError, aiohttp.ServerDisconnectedError) as err:
            raise UpdateFailed(f"Error while fetching data: {err}") from err

    def _get_default_data(self) -> Dict[str, Any]:
        """Return default data when the API returns bad/no data."""
        return {
            "total_satellites": 0,
            "effective_satellites": 0,
            "last_packet_time": "0",
            "dataByte": 0,
            "latency": 0,
            "satInfo": [],
            "hourlyData": []
        }

    def get_current_hourly_data(self) -> Dict[str, Any]:
        """Get the most recent hourly data."""
        if not self.hourly_data:
            return {}
        return max(self.hourly_data, key=lambda x: x['timestamp'])

    async def async_close(self) -> None:
        """Close the aiohttp ClientSession."""
        if self.session:
            await self.session.close()