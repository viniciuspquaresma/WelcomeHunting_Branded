# PARTE1
# coding: latin-1
from flask import Flask, jsonify, request
from lib.isBranded import Brandeado
import datetime
import shutil
import os.path
from collections import Counter
import json
import requests
from time import time, sleep
from sched import scheduler
import sys
import importlib
import csv
import time
from bs4 import BeautifulSoup
import os
from dictor import dictor

# PARTE2
app = Flask(__name__)
observacao = []


@app.route('/ping', methods=['POST'])
def create_task():
    print(request.json)
    
    return (request.json['title'])

@app.route('/csv', methods=['GET'])
def csvGet():
    return csvMain() 

@app.route('/brandeado', methods=['GET'])
def csvBrandeadoGet():
    return brandeadoMain() 

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
    # return"Tudo pronto!"

@app.route('/brandeado/<cust_id>', methods=['GET'])
def brandeadoCust(cust_id=None):
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


@app.route('/validar/<cust_id>/<begin_date>', methods=['GET'])
def getMonitor(cust_id=None,begin_date=None,end_date=datetime.datetime.now()):
  
    return mainMonitor(cust_id,begin_date,end_date)

def csvMain():
    print("Verificando se tem arquivo a ser feito...")
    data = []
    try:
        with open('welcome_hunting.csv', 'r') as f:
            print("Arquivo encontrado...")
            
            mainMonitorCSV()
            data.append({'return': 'CSV GERADO'})
    except IOError as e:
        data.append({'return': 'Nao foi encontrado o arquivo ou está fora da VPN'})
        print("Nao foi encontrado ARQUIVO ou está fora da VPN - "+str(e))

def brandeadoMain():
    print("Verificando se tem arquivo a ser feito...")
    data = []
    try:
        with open('brandeado.csv', 'r') as f:
            print("Arquivo encontrado...")
            
            mainBrandeadoCSV()
            data.append({'return': 'CSV GERADO'})
    except IOError as e:
        data.append({'return': 'Nao foi encontrado o arquivo ou está fora da VPN'})
        print("Nao foi encontrado ARQUIVO ou está fora da VPN - "+str(e))
        

    return jsonify(data)

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
def mainMonitor(cust_id,begin_date,end_date):
    data_csv = []
    if os.path.exists('welcome_hunting.csv'):
        print("Arquivo encontrado...")
        data_csv = lerCsv()    
        
    
    
    
    # print (data_csv)
    json_final = []
    application = capturarApp(cust_id)
    if(application!="None"):
        access_token = capturarTokenProd(application,cust_id)
        test_access_token = capturarTokenSand(application,cust_id)
    begin_date = str(begin_date)
    end_date = str(end_date)
    end_date = end_date[0:23]+"-04:00"
    end_date = end_date.replace(" ", "T")
    
    
    if (application!="None"):
        try:
            validar_prod = validar(access_token,begin_date,end_date)
            # print(str(validar_prod))
            validar_sand = validar(test_access_token,begin_date,end_date)
            print(str(validar_sand))
           
            json_final.append({
                    'Producao': validar_prod,
                    'SandBox': validar_sand
            

            
            })  

            print (str(json_final))
            return jsonify(json_final)
        except Exception as e:
            json_final.append({'return': {
                'exception': e
            
        }})
            # print(json_final)

            return (str(json_final))    
    else:
        json_final.append({
                    'Producao': 'Nao tem application',
                    'SandBox':  'Nao tem application'
            

            
            }) 
        return jsonify(json_final)    
    
    # return"Tudo pronto!"

def mainBrandeadoCSV():
    
    linhas = lerBrandeadoCsv()
    
    # CRIACAO DE UM NOVO ARQUIVO
    novoArquivo = open("brandeado_upt.csv","w+", buffering=1)#csv.writer(open("brandeado_upt.csv", "a"))
    tokensProblema = csv.writer(open("brandeado_problema.csv", "a"))
    # CABECALHO
    novoArquivo.write("Cust_id, branded_link, branded_pref, api"+"\r\n")
    tokensProblema.writerow(["Cust_id", "IsBranded"])
    count = 1
    for linha in linhas:
        print('Analise do Cust - '+str(linha['Cust_id']))
        try:

            #LEITURA DO ARQUIVO EXISTENTE
            cust_id = linha["Cust_id"]

            json_final = []

            # os.system('cls' if os.name == 'nt' else 'clear')
            print('sequencia: ' + str(count))
            print ("------------------")
            print (" - Cust - "+str(cust_id))

            brand = Brandeado()
            resultado_branded = brand.isBranded(str(cust_id))
            count = count + 1
            novoArquivo.write(str(linha["Cust_id"]) + ',' + str(resultado_branded) + "\r\n")

            print('isBranded: ' +str(resultado_branded))
            #time.sleep(3)
            print("----------------------")
        except Exception as e:
            novoArquivo.write(str(linha["Cust_id"]) + ',' + 'ERRO' + "\r\n")
            tokensProblema.writerow([linha["Cust_id"],'ERRO'])
            print("ERRO"+str(e))
            json_final.append({'return': {
                'exception': e
        }})
    novoArquivo.close()
    #shutil.move("brandeado.csv", "/Users/rbarros/Desktop/projetos/Welcome Hunting/sucesso")  


