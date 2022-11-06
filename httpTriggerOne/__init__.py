import logging
import mimetypes
from suds.client import Client
import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    #the httpRequest is just a string containing and Arraay with many JSon Strings. Actually should be one big json string with sub categories, but whatever
    logger= logging.getLogger(__name__)
    logging.info('Python HTTP trigger function processed a request.')
    try:
        req_body = req.get_json()
        logging.info(req_body)
    except ValueError: 
        logging.info(ValueError)
        pass
    except Exception as e:
        logging.error("Failed in init process!")
        logging.error(e)

    #check validity of requesterVAtID
    if req_body[0]['requestervatID'] != '':
        if not req_body[0]['requestervatID'][:2].isalpha():
            return func.HttpResponse(
                f"Invalid requester Vatid. Requester ID must begin with two letters for country code",
                status_code=400
            ) 
        else:
            checkTheRequesterVatID = viesConnectionApprox(req_body[0])
            if checkTheRequesterVatID == "Server raised fault: 'Invalid Requester member state'" or checkTheRequesterVatID == "Server raised fault: 'INVALID_REQUESTER_INFO'":
                return func.HttpResponse(
                    f"Invalid requester Vatid. VIES raised error: Requester VAT ID is not valid.",
                    status_code=400
                ) 
        

    response = []
    for x in req_body:
        response.append(viesConnectionApprox(x))#json.loads(x))) #json.loads converts the JSON String into a Python dict # mainprocess

    try:
        if response:
            logging.info(type(response))
            logging.info(response)
            returnJson = json.dumps(response, default=str)
            logging.info("Response: " + returnJson)
            return func.HttpResponse(returnJson, status_code = 200, mimetype="application/json")
            
        else:
            return func.HttpResponse(
                f"Something went wrong with the execution. Contact System Developer.",
                status_code=500
            )
    except Exception as e:
        logging.exception("myError")
        return func.HttpResponse("customError", status_code=502)
        

def viesConnectionApprox(req_body): #Expects one line, with one VAT ID
    #define all the parameters from the json Post
    try:
        #keys = req_body.keys()
        vatID = req_body['vatID']
        vatNumber = vatID[2:]
        countryCode = vatID[:2]
        traderName = req_body['traderName']
        traderCompanyType = req_body['traderCompanyType']
        traderStreet = req_body['traderStreet']
        traderPostcode = req_body['traderPostcode']
        traderCity = req_body['traderCity']
        requesterVatID = req_body['requestervatID']
        requesterCountryCode = requesterVatID[:2]
        requesterVatNumber = requesterVatID[2:]
    except Exception as e:
        logging.exception("after the dict auseinander")
        return e
    
            

    #call the vies SOAP API
    try:
        url="https://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl"
        client = Client(url) # suds.Client
        logging.info(countryCode +vatNumber + traderName + traderCompanyType + traderStreet +  traderPostcode + traderCity + requesterCountryCode + requesterVatNumber)
        response = client.service.checkVatApprox(countryCode,vatNumber, traderName, traderCompanyType, traderStreet,  traderPostcode, traderCity, requesterCountryCode, requesterVatNumber)
        response = Client.dict(response)
        response["comment"] = getCountrySpecificComment(countryCode)
        return response
    except Exception as e:
        if str(e) == "Server raised fault: 'Invalid Requester member state'" or str(e) == "Server raised fault: 'INVALID_REQUESTER_INFO'":
            return str(e)
        #andere Errors returnen JSON
        return {
            "countryCode": "",
            "requestDate": "",
            "requestIdentifier": "",
            "traderAddress": "",
            "traderCompanyType": "",
            "traderName": "",
            "valid": False,
            "vatNumber": vatNumber,
            "comment": "Calling the VIES API Failed: " + str(e)
            }

def getCountrySpecificComment(countryCode):
    if countryCode.isalpha():
        commentByCountry= {"DE": "Germany does not give Customer Addresses via VIES.",
            "GB": "VIES has no data for britisch VAT IDs. Consider checking XI VAT Ids instead.",
            "IT": ""} #TODO finisch this list
        if commentByCountry[countryCode]
            return commentByCountry[countryCode]
        else:
            return ""
    else:
        return "not valid country code"
    
    