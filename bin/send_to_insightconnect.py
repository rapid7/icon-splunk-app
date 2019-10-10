""" Modular Alert for sending a Splunk alert to InsightConnect """

import sys
import json
import os
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
            event = json.load(sys.stdin)
            config = event.pop("configuration")

            trigger_url = config["trigger_url"]
            api_key = config["x-api-key"]

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

        if not self.api_key:
            s = "Error: Missing Rapid7 Insight platform API key! If you need an API key, one can be created at " \
                "https://insight.rapid7.com/platform#/apiKeyManagement"
            self.logger.error(s)
            raise Exception(s)

        self.logger.info("Sending alert to Rapid7 InsightConnect!")

        self._send_alert(url=self.trigger_url,
                         api_key=self.api_key,
                         alert=self.event)

    def _send_alert(self, url, api_key, alert):
        """
        Sends a Splunk alert to Rapid7 InsightConnect
        :param url: Rapid7 InsightConnect Workflow URL
        :param api_key: Rapid7 Insight platform API Key (used for the X-Api-Key POST header)
        :param alert: The Splunk alert to send
        :return: None
        """

        # URL should always use HTTPS as that is the only option with the Rapid7 Insight platform.
        response = requests.post(url, alert, headers={"X-Api-Key": api_key})

        # Documented status codes
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
