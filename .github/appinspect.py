import requests
from requests.auth import HTTPBasicAuth
import logging
import sys
import time
import json
import argparse

# Configure logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class AppInspector(object):

    def __init__(self, username: str, password: str, use_cloud: bool = False):
        self.username = username
        self.password = password
        self.use_cloud = use_cloud

        self.session = None

    @classmethod
    def init_from_ci(cls, username: str, password: str, use_cloud: bool = False):
        return cls(
            username=username,
            password=password,
            use_cloud=use_cloud
        )

    def authenticate(self) -> None:
        uri = "https://api.splunk.com/2.0/rest/login/splunk"
        logger.info(f"Authenticating with Splunk AppInspect...")
        response = requests.get(uri, auth=HTTPBasicAuth(self.username, self.password))

        response.raise_for_status()

        logger.info("Authentication to Splunk AppInspect complete!")
        user_token = response.json().get("data").get("token")

        session = requests.Session()
        session.headers.update({"Authorization": f"bearer {user_token}"})

        self.session = session

    def submit_file(self, spl_path: str) -> str:
        """
        Submits a file to Splunk AppInspect
        :param spl_path: Path to packaged SPL
        :return: AppInspect request ID
        """
        uri = "https://appinspect.splunk.com/v1/app/validate"

        files = {"app_package": open(spl_path, "rb")}

        if self.use_cloud:
            logger.info(f"Submitting {spl_path} to Splunk Cloud AppInspect...")
            response = self.session.post(uri, files=files, data={"included_tags": "cloud"})
        else:
            logger.info(f"Submitting {spl_path} to Splunk AppInspect...")
            response = self.session.post(uri, files=files)

        response.raise_for_status()

        logger.info("Submission to Splunk AppInspect complete!")

        return response.json()["request_id"]

    def is_submission_report_ready(self, request_id: str) -> bool:
        """
        Checks if a Splunk AppInspect submission report is ready
        :return: True if it is ready, false otherwise
        """

        uri = f"https://appinspect.splunk.com/v1/app/validate/status/{request_id}"
        logger.info("Checking if submission report is ready...")
        response = self.session.get(uri)

        if response.status_code == 404 or response.json()["status"] in ["PREPARING", "PROCESSING"]:
            return False
        elif response.status_code == 200:
            return True
        else:
            logger.info("An unhandled error occurred while retrieving the submission report status!")
            response.raise_for_status()

    def get_submission_report(self, request_id: str) -> dict:
        """
        Gets a Splunk AppInspect submission report
        :param request_id: Request ID for the submission
        :return: JSON dict of the report
        """

        uri = f"https://appinspect.splunk.com/v1/app/report/{request_id}"
        response = self.session.get(uri)

        response.raise_for_status()

        json_ = response.json()

        return json_

    def is_submission_good(self, json_report: dict) -> bool:
        """
        Checks whether or not a submission has passed Splunk AppInspect
        :param json_report: JSON report
        :return: True if pass, false if fail
        """

        summary = json_report["summary"]
        failures = summary["failure"]

        if failures == 0:
            return True
        else:
            logger.error(f"APPINSPECT FAILED! Failures: {self._get_submission_failures(json_report=json_report)}")
            return False

    def _get_submission_failures(self, json_report: dict) -> str:
        """
        Gets a list of all failures from the Splunk AppInspect report
        :param json_report: JSON report
        :return: JSON string of failed AppInspect checks
        """

        failed = []
        reports = json_report["reports"]

        for report in reports:
            for group in report["groups"]:
                for check in group["checks"]:
                    if check["result"] == "failure":
                        failed.append(check)

        return json.dumps(failed, indent=4, sort_keys=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Splunk AppInspect with credentials.')
    parser.add_argument("username", type=str, help="Username")
    parser.add_argument("password", type=str, help="Password")
    parser.add_argument("--cloud", type=bool)

    args = parser.parse_args()
    username = args.username
    password = args.password
    use_cloud = args.cloud

    if use_cloud:
        a = AppInspector.init_from_ci(username=username, password=password, use_cloud=True)
    else:
        a = AppInspector.init_from_ci(username=username, password=password)
    a.authenticate()
    request_id = a.submit_file(spl_path="InsightConnect.spl")

    while True:
        logger.info("Checking submission report status...")
        ready = a.is_submission_report_ready(request_id=request_id)
        if ready:
            logger.info("Submission report is ready!")
            break
        else:
            logger.info("Submission report is not ready, sleeping for 5 seconds...")
            time.sleep(5)

    jr = a.get_submission_report(request_id=request_id)
    if a.is_submission_good(json_report=jr):
        logger.info("Splunk AppInspect PASSED!")
    else:
        raise Exception("Splunk AppInspect FAILED!")
