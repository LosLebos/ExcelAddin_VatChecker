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
        logging.info("after: ")
        logging.info(req_body)
    except ValueError: #dont catch all error, specify the error to catch
        logging.info(ValueError)
        pass
    except Exception as e:
        logging.error("Failed in init process!")
        logging.error(e)

    #check validity of requesterVAtID
    if req_body[0]['requestervatID'] != '':
        if not req_body[0]['requestervatID'].isalpha():
            return func.HttpResponse(
                f"Invalid requester Vatid. Requester ID must begin with two letters for country code",
                status_code=203
            )

    response = []
    for x in req_body:
        response.append(viesConnectionApprox(json.loads(x))) #json.loads converts the JSON String into a Python dict # mainprocess

    try:
        if response:
            logging.info(type(response))
            logging.info(response)
            returnJson = json.dumps(response, default=str)
            logging.info("Response: " + returnJson)
            return func.HttpResponse(returnJson, status_code = 201, mimetype="application/json")
            
        else:
            return func.HttpResponse(
                f"Something went wrong with the execution. Contact System Developer.",
                status_code=202
            )
    except Exception as e:
        logging.exception("myError")
        return func.HttpResponse("customError", status_code=502)
        

def viesConnectionApprox(req_body):
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
    
    if countryCode != '':
        if not countryCode.isalpha():
            return {
            "countryCode": "",
            "requestDate": "",
            "requestIdentifier": "",
            "traderAddress": "",
            "traderCompanyType": "",
            "traderName": "",
            "valid": False,
            "vatNumber": vatNumber,
            "comment": "Invalid Vatid. Searched Vat ID must begin with two letters as a country code"
            }
            

    #call the vies api
    try:
        url="https://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl"
        client = Client(url)
        logging.info(countryCode +vatNumber + traderName + traderCompanyType + traderStreet +  traderPostcode + traderCity + requesterCountryCode + requesterVatNumber)
        response = client.service.checkVatApprox(countryCode,vatNumber, traderName, traderCompanyType, traderStreet,  traderPostcode, traderCity, requesterCountryCode, requesterVatNumber)
        response = Client.dict(response)
        return response
    except Exception as e:
        # todo falls e error von Vies , dann entsprechend return
        return {
            "countryCode": "",
            "requestDate": "",
            "requestIdentifier": "",
            "traderAddress": "",
            "traderCompanyType": "",
            "traderName": "",
            "valid": False,
            "vatNumber": vatNumber,
            "comment": "Calling the VIES API Failed: " + e
            }
        