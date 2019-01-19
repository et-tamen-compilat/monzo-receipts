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
master_regex = r"(\||\*|^)([a-zA-Z\ &\d\(\)\.:\]\[\-\,]+)(\n[a-zA-Z\ &\d\(\)\.:\]\[\-\,]+)*[\ \n\r]*\|[\ \n\r]*-?£?(\d+\.\d{2})\D"

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
    #google play store id rfc822msgid:a685cf0371b7dafc083015faa60953cc0d0ac6fd-10044049-100240651@google.com
    #amazon id1 'rfc822msgid:01020168438850f4-ffad1b13-6154-4f65-8e71-7c18b615503f-000000@eu-west-1.amazonses.com
    #amazon id2 rfc822msgid:010201677e7bbc72-42a07a16-9e03-476e-80ca-8bb3dda11a86-000000@eu-west-1.amazonses.com
    #<<<<<<< HEAD
    query = 'rfc822msgid:1225807702.31204847.1545384334683.JavaMail.email@email.apple.com'
    message_id = get_email_id_by_query(service, query)
    z = get_email_by_id(service, message_id)
    print(get_matching_emails(service, "2019/01/20", "2019/01/01", "Monzo"))
    #=======
    #amazon id3 rfc822msgid:01020163186f0a90-7644ce96-1906-4565-9ee6-60115b6c96e3-000000@eu-west-1.amazonses.com
    #query = 'rfc822msgid:01020163186f0a90-7644ce96-1906-4565-9ee6-60115b6c96e3-000000@eu-west-1.amazonses.com'
    
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
