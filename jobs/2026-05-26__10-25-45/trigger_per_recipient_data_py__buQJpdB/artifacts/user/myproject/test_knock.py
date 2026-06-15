import os
import requests

service_token = os.environ.get('KNOCK_SERVICE_TOKEN')
print("Service token:", service_token is not None)
api_token = os.environ.get('KNOCK_API_TOKEN')
print("API token:", api_token is not None)
