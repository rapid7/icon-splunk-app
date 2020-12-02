# encoding = utf-8

import json
import re

import requests


class SendToInsightConnectAlert:
    """ Sends an alert to InsightConnect """

    def __init__(self, trigger_url, api_key, event, helper):
        """
        Initialize a SendToInsightConnectAlert
        :param trigger_url: API Trigger URL for workflow within Rapid7 InsightConnect
        :param api_key: X-API-Key for Insight platform
        :param event: Splunk event being alerted on
        """
        self.trigger_url = trigger_url
        self.api_key = api_key
        self.event = event
        self.helper = helper

    @classmethod
    def from_cli(cls, helper):
        """
        Initializes a SendToInsightConnectAlert object from CLI via stdin
        :return: SendToInsightConnectAlert instance
        """

        try:
            api_key = helper.get_global_setting("rapid7_insight_api_key")
            trigger_url = helper.get_param("workflow_trigger_url")
            j_event = cls._create_payload(helper=helper)

        except KeyError:
            raise Exception("Error: Either 'trigger URL' or 'x-api-key' was missing!")
        except ValueError:
            raise Exception("Error: An invalid JSON string was received!")

        return cls(trigger_url=trigger_url, api_key=api_key, event=j_event, helper=helper)

    def run(self):
        """
        Runs the Alert action
        :return: None
        """

        if not self.trigger_url:
            s = "Error: Missing Rapid7 InsightConnect Workflow API trigger URL!"
            self.helper.log_error(s)
            raise Exception(s)

        if not self._is_workflow_trigger_url_valid(trigger_url=self.trigger_url):
            s = "Error: Invalid Rapid7 InsightConnect Workflow API trigger URL!"
            self.helper.log_error(s)
            raise Exception(s)

        if not self.api_key:
            s = "Error: Missing Rapid7 Insight platform API key! If you need an API key, one can be created at " \
                "https://insight.rapid7.com/platform#/apiKeyManagement"
            self.helper.log_error(s)
            raise Exception(s)

        # Both required inputs are present and valid, so proceed with the alert
        self.helper.log_info("Sending alert to Rapid7 InsightConnect!")

        self._send_alert(url=self.trigger_url,
                         api_key=self.api_key,
                         alert=self.event)

    @staticmethod
    def _create_payload(helper):
        """
        Creates a payload to send to Rapid7 InsightConnect
        :param helper: Splunk helper
        :return: Payload
        """
        return json.dumps({"events": [dict(event) for event in helper.get_events()]})


    def _is_workflow_trigger_url_valid(self, trigger_url):
        """
        Checks if a Rapid7 InsightConnect workflow trigger URL is valid based on a known schema as of 10/10/19
        :param trigger_url: Workflow trigger URL to validate
        :return: Boolean value indicating if the URL is valid (true) or invalid (false)
        """

        # Regex pattern, matches something like:
        # https://us.api.insight.rapid7.com/connect/v1/workflows/16b3-z81b-40b7-afc2-zf53127d3758/events/execute
        # OR, the new style async URL:
        # https://us.api.insight.rapid7.com/connect/v1/execute/async/workflows/c3b886da-b345-7abe-cda3-c96173c93de1
        rp = r"https:\/\/.{2}\.api\.insight\.rapid7\.com\/connect\/v\d{1}\/workflows\/[a-zA-Z0-9\-]*\/events\/execute" \
             r"|https:\/\/.{2}\.api\.insight\.rapid7\.com\/connect\/v\d{1}\/execute\/async\/workflows\/[a-zA-Z0-9\-]*"
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
        if response.status_code != 200:
            s = "An error occurred! Response was: %s" % response.text
            self.helper.log_error(s)
            raise Exception(s)

        self.helper.log_info("Successfully sent alert to Rapid7 InsightConnect!")


def process_event(helper, *args, **kwargs):
    """
    # IMPORTANT
    # Do not remove the anchor macro:start and macro:end lines.
    # These lines are used to generate sample code. If they are
    # removed, the sample code will not be updated when configurations
    # are updated.

    [sample_code_macro:start]

    # The following example gets account information
    user_account = helper.get_user_credential("<account_name>")

    # The following example gets the setup parameters and prints them to the log
    rapid7_insight_api_key = helper.get_global_setting("rapid7_insight_api_key")
    helper.log_info("rapid7_insight_api_key={}".format(rapid7_insight_api_key))

    # The following example gets the alert action parameters and prints them to the log
    workflow_trigger_url = helper.get_param("workflow_trigger_url")
    helper.log_info("workflow_trigger_url={}".format(workflow_trigger_url))


    # The following example adds two sample events ("hello", "world")
    # and writes them to Splunk
    # NOTE: Call helper.writeevents() only once after all events
    # have been added
    helper.addevent("hello", sourcetype="sample_sourcetype")
    helper.addevent("world", sourcetype="sample_sourcetype")
    helper.writeevents(index="summary", host="localhost", source="localhost")

    # The following example gets the events that trigger the alert
    events = helper.get_events()
    for event in events:
        helper.log_info("event={}".format(event))

    # helper.settings is a dict that includes environment configuration
    # Example usage: helper.settings["server_uri"]
    helper.log_info("server_uri={}".format(helper.settings["server_uri"]))
    [sample_code_macro:end]
    """

    helper.log_info("Alert action send_to_rapid7_insightconnect started.")

    try:
        modular_alert = SendToInsightConnectAlert.from_cli(helper=helper)
        modular_alert.run()
        return 0
    except Exception as e:
        raise Exception("An error occurred while running the alert. Information about the error: %s" % str(e))
