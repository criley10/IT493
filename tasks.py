import os
import sys
import requests
import time
# If you are using a Jupyter notebook, uncomment the following line.
# %matplotlib inline
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from PIL import Image
from io import BytesIO
from azure.storage.blob import BlobServiceClient

def request_analysis(subscription_key, image_name, text_recognition_url):
    headers = {'Ocp-Apim-Subscription-Key': subscription_key}
    data = {'url': 'https://elevenbravodelta.blob.core.windows.net/capstone/2019/' + image_name}
    response = requests.post(
        text_recognition_url, headers=headers, json=data)
    response.raise_for_status()

    # Holds the URI used to retrieve the recognized text.
    operation_url = response.headers["Operation-Location"]

    return operation_url

def analyze_response(operation_url, subscription_key):
    headers = {'Ocp-Apim-Subscription-Key': subscription_key}
    # The recognized text isn't immediately available, so poll to wait for completion.
    analysis = {}
    poll = True
    while (poll):
        response_final = requests.get(
            operation_url, headers=headers)
        analysis = response_final.json()
        print(analysis)
        time.sleep(1)
        if ("recognitionResults" in analysis):
            poll = False
        if ("status" in analysis and analysis['status'] == 'Failed'):
            poll = False

    return analysis

def create_polygons(analysis):
    polygons = []
    if ("recognitionResults" in analysis):
        # Extract the recognized text, with bounding boxes.
        polygons = [(line["boundingBox"], line["text"])
                    for line in analysis["recognitionResults"][0]["lines"]]
    
    return polygons

def draw_boxes(image_name, polygons):
    # Display the image and overlay it with the extracted text.
    plt.figure(figsize=(15, 15))
    image = Image.open(BytesIO(requests.get("https://elevenbravodelta.blob.core.windows.net/capstone/2019/" + image_name).content))
    ax = plt.imshow(image)
    for polygon in polygons:
        vertices = [(polygon[0][i], polygon[0][i+1])
                    for i in range(0, len(polygon[0]), 2)]
        text = polygon[1]
        patch = Polygon(vertices, closed=True, fill=False, linewidth=2, color='y')
        ax.axes.add_patch(patch)
        plt.text(vertices[0][0], vertices[0][1], text, fontsize=10, va="top", color='red')

    plt.savefig(image_name)

@task
def main(c):
    if 'COMPUTER_VISION_SUBSCRIPTION_KEY' in os.environ:
        subscription_key = os.environ['COMPUTER_VISION_SUBSCRIPTION_KEY']
    else:
        print("\nSet the COMPUTER_VISION_SUBSCRIPTION_KEY environment variable.\n**Restart your shell or IDE for changes to take effect.**")
        sys.exit()

    if 'COMPUTER_VISION_ENDPOINT' in os.environ:
        endpoint = os.environ['COMPUTER_VISION_ENDPOINT']

    text_recognition_url = endpoint + "vision/v2.1/read/core/asyncBatchAnalyze"

    if 'AZURE_STORAGE_CONNECTION_STRING' in os.environ:
        connect_str = os.environ['AZURE_STORAGE_CONNECTION_STRING']
    else:
        print("\nSet the AZURE_STORAGE_CONNECTION_STRING environment variable.\n**Restart your shell or IDE for changes to take effect.**")
        sys.exit()
    
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_client = blob_service_client.get_container_client('capstone')
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        image_name = blob['name'].split('/')[1]
        operation_url = request_analysis(subscription_key, image_name, text_recognition_url)
        analysis = analyze_response(operation_url, subscription_key)
        polygons = create_polygons(analysis)
        draw_boxes(image_name, polygons)
