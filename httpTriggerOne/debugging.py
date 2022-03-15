import logging
import mimetypes
from suds.client import Client
#import azure.functions as func
import json




#def main(req: func.HttpRequest) -> func.HttpResponse:
def main(req):
    logging.info('Python HTTP trigger function processed a request.')
    try:
        #req_body = req.get_json()
        req_body = req
        logging.info("after: ")
        logging.info(req_body)
    except ValueError: #dont catch all error, specify the error to catch
        logging.info(ValueError)
        pass
    except Exception as e:
        logging.error("Failed in init process!")
        logging.error(e)

    i = 0
    response = []
    for x in req_body:
        response.append(viesConnectionApprox(x))

    try:
        if response:
            logging.info(type(response))
            logging.info(response)
            #returnDict = Client.dict(response)
            
            #logging.info(returnDict)
            returnDict = response
            returnJson = json.dumps(returnDict, default=str)
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
        keys = req_body.keys()
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
    #check validity of request
    if requesterCountryCode != '':
        if not requesterCountryCode.isalpha():
            return "Invalid requester Vatid. Requester ID must begin with country code "
    if countryCode != '':
        if not countryCode.isalpha():
            return "Invalid Vatid. Searched Vat ID must begin with country code"

    #call the vies api
    try:
        url="https://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl"
        client = Client(url)
        logging.info(countryCode +vatNumber + traderName + traderCompanyType + traderStreet +  traderPostcode + traderCity + requesterCountryCode + requesterVatNumber)
        response = client.service.checkVatApprox(countryCode,vatNumber, traderName, traderCompanyType, traderStreet,  traderPostcode, traderCity, requesterCountryCode, requesterVatNumber)
        response = Client.dict(response)
        return response
    except Exception as e:
        # todo falls e eroror von Vies , dann entsprechend return
        logging.exception("error calling vies")

#the debugging part:
import os
script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, 'sample.dat')
with open(file_path) as file:
    req = json.load(file)      
main(req)
#end debugging.