def mainMonitorCSV():
    
    linhas = lerCsv()
    
    # CRIACAO DE UM NOVO ARQUIVO
    novoArquivo = csv.writer(open("welcome_hunting_upt.csv", "a"))
    tokensProblema = csv.writer(open("tokens_problema.csv", "a"))
    # CABECALHO
    novoArquivo.writerow(["Data inicio","Cust_id","Produto","Application","1 Request - Sand","1 Request - Prod", "Go-live", "IsBranded"])
    tokensProblema.writerow(["Data inicio","Cust_id","Produto","Application","1 Request - Sand","1 Request - Prod", "Go-live", "IsBranded"])
    for linha in linhas:
     print('Analise do Cust - '+str(linha['Cust_id']))
     try:
            
        #LEITURA DO ARQUIVO EXISTENTE
        cust_id = linha["Cust_id"]
        begin_date = linha["Data inicio"]
        end_date = datetime.datetime.now()
        begin_date = datetime.datetime.strptime(begin_date, "%d/%m/%Y").strftime("%Y-%m-%dT00:00:59.999-04:00")
        
        json_final = []
        
        application = capturarApp(cust_id)
        # os.system('cls' if os.name == 'nt' else 'clear')
        print ("------------------")
        print (" - Cust - "+str(cust_id))
        print("APP - "+application)
        print ("End_date - "+str(end_date))
        print ("Begin_date - "+str(begin_date))
        if(application!="None"):
            access_token = capturarTokenProd(application,cust_id)
            time.sleep(3)
            test_access_token = capturarTokenSand(application,cust_id)
            # time.sleep(3)
        begin_date = str(begin_date)
        end_date = str(end_date)
        end_date = end_date[0:23]+"-04:00"
        end_date = end_date.replace(" ", "T")
    
        
        if (application!="None"):
            
            try:
                validar_prod = validarV2(access_token,begin_date,end_date)
                validar_prod_ajustado = validar_prod[0:10]
                validar_sand = validarV2(test_access_token,begin_date,end_date)
                validar_sand_ajustado = validar_sand[0:10]

                if(str(validar_prod_ajustado)!="None"):    
                    validar_prod_ajustado = (datetime.datetime.strptime(validar_prod_ajustado, "%Y-%m-%d").strftime("%d/%m/%Y"))
                
                if(str(validar_sand_ajustado)!="None"):
                    validar_sand_ajustado = (datetime.datetime.strptime(validar_sand_ajustado, "%Y-%m-%d").strftime("%d/%m/%Y"))
                
                brand = Brandeado()
                resultado_branded = brand.isBranded(str(cust_id))
                # print(str(resultado_branded))
                # print(str(msg))
                # linha = ([linha["Data inicio"],linha["Cust_id"],linha["Produto"],"S",str(validar_sand_ajustado),str(validar_prod_ajustado),linha["Go-live"],str(msg)])
                # print(linha)
                novoArquivo.writerow([linha["Data inicio"],linha["Cust_id"],linha["Produto"],"S",str(validar_sand_ajustado),str(validar_prod_ajustado),linha["Go-live"],str(resultado_branded)])
                
                print('Validar Prod = '+str(validar_prod_ajustado))
                print('Validar Sand = '+str(validar_sand_ajustado))
                print('isBranded: ' +str(resultado_branded))
                time.sleep(3)
                print("----------------------")
            except Exception as e:
                novoArquivo.writerow([linha["Data inicio"],linha["Cust_id"],linha["Produto"],"S",str(validar_sand),str(validar_prod),linha["Go-live"],''])
                tokensProblema.writerow([linha["Data inicio"],linha["Cust_id"],linha["Produto"],"S",str(validar_sand),str(validar_prod),linha["Go-live"],''])

                print("ERRO"+e)
                json_final.append({'return': {
                    'exception': e
            }})
        else:
            novoArquivo.writerow([linha["Data inicio"],linha["Cust_id"],linha["Produto"],"N"," "," ",linha["Go-live"],"False"])
            print("----------------------")
     
     except Exception as identifier:
      print("ERRO")
      print(identifier)
      tokensProblema.writerow([linha["Data inicio"],linha["Cust_id"],linha["Produto"],"ERRO",str(validar_sand),str(validar_prod),linha["Go-live"],''])
    shutil.move("welcome_hunting.csv", "/Users/rbarros/Desktop/projetos/Welcome Hunting/sucesso")        
                
def capturarTokenProd(application_id,cust_id):
   
    # data = []
    
    url = "http://api.internal.ml.com/applications/"+application_id+"/credentials?caller.id="+cust_id
    response = requests.get(url)
    # print(str(url))
    response.encoding = "Latin-1"
    comments = json.loads(response.content)
    # print(str(comments['access_token']))
    # access_token = (str(dictor(comments, "0.access_token")))
    
    access_token = (str(comments['access_token']))
    # print(access_token)
    # test_access_token = (str(dictor(comments, "0.test_access_token")))
    test_access_token = (str(comments['test_access_token']))
    # print(access_token)
    # data.append[{'token_prod': access_token,'token_sand': test_access_token}] 
    return access_token

