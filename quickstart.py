from __future__ import print_function
import pickle
import base64
import os.path
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import html2text

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

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
    #amazon id3 rfc822msgid:01020163186f0a90-7644ce96-1906-4565-9ee6-60115b6c96e3-000000@eu-west-1.amazonses.com
    query = 'rfc822msgid:01020163186f0a90-7644ce96-1906-4565-9ee6-60115b6c96e3-000000@eu-west-1.amazonses.com'
    
    response = service.users().messages().list(userId='me', q=query).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])
    message_id = messages[0]['id']

    z = service.users().messages().get(userId='me', id=message_id).execute()
  
    print(z)
    print(z.keys())
    print(z["payload"].keys())
    print(z["payload"]['parts'][0])
    for x in z["payload"]['parts']:
      print(x['mimeType'])
      if (x['mimeType'] == 'text/html'):
        html = base64.urlsafe_b64decode(x['body']['data'])
        #soup = BeautifulSoup(html, features="html.parser")
        #for script in soup(["script", "style"]):
            #script.extract()    # rip it out
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        h.ignore_tables = True
        h.ignore_emphasis = True
        print(h.handle(str(html)))
        

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
