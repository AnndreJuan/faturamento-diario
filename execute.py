from scripts.data import analysis, metasAndSellers
from scripts.Email import sendEmail_faturamento

def executeFaturamento():

    # consulta query - Exemplo
    notasFiscais = f"""
    {{
    notasFiscais(
        take: 500
        skip: 0
        where: {{
        and: [
            {{ estado: {{ eq: EMITIDA }} }},
            {{ estadoConfiguravel: {{ descricao: {{ neq: "Não comissionar" }} }} }},
            {{ nfeFinalidadeDeEmissao: {{ eq: NFE_NORMAL }} }},
            {{ entradaOuSaida: {{ eq: SAIDA }} }},
            {{ operacaoFiscal: {{ tipo: {{ eq: FATURAMENTO }} }} }},
        ]
        }}
    ) {{
        totalCount
        items {{
        numero
        emissaoData
        valorTotal

        destinatarioOuRemetente {{
            apelido
            crmRegiao {{
            descricao
            }}
        }}

        itensDaNotaFiscalEmitidaOuRecebida {{
            valorTotalComImpostosExternos
            item {{
            codigo
            grupo {{
                grupoDescricao
            }}
            }}
        }}
        }}
    }}
    }}
    """

    DicionatyItemsEmail, DicionatyGeneric, DicionatyItems = analysis(endpoint="notasFiscais", query=notasFiscais, take=500).analysisData()
    metaSellers = metasAndSellers()

    for region, values in DicionatyItemsEmail.items():
        
        ValorProdutos = values.get('produto', 0)
        ValorServInterno = values.get('interno', 0)
        ValorServExterno = values.get('externo', 0)
        
        try:
            # Caso não tenha a região da lista de metas, será ignorado e não enviará o email...
            metaProdutos = metaSellers.loc[metaSellers['regiao'] == region, 'meta produto'].iloc[0]
        except:
            continue
        metaServInterno = metaSellers.loc[metaSellers['regiao'] == region, 'meta serviço interno'].iloc[0]
        metaServExterno = metaSellers.loc[metaSellers['regiao'] == region, 'meta serviço externo'].iloc[0]
        
        emailVendInterno = metaSellers.loc[metaSellers['regiao'] == region, 'email interno'].iloc[0]
        emailVendExterno = metaSellers.loc[metaSellers['regiao'] == region, 'email externo'].iloc[0]

        items = str(region), str(emailVendInterno), str(emailVendExterno), float(ValorProdutos), float(ValorServInterno), float(ValorServExterno), float(metaProdutos), float(metaServInterno), float(metaServExterno)
        
        if region in DicionatyItems:
            descriptions_items = DicionatyItems[region]

        # enviando email
        sendEmail_faturamento(items, descriptions_items)

if __name__ == '__main__':
    executeFaturamento()