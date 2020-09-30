import requests
import time
import json
import csv
import logging
from datetime import datetime, timedelta


# f= open("relatorio.csv","w+")
# f.write('cust,detalhe,is_branded?'+"\r\n")



class Brandeado:

    def __init__(self):
        self.url_app = 'http://api.internal.ml.com/applications/search?owner_id='
        self.url_mkt = 'http://api.internal.ml.com/marketplaces/search?app_id='
        self.url_credencial = "http://api.internal.ml.com/applications/"
        self.url_payments = 'http://api.mp.internal.ml.com/v1/payments/search'

        self.url_preference = 'http://api.internal.ml.com/checkout/preferences/'


        self.hoje = datetime.now()
    #CALCULA A SUBTRAÇAO DAS DATAS
    def tratamentoData(self,qtd_dias):
        # global self.hoje
        data_hora = self.hoje.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        conversao = datetime.strptime(data_hora, '%Y-%m-%dT%H:%M:%S.%f')
        conversao = conversao - timedelta(days=int(qtd_dias))
        # conversao_string = conversao.strftime('%Y-%m-%d%H:%M:%S.%f')
        # print(conversao_string)
        # return conversao_string
        return conversao
    
    #VERIFICAR SE É BRANDED
    def isBranded(self,cust_id):
        
        # global hoje
        # response_credentials = requests.get(url_credencial+str(application_id)+"/credentials?caller.id="+str(cust_id['cust_id']))
        # response_credentials_json = response_credentials.json()
        begin_date = self.tratamentoData(int(10))
        end_date = self.hoje.strftime('%d/%m/%Y %H:%M:%S')
    
        limit = '100'
        
        header = {'x-caller-scopes': 'admin',
                 'Content-Type': 'application/x-www-form-urlencoded'}
    
        payload = {'collector.id': cust_id,
                    'operation_type': 'regular_payment', #-- ESTAVA DANDO INTERNAL SERVER ERROR
                    'limit': limit,
                    'criteria': 'desc',
                    'range': 'date_created',
                    'marketplace': 'NONE',
                    'begin_date': begin_date.strftime('%Y-%m-%dT%H:%M:%S.999-04:00'),
                    'end_date': self.hoje.strftime('%Y-%m-%dT%H:%M:%S.999-04:00')}
    
        #time.sleep(5)
        while True:
            response_payments = requests.get(self.url_payments, headers=header, data=payload)
            response_payments_json = response_payments.json()
            if response_payments.ok:
                break
            else:
                print('Time out ao realizar consultar, esperando 10 segundos.')
                time.sleep(1)
        product_id = None
        branded_pref = 0
        branded_link = 0
        api = 0
        retorno = 0
        #alterado aqui tbm
        if int(response_payments_json['paging']['total']) > 0:
            for payment in response_payments_json['results']:
                retorno = 0
                try:
                    #print(payment['id'])
                    #print(payment['internal_metadata'])
                    if(payment['internal_metadata']['preference']['id']):
                        response_preference = requests.get(self.url_preference + payment['internal_metadata']['preference']['id'], headers=header)
                        response_preference = response_preference.json()
                        retorno = 1
                        try:
                            if response_preference['product_id'] is not None:
                                #print(payment['id'])
                                #print(response_preference['product_id'])
                                product_id = response_preference['product_id']
                                if self.productIdBranded(product_id):
                                    retorno = 2
                        except:
                            #branded_pref = branded_pref + 1
                            #print('Erro ao consultar product_id')
                            pass
                except:
                    #api = api + 1
                    #print('Erro ao consultar preference')
                    pass

                if retorno == 2:
                    branded_link = branded_link + 1
                elif retorno == 1:
                    branded_pref = branded_pref + 1
                elif retorno == 0:
                    api = api + 1
            total = len(response_payments_json['results'])
            print(total)
            if total == 0:
                return 3

            print('link: ' + str(branded_link * 100 / total))
            print('pre: ' + str(branded_pref * 100 / total))
            print('api: ' + str(api * 100 / total))

            percent_link = 30
            percent_pref = 10
            if (branded_link * 100 / total) > percent_link:
                return 2
            elif (branded_pref * 100 / total) > percent_pref:
                return 1
            return 0
            
        else:
            # print('NAO TEM PAGAMENTO - '+ cust_id)    
            return 3#,'NAO TEM PAGAMENTO (POSSIVELMENT MKT)'

    
    
    # VERIFICA QUE TEM PAGAMENTOS NO MARKETPLACE
    def havePayments(self,application_id, cust_id):
        response_credentials = requests.get(self.url_credencial+str(application_id)+"/credentials?caller.id="+str(cust_id['cust_id']))
        response_credentials_json = response_credentials.json()
    
        response_payments = requests.get(self.url_payments+response_credentials_json['access_token'])
        response_payments_json = response_payments.json()
    
        if int(response_payments_json['paging']['total']) > 0:
            return True
        else:
            return False
    
    # APLICACOES
    def applications(self,cust_id):
        response = requests.get(self.url_app+cust_id)
        response_json = response.json()
        return response_json
    
    # VERIFICA OS CUSTS
    def lerCsv(self):
        arquivo = open('data.csv')
        linhas = csv.DictReader(arquivo)
        return linhas
    
    # VERIFICA SE É MARKETPLACE
    def isMarketplace(self,app_id):
        response = requests.get(self.url_mkt+str(app_id))
        response_json = response.json()
        if response_json['results'] == []:
            return False
        else:
            return True

    #alterado aqui
    def productIdBranded(self,payment_product):

        products = 'BGPQ8U6H3OU001NR2HVGBGPQ97BFP71G01LFUEU0BGPQ8BMH3OU001NR2HV0BQTVV5SDTG7G01IMCUBGBQTVVTKBFOCG01H0F340BEH9099AT85G01M2J78G'
        if payment_product in products:
            return True
        return False

    
    # custs = []
    # custs = lerCsv()
    

    
# brand = Brandeado()
# resultado, msg = brand.isBranded('624863523')
# if resultado:
#     print(resultado)
#     print(msg)
# else:    
#     print(msg)
#     print(resultado)
            
    
    
    
    
    