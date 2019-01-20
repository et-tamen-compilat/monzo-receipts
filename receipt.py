import requests
import time
# If you are using a Jupyter notebook, uncomment the following line.
#%matplotlib inline
#import matplotlib.pyplot as plt
#from matplotlib.patches import Rectangle
#from PIL import Image
from io import BytesIO

# Replace <Subscription Key> with your valid subscription key.
subscription_key = "6c54a0d3566846a59ed7e41de5d65bd0"
assert subscription_key

# You must use the same region in your REST call as you used to get your
# subscription keys. For example, if you got your subscription keys from
# westus, replace "westcentralus" in the URI below with "westus".
#
# Free trial subscription keys are generated in the "westus" region.
# If you use a free trial subscription key, you shouldn't need to change
# this region.


# Set image_url to the URL of an image that you want to analyze.
#restaurant_one = "https://media-cdn.tripadvisor.com/media/photo-s/10/e8/f0/ac/receipt.jpg"
#restaurant_two = "https://media-cdn.tripadvisor.com/media/photo-s/03/63/af/02/george-s-italian-restaurant.jpg?fbclid=IwAR1zBKPmZLW-q0CPot9oRL8tkQ81srgEBz-NYWdydXnCJAXG7J3NVByghO4"
#restaurant_three = "https://scontent-lht6-1.xx.fbcdn.net/v/t1.15752-9/49368778_377540766157610_2943868939429478400_n.jpg?_nc_cat=105&_nc_ht=scontent-lht6-1.xx&oh=bd9502cd48398e9b9a7cda71825fd112&oe=5CD04606"
#bar_receipt = "https://www.latimes.com/resizer/icwsRMTiP_WDz5RvchwQGDCDKHY=/1200x0/www.trbimg.com/img-561c0d46/turbine/la-sp-sarkisian-alcohol-receipts-20151012?fbclid=IwAR1soFOkwaz03TCFHg8OVj6P_a20zUyUcBxCcvrdXsri-rvoPWZNtSDa590"
#image_url = restaurant_one

vision_base_url = "https://westcentralus.api.cognitive.microsoft.com/vision/v2.0/"
ocr_url = vision_base_url + "ocr"
handwritten_url = vision_base_url + "recognizeText"
headers = {'Ocp-Apim-Subscription-Key': subscription_key}
params  = {'language': 'unk', 'detectOrientation': 'true'}
image_path = "C:/Users/HugoMayo/Downloads/restaurantreceipt.jpg"
image_data = open(image_path, "rb").read()
headers    = {'Ocp-Apim-Subscription-Key': subscription_key,
                  'Content-Type': 'application/octet-stream'}
                  
handwritten = False
if not handwritten:
    params     = {'visualFeatures': 'Categories,Description,Color'}
    response = requests.post(ocr_url, headers=headers, params=params, data=image_data)
    response.raise_for_status()
    analysis = response.json()  

   # Extract the word bounding boxes and text.
    line_infos = [region["lines"] for region in analysis["regions"]]
    index = 0
    all_words = [[]]
    for line_info in line_infos:
        for line in line_info:
            all_words.append([])
            for word in line['words']:
                all_words[index].append(word['text'])
            index += 1
    print(all_words)
else:
    params = {'mode' : 'Handwritten'}
    response = requests.post(
        handwritten_url, headers=headers, params=params, data=image_data)
    response.raise_for_status()
    

    operation_url = response.headers["Operation-Location"]

    # The recognized text isn't immediately available, so poll to wait for completion.
    analysis = {}
    poll = True
    while (poll):
        response_final = requests.get(
            response.headers["Operation-Location"], headers=headers)
        analysis = response_final.json()
        time.sleep(1)
        if ("recognitionResult" in analysis):
            poll= False 
        if ("status" in analysis and analysis['status'] == 'Failed'):
            poll= False

    polygons=[]
    if ("recognitionResult" in analysis):
        # Extract the recognized text, with bounding boxes.
        polygons = [(line["boundingBox"], line["text"])
            for line in analysis["recognitionResult"]["lines"]]
    print(polygons)
    text = []
    for line in polygons:
        text.append(line[1])
    print(text)

