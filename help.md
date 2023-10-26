# Description

The Rapid7 InsightConnect App for Splunk enables users of both Splunk and Rapid7 InsightConnect to forward events from
their Splunk instances to Rapid7 InsightConnect to trigger workflows.

# Key Features

* Forward events via Splunk alerts to Rapid7 InsightConnect

# Requirements

* Insight API Key (generate one here: https://insight.rapid7.com/platform#/apiKeyManagement)
* Splunk instance
* Rapid7 InsightConnect license

# Documentation

## Setup

### Connection

Directions for configuring the Rapid7 InsightConnect App for Splunk can be
found [here](https://insightconnect.help.rapid7.com/docs/set-up-the-insightconnect-app-for-splunk).

## Technical Details

### Configuration

Directions for configuring the Rapid7 InsightConnect App for Splunk can be
found [here](https://insightconnect.help.rapid7.com/docs/set-up-the-insightconnect-app-for-splunk).

### Contributing

Rapid7 welcomes contributions to the InsightConnect App for Splunk and has designated its repository as open source.
The source code for the repository is licensed with the MIT License.

#### Testing

The easiest way to test the app within Splunk is the following:

1. Compile the app package with `make app`.

2. Install the app within Splunk.

3. Use the following search query to manually trigger the alert, replacing the placeholders within `<>` as needed:
`index="*" | head 2 | sendalert send_to_insightconnect param.trigger_url="https://us.api.insight.rapid7.com/connect/v1/workflows/<workflow ID>/events/execute" param.x-api-key="<API key>"`

### Troubleshooting

* Ensure all required InsightConnect workflows are active.
* Ensure your Insight API key is valid and not misspelled.

# Version History

* 2.0.1 - Patch add-on builder code to fix potential FileNotFoundError | Support new workflow trigger URL style
* 2.0.0 - Update for Splunk Cloud
* 1.0.1 - Add MIT license | Remove statement that could potentially log credentials in an error scenario | Add validation around Rapid7 InsightConnect workflow trigger URL
* 1.0.0 - Initial integration

# Links

## References

* [Splunkbase listing](https://splunkbase.splunk.com/app/4673/)
* [InsightConnect App for Splunk Setup Documentation](https://insightconnect.help.rapid7.com/docs/set-up-the-insightconnect-app-for-splunk).
* [Rapid7](https://www.rapid7.com/)