def capturarTokenSand(application_id,cust_id):
   
    url = "http://api.internal.ml.com/applications/"+application_id+"/credentials?caller.id="+cust_id
    response = requests.get(url)
    response.encoding = "Latin-1"
    comments = json.loads(response.content)
    test_access_token = (str(comments['test_access_token']))
    # test_access_token = (str(dictor(comments, "0.test_access_token")))
    # data.append[{'token_prod': access_token,'token_sand': test_access_token}] 
    return test_access_token

def capturarApp(cust_id):
    
    url = "http://api.internal.ml.com/applications/search?owner_id="+cust_id 
    response = requests.get(url)
    response.encoding = "Latin-1"
    comments = json.loads(response.content)
    # print (comments)
    application_id = str(dictor(comments, "0.id"))
    return application_id

def validar(access_token,begin_date,end_date):
    
    data = []
    data_ = []
    # global observacao
    data_validacao = []

    primeira_data = []
    
    try:
        url = "https://api.mercadopago.com/v1/payments/search?access_token="+access_token+"&limit=1000&range=date_created&begin_date="+begin_date+"&end_date="+end_date+"&sort=date_created&criteria=asc" 
        # print (url)
        
        response = requests.get(url)
        response.encoding = "Latin-1"
        comments = json.loads(response.content)
        json_data = json.dumps(comments)
        item_dict = json.loads(json_data)
        # print(str(dictor(comments, "results")))
       
        
        for date_created in range(len(item_dict['results'])):
            
            if(str(dictor(comments, "results."+str(date_created)+".order.type"))!="mercadolibre"):
                
                primeira_data.append(str(date_created))
                
                
                # print(date_created)
                # print(primeira_data[0])
                # print(str(dictor(comments, "results."+str(date_created)+".order.type")))
                data_string = str(dictor(comments, "results."+str(date_created)+".date_created"))
                data_string = data_string[0:10]
                data_string = data_string.replace("-","")
                data_.append(data_string)

        
         

        
        
       
       

        if (response.status_code == 200):
            # print (primeira_data)
            if not primeira_data:
                # print("VAZIO")
                primeira_data.append("None")

            data.append({
            'total': len(data_),
            'datas': Counter(data_),
            'primeira_request': str(dictor(comments, "results."+str(primeira_data[0])+".date_created"))
            

            
        })  
            # print (data)
            return (data)
    except Exception as e:
        data.append({'return': {
            'exception': e
        }})
        return jsonify(data)

    
    return jsonify(data)
    # return"Tudo pronto!"   

def validarV2(access_token,begin_date,end_date):
    
    data = []
    data_ = []
    # global observacao
    data_validacao = []
    primeira_data = []

    
    try:
        url = "https://api.mercadopago.com/v1/payments/search?access_token="+access_token+"&limit=1000&range=date_created&begin_date="+begin_date+"&end_date="+end_date+"&sort=date_created&criteria=asc" 
        # print (url)
        response = requests.get(url)
        response.encoding = "Latin-1"
        comments = json.loads(response.content)
        # print(comments)
        json_data = json.dumps(comments)
        item_dict = json.loads(json_data)
        # print(str(dictor(comments, "results.0")))
       

        if (response.status_code == 200):    
            for date_created in range(len(item_dict['results'])):
                if(str(dictor(comments, "results."+str(date_created)+".order.type"))!="mercadolibre"):
                    # print ((item_dict['results']))
                    primeira_data.append(str(date_created))
                    data_string = str(dictor(comments, "results."+str(date_created)+".date_created"))
                    data_string = data_string[0:10]
                    data_string = data_string.replace("-","")
                    data_.append(data_string)







            if (response.status_code == 200):

                if not primeira_data:
                    # print("VAZIO")
                    primeira_data.append("None")
                # print ("primeira request"+primeira_data[0])
                data = str(dictor(comments, "results."+str(primeira_data[0])+".date_created"))

                return (data)
            else:

                data = str(dictor(comments, "message"))
                return (data)
        else:
            data = str(dictor(comments, "message"))
            print(data)
            return (data)        
    except Exception as e:
        data.append({'return': {
            'exception': e
        }})
        return (data)

    
    return (data)
    # return"Tudo pronto!"   

def lerCsv():
    
    arquivo = open('welcome_hunting.csv')
    linhas = csv.DictReader(arquivo)
    
    return linhas   

def lerBrandeadoCsv():
    
    arquivo = open('brandeado.csv')
    linhas = csv.DictReader(arquivo)
    
    return linhas   

# def lerProduct():
    
#     arquivo = open('/Users/lfeitosa/Documents/Welcome Hunting/lib/id_branded.csv')
#     linhas = csv.DictReader(arquivo)
    
#     return linhas   

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5050))
    # app.run(host='0.0.0.0', port=port, debug=True)
    app.run(host='0.0.0.0', port=port, debug=True)
