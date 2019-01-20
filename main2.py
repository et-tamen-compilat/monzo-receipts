import json
import uuid

import requests

import config
import oauth2
import receipt_types
from utils import error
from quickstart import get_matching_emails, convert_to_plain_text, get_email_by_id, get_data, get_service
import dateutil.parser

class ReceiptsClient:
    ''' An example single-account client of the Monzo Transaction Receipts API. 
        For the underlying OAuth2 implementation, see oauth2.OAuth2Client.
    '''

    def __init__(self):
        self._api_client = oauth2.OAuth2Client()
        self._api_client_ready = False
        self._account_id = None
        self.transactions = []


    def do_auth(self):
        ''' Perform OAuth2 flow mostly on command-line and retrieve information of the
            authorised user's current account information, rather than from joint account, 
            if present.
        '''

        print("Starting OAuth2 flow...")
        self._api_client.start_auth()

        print("OAuth2 flow completed, testing API call...")
        response = self._api_client.test_api_call()
        if "authenticated" in response:
            print("API call test successful!")
        else:
            error("OAuth2 flow seems to have failed.")
        self._api_client_ready = True

        print("Retrieving account information...")
        success, response = self._api_client.api_get("accounts", {})
        if not success or "accounts" not in response or len(response["accounts"]) < 1:
            error("Could not retrieve accounts information")
        
        # We will be operating on personal account only.
        for account in response["accounts"]:
            if "type" in account and account["type"] == "uk_retail":
                self._account_id = account["id"]
                print("Retrieved account information.")
                return

        if self._account_id is None:
            error("Could not find a personal account")
    

    def list_transactions(self, limit, since):
        ''' An example call to the end point documented in
            https://docs.monzo.com/#list-transactions, other requests 
            can be implemented in a similar fashion. 
        '''
        if self._api_client is None or not self._api_client_ready:
            error("API client not initialised.")

        # Our call is not paginated here with e.g. "limit": 10, which will be slow for
        # accounts with a lot of transactions.
        success, response = self._api_client.api_get("transactions", {
            "account_id": self._account_id, "limit": limit, "since": since, "expand[]": "merchant"
        })

        if not success or "transactions" not in response:
            error("Could not list past transactions ({})".format(response))
        
        self.transactions = response["transactions"]
        print(limit, " transactions loaded from ", since)

        #for t in self.transactions:
        #    print(t["id"])

        return self.transactions#[-2]
        
    def get_transaction(self, id):
        ''' An example call to the end point documented in
            https://docs.monzo.com/#list-transactions, other requests 
            can be implemented in a similar fashion. 
        '''
        if self._api_client is None or not self._api_client_ready:
            error("API client not initialised.")

        # Our call is not paginated here with e.g. "limit": 10, which will be slow for
        # accounts with a lot of transactions.
        success, response = self._api_client.api_get("transactions/" + id, {
            "account_id": self._account_id, "expand[]": "merchant"
        })

        if not success or "transaction" not in response:
            error("Could not list past transactions ({})".format(response))
        
        #self.transactions = response["transactions"]
        #print(limit, " transactions loaded from ", since)

        #for t in self.transactions:
        #    print(t["id"])

        return response["transaction"]#self.transactions[-2]
 
    def read_receipt(self, receipt_id):
        ''' Retrieve receipt for a transaction with an external ID of our choosing.
        '''
        success, response = self._api_client.api_get("transaction-receipts", {
            "external_id": receipt_id,
        })
        if not success:
            error("Failed to load receipt: {}".format(response))
        
        print("Receipt read: {}".format(response))

    
    def example_add_receipt_data(self, data_in, transaction_id, amount, currency, payment_type, vat_amount):
        ''' An example in which we add receipt data to the latest transaction 
            of the account, with fabricated information. You can set varying 
            receipts data on the same transaction again and again to test it 
            if you need to. 
        '''

        #transaction_id = self.transactions[-2]
        print("Using most recent transaction to attach receipt: {}".format(transaction_id))

        # Using a random receipt ID we generate as external ID
        receipt_id = uuid.uuid4().hex
       
        items = []
        for i in data_in:
            items.append(receipt_types.Item(i[0], i[1], "", i[2], currency, 0, []))

        payments = [receipt_types.Payment(payment_type, "", "", "", "", "", "", "", amount, currency )]
        taxes = [receipt_types.Tax("VAT", vat_amount, currency, "12345678" )]
        receipt = receipt_types.Receipt("", receipt_id, transaction_id, amount, currency, payments, taxes, items)
        receipt_marshaled = receipt.marshal()        
        
        print("Uploading receipt data to API: ", json.dumps(receipt_marshaled, indent=4, sort_keys=True))
        print("")
        
        success, response = self._api_client.api_put("transaction-receipts/", receipt_marshaled)
        if not success:
            error("Failed to upload receipt: {}".format(response))

        print("Successfully uploaded receipt {}: {}".format(receipt_id, response))
        return receipt_id

    
    def example_register_webhook(self, incoming_endpoint):
        '''
        This is an example on registering a webhook with Monzo for Monzo's server to call your own
        backend service endpoint when certain events happen on an account. This is useful if you 
        deploy an API client as a backend service with an incoming interface exposed to the internet.
        Your backend code can then, for example, attach receipts to new transactions in an event-
        driven manner. For more details, see https://docs.monzo.com/#webhooks
        '''

        print("Listing webhooks on account")
        success, response = self._api_client.api_get("webhooks", {
            "account_id": self._account_id,
        })
        if not success:
            error("Failed to list webhooks: {}".format(response))
        print("Existing webhooks: ", response)

        print("Registering a webhook with callback URL {} ...".format(incoming_endpoint))
        success, response = self._api_client.api_post("webhooks", {
            "account_id": self._account_id,
            "url": incoming_endpoint,
        })
        if not success or "webhook" not in response:
            error("Failed to register webhook: {}".format(response))
        print("Successfully registered webhooks ", response)

        return response["webhook"]["id"]
        

if __name__ == "__main__":
    client = ReceiptsClient()
    client.do_auth()
    transactions = client.list_transactions(10, "2018-05-05T20:00:00Z")
    #receipt_id = client.example_add_receipt_data([["Bangkok Street Platter", 2, "platters", 1600, 320],["Grilled Chicken Satay", 1, "meal", 650, 130],["Pork Belly", 1, "meal", 1300, 260]],transaction_id , 3550, "GBP", "card", 710 )
    #client.read_receipt(receipt_id)
    #client.example_register_webhook("https://example.com/webhook_callback") 
    # The webhook endpoint used should be an HTTP-style server served by your own app server.
    for i in transactions:
        if i["merchant"] != None:
            print(i["merchant"]["name"], i["amount"], i["id"])
    transaction_id = "tx_00009WJJ1JHofc2YzrDXRh"
    transaction = client.get_transaction(transaction_id)
    print(transaction)
    print(transaction["created"], dateutil.parser.parse(transaction["created"]))
    seconds = int(dateutil.parser.parse(transaction["created"]).timestamp())
    service = get_service()
    matching = get_matching_emails(service, seconds + 86400, seconds - 86400, transaction["merchant"]["name"])
    print(matching)
    (items, vat, total) = (get_data(convert_to_plain_text(get_email_by_id(service, matching[0]))))
    print(items)
    print(vat)
    print(total)
    client.example_add_receipt_data(items, "tx_00009WJJ1JHofc2YzrDXRh", total, 'GBP', 'card', vat)


    
            
        
    
