import os
import json
from unittest import TestCase

import boto3
import botocore
import requests

"""
Make sure env variable AWS_SAM_STACK_NAME exists with the name of the stack we are going to test. 
"""

# Set "running_locally" flag if you are running the integration test locally
# Using VSCode tasks to set environment variables, so performing this comparison to convert to boolean
running_locally = (os.environ['RUNNING_LOCAL'] == "true")

class TestPingEvent(TestCase):
    api_endpoint: str
    lambda_client: botocore.client

    @classmethod
    def get_and_verify_stack_name(cls) -> str:
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")
        if not stack_name:
            raise Exception(
                "Cannot find env var AWS_SAM_STACK_NAME. \n"
                "Please setup this environment variable with the stack name where we are running integration tests."
            )

        # Verify stack exists
        client = boto3.client("cloudformation")
        try:
            client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(
                f"Cannot find stack {stack_name}. \n" f'Please make sure stack with the name "{stack_name}" exists.'
            ) from e

        return stack_name

    def setUp(self) -> None:
        """
        Based on the provided env variable AWS_SAM_STACK_NAME,
        here we use cloudformation API to find out what the DiscordBotApi URL is
        """

        """
        Setup Lambda client for local testing
        """
        if running_locally:
            self.api_endpoint = "http://localhost:3000/interactions"
        else: 
            stack_name = TestPingEvent.get_and_verify_stack_name()

            client = boto3.client("cloudformation")

            response = client.describe_stacks(StackName=stack_name)
            stacks = response["Stacks"]
            self.assertTrue(stacks, f"Cannot find stack {stack_name}")

            stack_outputs = stacks[0]["Outputs"]
            api_outputs = [output for output in stack_outputs if output["OutputKey"] == "DiscordBotApi"]
            self.assertTrue(api_outputs, f"Cannot find output DiscordBotApi in stack {stack_name}")

            self.api_endpoint = api_outputs[0]["OutputValue"]\


    def test_ping_event(self):
        """
        Make request to the ServerlessRestApi, verify the response has the proper keys.
        """
        pint_event_filepath = './events/ping.json'
        ping_event = None
        with open(pint_event_filepath) as f:
            ping_event = json.load(f)
            
            headers = ping_event['headers']
            body = ping_event['body']

            response = requests.post(self.api_endpoint, data=body, headers=headers)

            self.assertEqual(response.json()['type'], 1)

    def test_bad_request_signing(self):
        bad_signature_event_filepath = './events/bad_signature.json'
        bad_signature_event = None
        with open(bad_signature_event_filepath) as f:
            bad_signature_event = json.load(f)

            headers = bad_signature_event['headers']
            body = bad_signature_event['body']

            response = requests.post(self.api_endpoint, data=body, headers=headers)

            self.assertEqual(response.json()['content'], 'Invalid Request Signature')
