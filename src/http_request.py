import requests

from src.constants import GITHUB_URL, SUCCESS_CODES
from src.logger import setup_logger

log = setup_logger(__name__)

class HttpRequest:

    def __init__(self, github_token, owner, repo_name):
        self.github_repo_name = repo_name
        self.owner = owner
        self.headers = {
            "User-Agent": "svc.bot.ws1_github",
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {github_token}"
        }

    def put(self, url_segment, data):
        """
        Sends a PUT request
        :param url_segment: URL for the new Request object
        :param data: Data to be updated
        """
        return self.write_request(requests.put, url_segment, data)

    def post(self, url_segment, data):
        """
        Sends a POST request
        :param url_segment: URL for the new Request object
        :param data: Data to be uploaded
        """
        return self.write_request(requests.post, url_segment, data)

    def patch(self, url_segment, data):
        """
        Sends a POST request
        :param url_segment: URL for the new Request object
        :param data: Data to be uploaded
        """
        return self.write_request(requests.patch, url_segment, data)

    def write_request(self, req, url_segment, data):
        """
        Sends a write request
        :param req: request object can be request.put, request.patch, request.post
        :param url_segment: URL for the new Request object
        :param data: Data to be updated
        """
        url = f"{GITHUB_URL}/repos/{self.owner}/{self.github_repo_name}{url_segment}"
        return self.write_request_base(req, url, data)

    def org_put_request(self, url_segment, data):
        url = f"{GITHUB_URL}/orgs/{self.owner}{url_segment}"
        return self.write_request_base(requests.put, url, data)

    def write_request_base(self, req, url, data):
        """
        Sends a write request
        :param req: request object can be request.put, request.patch, request.post
        :param url: URL for the new Request object
        :param data: Data to be updated
        """
        response = req(url, json=data, headers=self.headers)

        if response.status_code not in SUCCESS_CODES:
            log.error(f'Url:{url} Method: {response.request.method} Status code: {response.status_code}\n '
                      f' Response: {response.text}\n')
            response.raise_for_status()  # Raise an exception for HTTP errors

        return response

    def delete(self, url_segment):
        url = f"{GITHUB_URL}/repos/{self.owner}/{self.github_repo_name}{url_segment}"
        return self.delete_base(url)

    def delete_base(self, url):
        """
        Sends a write request
        :param req: request object can be request.put, request.patch, request.post
        :param url: URL for the new Request object
        :param data: Data to be updated
        """
        response = requests.delete(url, headers=self.headers)

        if response.status_code not in SUCCESS_CODES:
            log.error(f'Url:{url} Method: {response.request.method} Status code: {response.status_code}\n '
                      f' Response: {response.text}\n')
            response.raise_for_status()  # Raise an exception for HTTP errors

        return response

    def org_get_request(self, url_segment):
        """
        Sends a GET request to the GitHub API
        :param url_segment: segment url of the request
        :return: the payload json
        """
        url = f"{GITHUB_URL}/orgs/{self.owner}{url_segment}"
        return self.get_base(url)

    def get(self, url_segment):
        """
        Sends a GET request to the GitHub API
        :param url_segment: segment url of the request
        :return: the payload json
        """
        url = f"{GITHUB_URL}/repos/{self.owner}/{self.github_repo_name}{url_segment}"
        return self.get_base(url)

    def get_base(self, url):
        """
        Sends a GET request to the GitHub API
        :param url: url of the request
        :return: the payload json
        """

        response = requests.get(url, headers=self.headers)

        if response.status_code not in SUCCESS_CODES:
            log.error(f'Url:{url} Method: GET Status code: {response.status_code}\n Response: {response.text}\n')
            response.raise_for_status()  # Raise an exception for HTTP errors

        return response.json()
