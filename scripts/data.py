import requests
import datetime
import calendar
import pandas as pd

# Consult Graphql
class ConsultarGraphql:
    def __init__(self, endpoint:str, query:str, take:str):
        self.endpoint = endpoint
        self.take = take
        self.url = str('https://api.maxiprod.com.br/graphql')
        self.Authorization = '' # insira sua token graphql
        self.query = query

        self.headers = { 'Content-Type':'application/json', 'Authorization': self.Authorization }
        self.data = { 'query':self.query }

        self.response = requests.post(url=self.url, headers=self.headers, json=self.data)

    # Retorna o total de paginações necessárias para a consulta completa
    def totalCount(self):
        if self.response.status_code == 200:
            self.data = self.response.json()
            self.countlines = self.data['data']['notasFiscais']['totalCount']
            self.count = self.countlines / self.take # total de itens / numero requisição por consulta
            self.result = int(self.count) + (1 if self.count % int( self.count ) else 0) # Arrendondando o total de paginações
            return self.result
        else:
            print("A solicitação falhou Graphql falhou: ", self.response.text)

    # retorna todos os itens da query requisitada
    def pushItems(self):
        all_items = []
        totalCount = self.totalCount()
        for skip in range(0, totalCount):
            self.skip_query = self.query.replace('skip: 0',f'skip: {skip * self.take}') # alterando na query o valor de skip, para fazer a paginação completa.
            self.data_skip = { 'query':self.skip_query }
            self.response = requests.post(url=self.url, headers=self.headers, json=self.data_skip)
            if self.response.status_code == 200:
                all_items.extend(self.response.json().get('data', {}).get(self.endpoint, {}).get('items', []))
            else:
                print("A solicitação falhou Graphql falhou: ", self.response.text)
                return None
        return all_items

class analysis(ConsultarGraphql):
    def __init__(self, endpoint:str, query:str, take:str):
        super().__init__(endpoint, query, take)

    # verificando o último dia útil do mês
    def last_business_day_of_month(self, year, month):
        _, last_day = calendar.monthrange(year, month)
        date = datetime.date(year, month, last_day)
        while not date.weekday() < 5:
            date -= datetime.timedelta(days=1)
        return date

    # Analisando o dicionário graphql
    def analysisData(self):
        self.data = self.pushItems()
        DicionatyGeneric = {}
        DicionatyItems = {}
        DicionatyClient = {}
        DicionatyItemsEmail = {}
        valor_exemplo = 0
        DicionatyGenericLastYeaer = {}

        ano_atual = datetime.datetime.now().year
        mes_atual = datetime.datetime.now().month
        ultimo_dia_util = self.last_business_day_of_month(ano_atual, mes_atual) # Último dia útil do mês atual
        lastYaer = datetime.datetime.now().year - 1

        for index in self.data:
            crmRegiao_info = index['destinatarioOuRemetente']['crmRegiao']
            emissaoData = datetime.datetime.fromisoformat(index['emissaoData']).date()

            if emissaoData.month == mes_atual and emissaoData.day >= 1 and emissaoData <= ultimo_dia_util and ano_atual == emissaoData.year:
                if crmRegiao_info is not None:
                    crmRegiao = crmRegiao_info['descricao']
                    valorTotal = index['valorTotal']
                    client = index['destinatarioOuRemetente']['apelido']

                    if crmRegiao not in DicionatyGeneric:
                        DicionatyGeneric[crmRegiao] = valorTotal
                    else:
                        DicionatyGeneric[crmRegiao] += valorTotal

                    if crmRegiao not in DicionatyItems:
                        DicionatyItems[crmRegiao] = {}

                    if client not in DicionatyClient:
                        DicionatyClient[client] = {}

                    if crmRegiao not in DicionatyItemsEmail:
                        DicionatyItemsEmail[crmRegiao] = {}

                    for item in index['itensDaNotaFiscalEmitidaOuRecebida']:
                        grupo = item['item']['grupo']['grupoDescricao']
                        valorItem = item['valorTotalComImpostosExternos']

                        # Adiciona o grupo ao dicionário de grupos da região
                        if grupo not in DicionatyItems[crmRegiao]:
                            DicionatyItems[crmRegiao][grupo] = valorItem
                        else:
                            DicionatyItems[crmRegiao][grupo] += valorItem

                        if grupo not in DicionatyClient[client]:
                            DicionatyClient[client][grupo] = valorItem
                        else:
                            DicionatyClient[client][grupo] += valorItem

                        if 'interno' in grupo.lower():
                            if 'interno' not in DicionatyItemsEmail[crmRegiao]:
                                DicionatyItemsEmail[crmRegiao]['interno'] = valorItem
                            else:
                                DicionatyItemsEmail[crmRegiao]['interno'] += valorItem
                        elif 'externo' in grupo.lower() or 'serviços' in grupo.lower():
                            if 'externo' not in DicionatyItemsEmail[crmRegiao]:
                                DicionatyItemsEmail[crmRegiao]['externo'] = valorItem
                            else:
                                DicionatyItemsEmail[crmRegiao]['externo'] += valorItem
                        else:
                            if 'produto' not in DicionatyItemsEmail[crmRegiao]:
                                DicionatyItemsEmail[crmRegiao]['produto'] = valorItem
                            else:
                                DicionatyItemsEmail[crmRegiao]['produto'] += valorItem

        return DicionatyItemsEmail, DicionatyGeneric, DicionatyItems

def metasAndSellers():
    
    dfMetas = pd.read_csv('./setupFiles/metas.csv' , encoding='utf-8', sep=';')
    numeric_columns = ['meta produto', 'meta serviço externo', 'meta serviço interno']
    dfMetas[numeric_columns] = dfMetas[numeric_columns].apply(lambda x: x.str.replace(',', '.')).astype(float)

    return dfMetas
