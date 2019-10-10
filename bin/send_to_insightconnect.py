""" Modular Alert for sending a Splunk alert to InsightConnect """

import sys
import json
import os
import re

import logging
import logging.handlers

import requests
import splunk


def setup_logging():
    """ Configures logging """
    logger = logging.getLogger("send_to_insightconnect")
    splunk_home = os.environ["SPLUNK_HOME"]

    logging_default_config_file = os.path.join(splunk_home, "etc", "log.cfg")
    logging_local_config_file = os.path.join(splunk_home, "etc", "log-local.cfg")
    logging_stanza_name = "python"
    logging_file_name = "send_to_insightconnect.log"
    base_log_path = os.path.join("var", "log", "splunk")
    logging_format = "%(asctime)s %(levelname)-s\t%(module)s:%(lineno)d - %(message)s"
    splunk_log_handler = logging.handlers.RotatingFileHandler(
        os.path.join(splunk_home, base_log_path, logging_file_name), mode="a")
    splunk_log_handler.setFormatter(logging.Formatter(logging_format))
    logger.addHandler(splunk_log_handler)
    splunk.setupSplunkLogger(logger, logging_default_config_file, logging_local_config_file, logging_stanza_name)

    return logger


class SendToInsightConnectAlert:
    """ Sends an alert to InsightConnect """

    def __init__(self, trigger_url, api_key, event):
        """
        Initialize a SendToInsightConnectAlert
        :param trigger_url: API Trigger URL for workflow within Rapid7 InsightConnect
        :param api_key: X-API-Key for Insight platform
        :param event: Splunk event being alerted on
        """
        self.trigger_url = trigger_url
        self.api_key = api_key
        self.event = event

        self.logger = setup_logging()

    @classmethod
    def from_cli(cls):
        """
        Initializes a SendToInsightConnectAlert object from CLI via stdin
        :return: SendToInsightConnectAlert instance
        """

        try:
            # Receive Splunk event
            event = json.load(sys.stdin)

            # Remove the configuration from the event - it can contain sensitive info that
            # we don't want to send to the InsightConnect workflow
            config = event.pop("configuration")

            # Pull out both the InsightConnect workflow trigger URL as well as the Insight platform API key
            trigger_url = config["trigger_url"]
            api_key = config["x-api-key"]

            # Write the event back out to a JSON string
            j_event = json.dumps(event)

        except KeyError:
            raise Exception("Error: Either 'trigger URL' or 'x-api-key' was missing!")
        except ValueError:
            raise Exception("Error: An invalid JSON string was received!")

        return cls(trigger_url=trigger_url, api_key=api_key, event=j_event)

    def run(self):
        """
        Runs the Alert action
        :return: None
        """

        if not self.trigger_url:
            s = "Error: Missing Rapid7 InsightConnect Workflow API trigger URL!"
            self.logger.error(s)
            raise Exception(s)

        if not self._is_workflow_trigger_url_valid(trigger_url=self.trigger_url):
            s = "Error: Invalid Rapid7 InsightConnect Workflow API trigger URL!"
            self.logger.error(s)
            raise Exception(s)

        if not self.api_key:
            s = "Error: Missing Rapid7 Insight platform API key! If you need an API key, one can be created at " \
                "https://insight.rapid7.com/platform#/apiKeyManagement"
            self.logger.error(s)
            raise Exception(s)

        # Both required inputs are present and valid, so proceed with the alert
        self.logger.info("Sending alert to Rapid7 InsightConnect!")

        self._send_alert(url=self.trigger_url,
                         api_key=self.api_key,
                         alert=self.event)

    def _is_workflow_trigger_url_valid(self, trigger_url):
        """
        Checks if a Rapid7 InsightConnect workflow trigger URL is valid based on a known schema as of 10/10/19
        :param trigger_url: Workflow trigger URL to validate
        :return: Boolean value indicating if the URL is valid (true) or invalid (false)
        """

        # Regex pattern, matches something like:
        # https://us.api.insight.rapid7.com/connect/v1/workflows/16b3-z81b-40b7-afc2-zf53127d3758/events/execute
        rp = r"https:\/\/.{2}\.api\.insight\.rapid7\.com\/connect\/v\d{1}\/workflows\/[a-zA-Z0-9\-]*\/events\/execute"
        matches = re.match(rp, trigger_url)

        if matches:
            return True
        else:
            return False

    def _send_alert(self, url, api_key, alert):
        """
        Sends a Splunk alert to Rapid7 InsightConnect
        :param url: Rapid7 InsightConnect Workflow URL
        :param api_key: Rapid7 Insight platform API Key (used for the X-Api-Key POST header)
        :param alert: The Splunk alert to send
        :return: None
        """

        # URL will always be HTTPS as that is the only option with the Rapid7 Insight platform
        # and regex validation is performed to ensure the URL schema is proper.
        response = requests.post(url, alert, headers={"X-Api-Key": api_key})

        # Documented Rapid7 InsightConnect API status codes
        messages = {
            400: "Inactive Rapid7 InsightConnect workflow!",
            404: "Rapid7 InsightConnect workflow version not found!",
            500: "An error occurred within Rapid7 InsightConnect!"
        }

        error_message = messages.get(response.status_code)
        if error_message:
            s = "Error: %s. \nResponse was: %s" % (error_message, response.text)
            self.logger.error(s)
            raise Exception(s)

        self.logger.info("Successfully sent alert to Rapid7 InsightConnect!")


if __name__ == "__main__":
    if not (len(sys.argv) > 1 and sys.argv[1] == "--execute"):
        raise Exception("Unsupported execution mode (expected --execute flag)")

    try:
        modular_alert = SendToInsightConnectAlert.from_cli()
        modular_alert.run()
        sys.exit(0)
    except Exception as e:
        raise Exception("An error occurred while running the alert. Information about the error: %s" % str(e))
