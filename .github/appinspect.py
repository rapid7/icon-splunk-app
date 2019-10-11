import requests
from requests.auth import HTTPBasicAuth
import logging
import time

# Configure logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class AppInspector(object):

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

        self.session = None

    @classmethod
    def init_from_ci(cls, username: str, password: str):
        return cls(
            username=username,
            password=password
        )

    def authenticate(self) -> requests.Session:
        uri = "https://api.splunk.com/2.0/rest/login/splunk"
        logger.info("Authenticating with Splunk AppInspect...")
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

        if response.status_code == 404:
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
            logger.error(f"APPINSPECT FAILED! See report: \n{json_report}")
            return False


# if __name__ == "__main__":
#     if not (len(sys.argv) > 1 and sys.argv[1] == "--execute"):
#         raise Exception("Unsupported execution mode (expected --execute flag)")
#
#     try:
#         modular_alert = SendToInsightConnectAlert.from_cli()
#         modular_alert.run()
#         sys.exit(0)
#     except Exception as e:
#         raise Exception("An error occurred while running the alert. Information about the error: %s" % str(e))

a = AppInspector.init_from_ci(username="mrinehartr7", password="Ajfy^jwjg8fnBB%#$*Tb")
a.authenticate()
request_id = a.submit_file(spl_path="../InsightConnect.spl")

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
    logger.error("Splunk AppInspect FAILED!")



