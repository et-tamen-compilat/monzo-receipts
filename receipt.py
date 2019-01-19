import requests
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
vision_base_url = "https://westcentralus.api.cognitive.microsoft.com/vision/v2.0/"

ocr_url = vision_base_url + "ocr"

# Set image_url to the URL of an image that you want to analyze.
image_url = "https://media-cdn.tripadvisor.com/media/photo-s/10/e8/f0/ac/receipt.jpg"

headers = {'Ocp-Apim-Subscription-Key': subscription_key}
params  = {'language': 'unk', 'detectOrientation': 'true'}
data    = {'url': image_url}
response = requests.post(ocr_url, headers=headers, params=params, json=data)
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
            #print(word['text'],end='')
        #print('\n')
        index += 1
# Display the image and overlay it with the extracted text.
#plt.figure(figsize=(5, 5))
#image = Image.open(BytesIO(requests.get(image_url).content))
#ax = plt.imshow(image, alpha=0.5)
print(all_words)
