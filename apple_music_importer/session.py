import requests
import time
import urllib.request
import json


class UnauthorizedRequestException(Exception):
    """Exception raised for unauthorized requests."""

    pass


class SessionHandler:
    def __init__(self, request_headers):
        self.session = requests.Session()
        self.session.headers.update(request_headers)

    def get(self, url, request_delay=1):
        time.sleep(request_delay)  # Ensure delay between requests
        response = self.session.get(url)
        if response.status_code in [401, 400]:
            print(response.json())
            raise UnauthorizedRequestException("Unauthorized request")
        if response.status_code in [429, 403]:
            print("Rate limit exceeded. Increasing delay and retrying...")
            if request_delay > 10:
                request_delay *= 2
            else:
                request_delay += 5
            return self.get(url, request_delay)
        response.raise_for_status()
        return response.json()

    def post(self, url, data=None, request_delay=1):
        time.sleep(request_delay)
        response = self.session.post(url, json=data)
        if response.status_code in [401, 400]:
            print(response.json())
            raise UnauthorizedRequestException("Unauthorized request")
        if response.status_code in [429, 403]:
            print("Rate limit exceeded. Increasing delay and retrying...")
            if request_delay > 10:
                request_delay *= 2
            else:
                request_delay += 5
            return self.post(url, data, request_delay)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_without_session(url, request_delay=1):
        time.sleep(request_delay)  # Ensure delay between requests
        with urllib.request.urlopen(url) as response:
            if response.getcode() != 200:
                if response.getcode() in [429, 403]:
                    print("Rate limit exceeded. Increasing delay and retrying...")
                    if request_delay > 10:
                        request_delay *= 2
                    else:
                        request_delay += 5
                    return SessionHandler.get_without_session(url, request_delay)
                if response.getcode() in [401, 400]:
                    raise UnauthorizedRequestException("Unauthorized request")
                raise Exception(f"Request failed with status code {response.getcode()}")
            return json.load(response)
