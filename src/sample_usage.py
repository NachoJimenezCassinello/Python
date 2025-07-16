"""Run this script to verify credentials & library wiring."""
from src.utils.sf_auth import SalesforceAuth
from src.utils.sf_REST import SalesforceREST
from src.utils.exceptions import SalesforceAPIError
if __name__ == "__main__":
    auth = SalesforceAuth()
    client = SalesforceREST(auth)

    print("→ First 3 Accounts")
    for rec in client.query("SELECT Id, Name FROM Account LIMIT 3"):
        print(rec["Id"], "=>", rec["Name"])

    # Example composite (two dummy GETs)
    batch = [
        {
			"method": "GET",
			"url": f"/services/data/v60.0/query/?q=SELECT Id, BillingStreet, BillingCity, BillingPostalCode, BillingCountry FROM Account LIMIT 1",
			"referenceId": "AccountReference"
		},{
            "method": "GET",
            "url": "/services/data/v60.0/sobjects/Account/@{AccountReference.records[0].Id}",
            "referenceId": "A",
        }
    ]
    print("→ Composite result", client.composite(batch))

    # Publish Platform‑Event example (catch error if event not defined)
    try:
        res = client.publish_event("Test__e", {"Code__c": "007"})
        print("→ Event ID", res)
    except SalesforceAPIError as err:
        print("Event failed:", err)
