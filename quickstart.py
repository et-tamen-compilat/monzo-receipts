from __future__ import print_function
import pickle
import base64
import os.path
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import html2text
from datetime import datetime
import re

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

#master_regex = r"([a-zA-Z\ &\d\(\)\.:\]\[\-\,]+)(\n?:Sold by[a-zA-Z\ &\d\(\)\.:]+)?[\ \n\r]*£?(\d+\.\d{2})\D"
#master_regex = r"([a-zA-Z\ &\d\(\)\.:\]\[\-\,]+)[\ \n\r]+£?(\d+\.\d{2})\D"
#master_regex = r"([a-zA-Z\ &\d\(\)\.:\]\[\-\,]+)(\n?Sold by[a-zA-Z\ &\d\(\)\.:]+)?[\ \n\r]*£?(\d+\.\d{2})\D"
#master_regex = r"(\||\*|^)([a-zA-Z\ &\d\(\)\.:\]\[\-\,]+)(\n[a-zA-Z\ &\d\(\)\.:\]\[\-\,]+)*[\ \n\r\|\-]*-?£?(\d+\.\d{2})\D"
#master_regex = r"([a-zA-Z][a-zA-Z\ &\d\(\)\.:\]\[\-\,]+)(\n[a-zA-Z\ &\d\(\)\.:\]\[\-\,]+)*[\|\-\ \n\r]*-?£?(\d+\.\d{2})\D"
#master_regex = r"([a-zA-ZÀ-ú][a-zA-ZÀ-ú\ &\d\(\)\.:\]\[\-\,]+)((?:\n)[a-zA-ZÀ-ú\ &\d\(\)\.:\]\[\-\,]+)*[\|\-\ \n\r]*-?£?(\d+\.\d{2})\D"
master_regex = r"([a-zA-ZÀ-ú®\'\"][a-zA-ZÀ-ú®\'\"\ &\d\(\)\.:\]\[\-\,]+)((?:\n)[a-zA-ZÀ-ú®\'\"\ &\d\(\)\.:\]\[\-\,]+)*[\|\-\ \n\r]*-?£?(\d+\.\d{2})\D"

def get_matching_emails(service, before, after, subject):
    q = "before:{before} after:{after} subject:{subject}".format(before=before, after=after, subject=subject)
    response = service.users().messages().list(userId='me', q=q).execute()
    return list(map(lambda x: x["id"], response["messages"]))

def convert_to_plain_text(email):
    for x in email["payload"]["parts"]:
        if (x["mimeType"] == "text/html"):
            html = base64.urlsafe_b64decode(x["body"]["data"])
            h = html2text.HTML2Text()
            h.ignore_links = True
            h.ignore_images = True
            #h.ignore_tables = True
            h.ignore_emphasis = True
            return h.handle(html.decode('UTF-8'))

def get_email_id_by_query(service, query):
    response = service.users().messages().list(userId='me', q=query).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])
    return messages[0]['id']

def get_email_by_id(service, message_id):
    return service.users().messages().get(userId='me', id=message_id).execute()

def get_date(email):
    return datetime.utcfromtimestamp(int(email["internalDate"]) / 1000)

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    #gbk id rfc822msgid:0100016533703b3a-1f3aebdc-db03-40c4-859c-3014bd1efa51-000000@email.amazonses.com
    #google play store id 
    amazon_id1 = 'rfc822msgid:01020168438850f4-ffad1b13-6154-4f65-8e71-7c18b615503f-000000@eu-west-1.amazonses.com'
    amazon_id2 = 'rfc822msgid:010201677e7bbc72-42a07a16-9e03-476e-80ca-8bb3dda11a86-000000@eu-west-1.amazonses.com'
    amazon_id3 = 'rfc822msgid:01020163186f0a90-7644ce96-1906-4565-9ee6-60115b6c96e3-000000@eu-west-1.amazonses.com'
    amazon_id4 = 'rfc822msgid:0102016622edbdf6-d0e91758-ec90-43a9-bea1-d0e05faeac1e-000000@eu-west-1.amazonses.com'
    amazon_id5 = 'rfc822msgid:0102016030c68d3b-ec689bf9-2fc9-4883-8ffa-206f1f893375-000000@eu-west-1.amazonses.com'
    google_play_id1 = 'rfc822msgid:a685cf0371b7dafc083015faa60953cc0d0ac6fd-10044049-100240651@google.com'
    google_play_id2 = 'rfc822msgid:5f665b9f0fdc8072.1532187432836.100240651.10044049.en-GB.589fc1be1ae4f1e4@google.com'
    google_play_id3 = 'rfc822msgid:5f665b9f0fdc8072.1523093171606.100240651.10044049.en-GB.45840e70707e3b8@google.com'
    google_play_id4 = 'rfc822msgid:000000000000c207b805789c8ce7@google.com'
    deliveroo_id1 = 'rfc822msgid:5afc7a1e51293_183fddfc3ec8d4273690@4320d7536864.mail'
    deliveroo_id2 = 'rfc822msgid:5babb9e861414_143fe11e20019049511e@5346a9355ef5.mail'
    #<<<<<<< HEAD
    query = deliveroo_id2

    message_id = get_email_id_by_query(service, query)
    z = get_email_by_id(service, message_id)
    print(get_matching_emails(service, "2019/01/20", "2019/01/01", "Monzo"))
    #=======
    
        #print(z)
    #print(z.keys())
    #print(z["payload"].keys())
    #print(z["payload"]["headers"])
    #print(z["payload"]['parts'][0])
    data = convert_to_plain_text(z)    
    print(data)
    print(get_date(z))

    print("---****---")

    for k in re.findall(master_regex, data, re.MULTILINE):
        print(k)
    reading_items = True
    final_data = []
    for k in re.findall(master_regex, data, re.MULTILINE):
        desc = k[0].rstrip()
        price = int(float(k[2]) * 100)
        if "Item Subtotal:" in desc or "Total" in desc:
            reading_items = False
        elif  'VAT' in desc and 'Total' not in desc:
            final_data.append(('VAT', price))
        elif "Postage" in desc and price > 0:
            final_data.append(('Postage & Packing', price))
        elif desc and "Postage & Packing:" not in desc and reading_items:
            quantity = 1
            final_data.append((desc, quantity, price))   
    print(final_data)
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    
    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            pass
            #print(label['name'])


if __name__ == '__main__':
    main()
