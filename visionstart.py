import os, uuid, sys, time, csv
from azure.cognitiveservices.language.textanalytics import TextAnalyticsClient
from azure.storage.blob import BlockBlobService, PublicAccess
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import TextOperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import TextRecognitionMode
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import os, uuid, sys
from azure.storage.blob import BlockBlobService, PublicAccess
import tkinter as tk
from tkinter.filedialog import askopenfilename
from shutil import copyfile
from azure.storage.blob import BlockBlobService
from azure.storage.blob import ContentSettings


############################################### Storage


#try:
    #print (sys.argv[1])


    # Create the BlockBlockService that is used to call the Blob service for the storage account
    #block_blob_service = BlockBlobService(account_name='angoraresumestorage', account_key='6OqlmeV5cPLVEs+tF57f37vjU4AxS5SxFGcWwfO3/LGRbwlmjEKXw8+RSY2MZVyyQoI7lTnucq+iJFktJkCsQA==')

    # Create a container called 'quickstartblobs'.
    #container_name ='userresumes'

    # Set the permission so the blobs are public.
    #block_blob_service.set_container_acl(container_name, public_access=PublicAccess.Container)

    # Download the blob(s).
    # Add '_DOWNLOADED' as prefix to '.txt' so you can see both files in Documents.
    #full_path_to_file2 = os.path.join(os.path.expanduser("~/Documents"), str.replace(sys.argv[1] ,'.pdf'))
    #block_blob_service.get_blob_to_path(container_name, sys.argv[1] + '.pdf', full_path_to_file2)

#except Exception as e:
#    print(e)

################################# Vision declare

# Add your Computer Vision subscription key to your environment variables.
if 'COMPUTER_VISION_SUBSCRIPTION_KEY' in os.environ:
    subscription_key = os.environ['COMPUTER_VISION_SUBSCRIPTION_KEY']
else:
    print("\nSet the COMPUTER_VISION_SUBSCRIPTION_KEY environment variable.\n**Restart your shell or IDE for changes to take effect.**")
    sys.exit()
# Add your Computer Vision endpoint to your environment variables.
if 'COMPUTER_VISION_ENDPOINT' in os.environ:
    endpoint = os.environ['COMPUTER_VISION_ENDPOINT']
else:
    print("\nSet the COMPUTER_VISION_ENDPOINT environment variable.\n**Restart your shell or IDE for changes to take effect.**")
    sys.exit()

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
############################################

########################################## Text Analytics declare

key_var_name = 'TEXT_ANALYTICS_SUBSCRIPTION_KEY'
if not key_var_name in os.environ:
    raise Exception('Please set/export the environment variable: {}'.format(key_var_name))
subscription_key_text = os.environ[key_var_name]

endpoint_var_name = 'TEXT_ANALYTICS_ENDPOINT'
if not endpoint_var_name in os.environ:
    raise Exception('Please set/export the environment variable: {}'.format(endpoint_var_name))
endpoint_text = os.environ[endpoint_var_name]

credentials = CognitiveServicesCredentials(subscription_key_text)

text_analytics = TextAnalyticsClient(endpoint="https://angoratextanalytics.cognitiveservices.azure.com/", credentials=credentials)
print("===== Detect printed text - remote =====")
# Get an image with printed text

##############################################
z = 0
go = True
gpas = []
names = []
j = 0
while j < 100:
    names.append("")
    j+=1

block_blob_service = BlockBlobService(account_name='angoraresumestorage', account_key='6OqlmeV5cPLVEs+tF57f37vjU4AxS5SxFGcWwfO3/LGRbwlmjEKXw8+RSY2MZVyyQoI7lTnucq+iJFktJkCsQA==')

blobs = block_blob_service.list_blobs('userresumes')

for blob in blobs:
    remote_image_printed_text_url = "https://angoraresumestorage.blob.core.windows.net/userresumes/" + blob.name

    # Call API with URL and raw response (allows you to get the operation location)
    recognize_printed_results = computervision_client.batch_read_file(remote_image_printed_text_url,  raw=True)

    # Get the operation location (URL with an ID at the end) from the response
    operation_location_remote = recognize_printed_results.headers["Operation-Location"]
    # Grab the ID from the URL
    operation_id = operation_location_remote.split("/")[-1]

    # Call the "GET" API and wait for it to retrieve the results 
    while True:
        get_printed_text_results = computervision_client.get_read_operation_result(operation_id)
        if get_printed_text_results.status not in ['NotStarted', 'Running']:
            break
        time.sleep(1)

    strin = ""
    # Print the detected text, line by line
    if get_printed_text_results.status == TextOperationStatusCodes.succeeded:
        for text_result in get_printed_text_results.recognition_results:
            for line in text_result.lines:
                strin += line.text + " "
                start = line.text.find("GPA")
                if "GPA" in line.text:
                    if start != -1:
                        stri = line.text[start]
                        i = start+1
                        try:
                            while not (stri in "43210"):
                                stri = line.text[i]
                                i += 1
                            gpa = line.text[i-1:i+2]
                            gpa = str(gpa)
                            gpa = list(gpa)
                            gpa[1] = '.'
                            gpa = "".join(gpa)
                            gpas.append([float(gpa),remote_image_printed_text_url, z, ""])

                        except:
                            try:
                                i = start
                                while not (strin in "1234567890"):
                                    strin = line.text[i]
                                    i-=1
                                gpa = line.text[i-1:i+2]
                                gpa = str(gpa)
                                gpa = list(gpa)
                                gpa[1] = '.'
                                gpa = "".join(gpa)
                                gpas.append([float(gpa),remote_image_printed_text_url, z, ""])
                            except:
                                strin += "\n"
                #print(line.bounding_box)


    # documents = [
    #     {
    #         "id": "1",
    #         "language": "en",
    #         "text": strin
    #     }
    # ]
    # response = text_analytics.key_phrases(documents=documents)
    print(z)

    ################################################################################################ Entity
    documents = [
        {
            "id": "1",
            "language": "en",
            "text": strin
        }
    ]
    response = text_analytics.entities(documents=documents)

    for document in response.documents:
        for entity in document.entities:
            if str(entity.type) == "Person":
                if names[z] == "":
                    names[z] = (entity.name)

    z+=1
count = 0
for tupl in gpas:
    tupl[3] = names[tupl[2]]
    count+=1;
with open('resumes.csv', 'w+') as csvfile:
    csvWriter = csv.writer(csvfile)
    csvWriter.writerows(gpas)

# Create the BlockBlockService that is used to call the Blob service for the storage account
block_blob_service = BlockBlobService(account_name='angoraresumestorage', account_key='6OqlmeV5cPLVEs+tF57f37vjU4AxS5SxFGcWwfO3/LGRbwlmjEKXw8+RSY2MZVyyQoI7lTnucq+iJFktJkCsQA==')

# Create a container called 'quickstartblobs'.
container_name ='gpareports'
block_blob_service.create_container(container_name)
# Set the permission so the blobs are public.
block_blob_service.set_container_acl(container_name, public_access=PublicAccess.Container)

block_blob_service.create_blob_from_path(container_name,'resumes.csv','/home/vagrant/Documents/Hussain/resumes.csv')

