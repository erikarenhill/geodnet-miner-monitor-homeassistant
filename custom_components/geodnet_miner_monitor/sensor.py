
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import PERCENTAGE, SIGNAL_STRENGTH_DECIBELS, DATA_KILOBYTES
from .const import CONF_SERIAL_NUMBER
from homeassistant.helpers.entity import Entity
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up Geodnet sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    api_key = entry.data[CONF_SERIAL_NUMBER]

    sensors = [
        GeodnetSensor(coordinator, "effective_satellites", api_key),
        GeodnetDataSensor(coordinator, "dataByte", api_key),
        #GeodnetSensor(coordinator, "total_satellites", api_key),
        GeodnetSatelliteInfoSensor(coordinator, api_key),
        GeodnetHourlySensor(coordinator, "satRate", api_key),
        GeodnetHourlySensor(coordinator, "onLineRate", api_key),
    ]

    async_add_entities(sensors)

class GeodnetSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Geodnet sensor."""

    def __init__(self, coordinator, sensor_type, api_key):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._api_key = api_key
        self._attr_name = f"geodnet_{api_key}_{sensor_type}"
        self._attr_unique_id = f"{DOMAIN}_{api_key}_{sensor_type}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._sensor_type)


    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._api_key)},
            "name": f"Geodnet Miner {self._api_key}",
            "manufacturer": "Hyfix",
            "model": "MobileCM",
        }

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        if self._sensor_type == "dataByte":
            return DATA_KILOBYTES
        return ""


class GeodnetDataSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Geodnet sensor."""

    def __init__(self, coordinator, sensor_type, api_key):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._api_key = api_key
        self._attr_name = f"geodnet_{api_key}_{sensor_type}"
        self._attr_unique_id = f"{DOMAIN}_{api_key}_{sensor_type}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._sensor_type)


    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._api_key)},
            "name": f"Geodnet Miner {self._api_key}",
            "manufacturer": "Hyfix",
            "model": "MobileCM",
        }

    @property
    def unit_of_measurement(self):
        return DATA_KILOBYTES


class GeodnetSatelliteInfoSensor(CoordinatorEntity, Entity):
    """Representation of a Geodnet satellite info sensor."""

    def __init__(self, coordinator, api_key):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._api_key = api_key
        self._attr_name = f"geodnet_{api_key}_satellites"
        self._attr_unique_id = f"{DOMAIN}_{api_key}_satellites"
        self._attr_device_class = "signal_strength"
        self._attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS

    # @property
    # def native_value(self):
    #     """Return the state of the sensor."""
    #     # Return the average SNR of all satellites
    #     sat_info = self.coordinator.data.get("satInfo", [])
    #     if sat_info:
    #         return sum(sat['snr'] for sat in sat_info) / len(sat_info)
    #     return None

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("total_satellites")

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            sat['sys_channel']: sat['snr']
            for sat in self.coordinator.data.get("satInfo", [])
        }

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._api_key)},
            "name": f"Geodnet Miner {self._api_key}",
            "manufacturer": "Hyfix",
            "model": "MobileCM",
        }

class GeodnetHourlySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Geodnet hourly sensor."""

    def __init__(self, coordinator, sensor_type, api_key):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._api_key = api_key
        self._attr_name = f"geodnet_{api_key}_{sensor_type}"
        self._attr_unique_id = f"{DOMAIN}_{api_key}_{sensor_type}"

    @property
    def state(self):
        """Return the state of the sensor."""
        hourly_data = self.coordinator.get_current_hourly_data()
        return hourly_data.get(self._sensor_type)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return PERCENTAGE

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        hourly_data = self.coordinator.get_current_hourly_data()
        return {
            "timestamp": hourly_data.get("timestamp"),
        }

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._api_key)},
            "name": f"Geodnet Miner {self._api_key}",
            "manufacturer": "Hyfix",
            "model": "MobileCM",
        }