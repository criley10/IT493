from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import TextOperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import TextRecognitionMode
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time

import unittest

class TestAzureConnection(unittest.TestCase):

  def test_setup(self):
    '''
    Test to try to set the required environment variables needed for the other tests
    '''
    if 'COMPUTER_VISION_SUBSCRIPTION_KEY' in os.environ:
      subscription_key = os.environ['COMPUTER_VISION_SUBSCRIPTION_KEY']
    else:
      print("\nSet the COMPUTER_VISION_SUBSCRIPTION_KEY environment variable.\n**Restart your shell or IDE for changes to take effect.**")
      sys.exit()

    if 'COMPUTER_VISION_ENDPOINT' in os.environ:
      endpoint = os.environ['COMPUTER_VISION_ENDPOINT']

    text_recognition_url = endpoint + "vision/v2.1/read/core/asyncBatchAnalyze"

  def test_cognitive(self):
    '''
    Test to send a example file to vision processing so we are confident 
    we can send handwritten files
    '''
    if 'COMPUTER_VISION_SUBSCRIPTION_KEY' in os.environ:
      subscription_key = os.environ['COMPUTER_VISION_SUBSCRIPTION_KEY']
    else:
      print("\nSet the COMPUTER_VISION_SUBSCRIPTION_KEY environment variable.\n**Restart your shell or IDE for changes to take effect.**")
      sys.exit()

    if 'COMPUTER_VISION_ENDPOINT' in os.environ:
      endpoint = os.environ['COMPUTER_VISION_ENDPOINT']

    text_recognition_url = endpoint + "vision/v2.1/read/core/asyncBatchAnalyze"
    
    headers = {'Ocp-Apim-Subscription-Key': subscription_key}
    data = {'url': 'https://imgur.com/flouJ14.jpg'}
    response = requests.post(
      text_recognition_url, headers=headers, json=data)
    response.raise_for_status()

    # Holds the URI used to retrieve the recognized text.
    operation_url = response.headers["Operation-Location"]

    # The recognized text isn't immediately available, so poll to wait for completion.
    analysis = {}
    poll = True
    while (poll):
        response_final = requests.get(
            operation_url, headers=headers)
        analysis = response_final.json()
        print(analysis)
        time.sleep(1)
        assertIn("recognitionResults", analysis)

  def test_container(self):
    '''
    Test to try the connection to blob container and fetch the list of files
    '''
    if 'AZURE_STORAGE_CONNECTION_STRING' in os.environ:
        connect_str = os.environ['AZURE_STORAGE_CONNECTION_STRING']
    else:
        print("\nSet the AZURE_STORAGE_CONNECTION_STRING environment variable.\n**Restart your shell or IDE for changes to take effect.**")
        sys.exit()
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_client = blob_service_client.get_container_client('capstone')
    blob_list = container_client.list_blobs()
    assertIsNotNone(blob_list)

  def test_upload(self):
    '''
    Test to try to upload a file to the blob container
    '''
    # Setup variables from os environment variables
    if 'AZURE_STORAGE_CONNECTION_STRING' in os.environ:
        connect_str = os.environ['AZURE_STORAGE_CONNECTION_STRING']
    else:
        print("\nSet the AZURE_STORAGE_CONNECTION_STRING environment variable.\n**Restart your shell or IDE for changes to take effect.**")
        sys.exit()
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Create a file in local data directory to upload and download
    local_path = "./data"
    local_file_name = "test" + str(uuid.uuid4()) + ".txt"
    upload_file_path = os.path.join(local_path, local_file_name)

    # Write text to the file
    file = open(upload_file_path, 'w')
    file.write("This is an upload test")
    file.close()

    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client(container='capstone', blob=local_file_name)

    print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

    # Upload the created file
    with open(upload_file_path, "rb") as data:
        blob_client.upload_blob(data)