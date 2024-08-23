# Geodnet Integration for Home Assistant

This custom integration allows you to integrate Geodnet miners into your Home Assistant instance.

## Prerequisites

Before installing this integration, you need to set up the Geodnet Headless Console API. This API is required for the integration to function properly.

1. Visit the [Geodnet Headless Console API repository](https://github.com/erikarenhill/geodnet-headless-console-api/).
2. Follow the instructions in the repository to set up and run the Docker server for the API.
3. Make note of the IP address where the API server is running, as you'll need this during the integration setup.

## Installation

### HACS (Recommended)

1. Ensure that [HACS](https://hacs.xyz/) is installed.
2. Add this repository as a custom repository in HACS:
   - In HACS, click on the three dots in the top right corner and select "Custom repositories".
   - Enter the URL of this repository: `https://github.com/erikarenhill/geodnet-miner-monitor-homeassistant`
   - Select "Integration" as the category.
   - Click "Add".
3. Search for "Geodnet" in the HACS "Integrations" tab.
4. Install the Geodnet integration.
5. Restart Home Assistant.

### Manual Installation

1. Copy the `custom_components/geodnet-miner-monitor` folder from this repository into your `custom_components` directory.
2. Restart Home Assistant.

## Configuration

1. In the Home Assistant UI, navigate to "Configuration" -> "Integrations".
2. Click the "+" button to add a new integration.
3. Search for "Geodnet" and select it.
4. Enter your Geodnet API key and the IP address of your Geodnet Headless Console API server.
5. Click "Submit" to add the integration.

## Usage

After configuration, the integration will create sensor entities for your Geodnet miner. These sensors will update every minute with the latest data from your miner.

## Support

For issues and feature requests, please use the [GitHub Issues](https://github.com/erikarenhill/geodnet-miner-monitor-homeassistant/issues) page.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.