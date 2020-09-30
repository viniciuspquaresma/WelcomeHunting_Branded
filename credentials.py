# PARTE1
# coding: latin-1
from flask import Flask, jsonify, request
# from datetime import datetime
import datetime
from collections import Counter
import json
import requests
import sys
import importlib
import csv
from bs4 import BeautifulSoup
import os
from dictor import dictor

# PARTE2
app = Flask(__name__)
observacao = []

# PARTE3


@app.route('/credenciais/<cust_id>', methods=['GET'])
def credentials(cust_id=None):
    data = []
    json_final = []
    application = capturarApp(cust_id)
    if(application!="None"):
        access_token = capturarTokenProd(application,cust_id)
        test_access_token = capturarTokenSand(application,cust_id)
        public_key = capturarPublicKeyProd(application,cust_id)
        test_public_key = capturarPublicKeySand(application,cust_id)
        json_final.append({
                    'Producao': access_token,
                    'SandBox': test_access_token,
                    'Public_key': public_key,
                    'Test_public_key': test_public_key,
            })    
    
    return jsonify(json_final)
                
def capturarTokenProd(application_id,cust_id):
   
    # data = []
    
    url = "http://api.internal.ml.com/applications/"+application_id+"/credentials?caller.id="+cust_id
    response = requests.get(url)
    response.encoding = "Latin-1"
    comments = json.loads(response.content)
    access_token = (str(dictor(comments, "0.access_token")))
    test_access_token = (str(dictor(comments, "0.test_access_token")))

    # data.append[{'token_prod': access_token,'token_sand': test_access_token}] 
    return access_token
def capturarTokenSand(application_id,cust_id):
   
    url = "http://api.internal.ml.com/applications/"+application_id+"/credentials?caller.id="+cust_id
    response = requests.get(url)
    response.encoding = "Latin-1"
    comments = json.loads(response.content)
    test_access_token = (str(dictor(comments, "0.test_access_token")))
    # data.append[{'token_prod': access_token,'token_sand': test_access_token}] 
    return test_access_token
def capturarPublicKeyProd(application_id,cust_id):
   
    url = "http://api.internal.ml.com/applications/"+application_id+"/credentials?caller.id="+cust_id
    response = requests.get(url)
    response.encoding = "Latin-1"
    comments = json.loads(response.content)
    public_key = (str(dictor(comments, "0.public_key")))
    # data.append[{'token_prod': access_token,'token_sand': test_access_token}] 
    return public_key    

def capturarPublicKeySand(application_id,cust_id):
   
    url = "http://api.internal.ml.com/applications/"+application_id+"/credentials?caller.id="+cust_id
    response = requests.get(url)
    response.encoding = "Latin-1"
    comments = json.loads(response.content)
    public_key = (str(dictor(comments, "0.test_public_key")))
    # data.append[{'token_prod': access_token,'token_sand': test_access_token}] 
    return public_key    

def capturarApp(cust_id):
    
    url = "http://api.internal.ml.com/applications/search?owner_id="+cust_id 
    response = requests.get(url)
    response.encoding = "Latin-1"
    comments = json.loads(response.content)
    # print (comments)
    application_id = str(dictor(comments, "0.id"))
    return application_id

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    # app.run(host='0.0.0.0', port=port, debug=True)
    app.run(host='0.0.0.0', port=port, debug=True)
