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
        branded = 0
        #alterado aqui tbm
        if int(response_payments_json['paging']['total']) > 0:
            for payment in response_payments_json['results']:
                try:
                    #print(payment['id'])
                    #print(payment['internal_metadata'])
                    if(payment['internal_metadata']['preference']['id']):
                        response_preference = requests.get(self.url_preference + payment['internal_metadata']['preference']['id'], headers=header)
                        response_preference = response_preference.json()
                        branded = 1
                        if response_preference['product_id'] is not None:
                            print(payment['id'])
                            print(response_preference['product_id'])
                            product_id = response_preference['product_id']
                except:
                    try:
                        product_id = payment['product_id']
                    except:
                        product_id = '0'
                if payment['operation_type'] == 'regular_payment' and branded == 1:
                    try:
                        retorno = self.productIdBranded(product_id)
                        if retorno > branded:
                            branded = retorno
                            if branded == 2:
                                return branded
                        self.productIdBranded(product_id)#, ('PRODUCT_ID BRANDEADO - '+cust_id)
                    except:
                        pass
            return branded
        else:
            # print('NAO TEM PAGAMENTO - '+ cust_id)    
            return 0#,'NAO TEM PAGAMENTO (POSSIVELMENT MKT)'
        # print('NAO TEM PREFERENCIA - '+ cust_id)
        return 0#, ('NAO TEM PRODUCT_ID BRANDEADO - '+ cust_id)
    
    
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
        linhas = self.lerProduct()
        final = 0
        for product_id in linhas:
            if product_id['product_id'] == payment_product and product_id['description'] == 'link_painel':
                final = 2
                return final
            elif product_id['product_id'] == payment_product:
                final = 1
                return final
        return final
    

        
    def lerProduct(self):
        try:
        
            arquivo = open('/Users/rbarros/Desktop/projetos/Welcome Hunting/lib/id_branded.csv')
            linhas = csv.DictReader(arquivo)
            return linhas     
        except:
            import traceback
            print('?', "| "+"\033[31m"+"Erro na leitura do welcome_hunting(verifique o log para detalhes)!"+"\033[0;0m\n"+str(traceback.format_exc()))
            logging.error(traceback.format_exc())
    
            
    
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
            
    
    
    
    
    