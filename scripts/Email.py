import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from smtplib import SMTP
import datetime
from time import sleep

fisrtDayMonth = datetime.date.today().replace(day=1).strftime('%d/%m/%Y')
today = datetime.date.today().strftime('%d/%m/%Y')

def sendEmail_faturamento(ListData, ListDataItems):

    smtp_server = "" #Insira seu smtp_server.
    port = 587 #Verificar caso seja necessário
    receiver_email = [] #Emails que receberão as notificações, lembrando que os vendedores serão inseridos aqui.
    sender_email = "" #Insira sua conta hotmail.
    password = "" #Insira sua senha

    # Função para colocar segurança ssl no e-mail
    context = ssl.create_default_context()

    # Verificando se realmente existe um email para enviar
    if ListData[1] != 'nan':
        receiver_email.insert(0, ListData[1])

    if ListData[2] != 'nan':
        receiver_email.insert(1, ListData[2])

    # definindo parametros
    region = ListData[0]
    ValorProdutos = ListData[3]
    ValorServInterno = ListData[4]
    ValorServExterno = ListData[5]
    metaProdutos = ListData[6]
    metaServInterno = ListData[7]
    metaServExterno = ListData[8]
    
    percentualProdutos = round((ValorProdutos/metaProdutos * 100), 3) if metaProdutos != 0 else (ValorProdutos/1 * 100)
    percentualInterno = round((ValorServInterno/metaServInterno * 100), 3) if metaServInterno != 0 else (ValorServInterno/1 * 100)
    percentualExterno = round((ValorServExterno/metaServExterno * 100), 3) if metaServExterno != 0 else (ValorServExterno/1 * 100)

    cellStyleProdutos = 'background-color: #56ff4a;' if percentualProdutos >= 100 else ''
    cellStyleInterno = 'background-color: #56ff4a;' if percentualInterno >= 100 else ''
    cellStyleExterno = 'background-color: #56ff4a;' if percentualExterno >= 100 else ''
        
    print(region ,receiver_email)

    try:
        
        # Configuração padrão para enviar e-mail e fazer o login
        server = SMTP(smtp_server, port)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)

        # Montado o e-mail
        message = MIMEMultipart('related')
        message["Subject"] = f"Faturamento - {region} de {fisrtDayMonth} até {today}"   
        message["From"] = sender_email                                                         
        message["To"] = ", ".join(receiver_email)

        html = f"""<html>
            <head>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        color: #333;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        text-align: center;
                    }}
                    .container {{
                        width: 100%;
                        margin: 0 auto;
                        background: #fff;
                        heigth: 100vh;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
                    }}
                    .header {{
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        color: #333;
                    }}

                    p {{
                        font-size: 13px;
                        font-weight: 500;
                        margin-top: 50px;
                        text-transform: uppercase;
                    }}

                    .table_content {{
                        margin-bottom: 50px;
                        margin-top: 45px;
                    }}

                    table {{
                        width: 50%;
                        border-collapse: collapse;
                    }}
                    th, td {{
                        text-align: center;
                        border: 1px solid #ddd;
                        padding: 8px;
                    }}
                    th {{
                        background-color: #ffbf00;
                        color: white;
                    }}

                    .footer {{
                        text-align: center;
                        font-size: 12px;
                        color: #666;
                        padding-top: 20px;
                    }}
                </style>
            </head>
            <body>

            <img src="cid:HeaderImage" alt="Header Image">

            <p style="font-weight: 500"; font-size: 2rem;>Segue abaixo valores de faturamento de produtos e de serviços na sua região.</p>

            <div class="container">

                <div class="table_content">
                    <table>
                        <tr>
                            <th style="{cellStyleProdutos}" colspan="2">Produtos</th>
                        </tr>
                        <tr>
                            <td>Meta</td>
                            <td>{"R$ {:_.2f}".format(metaProdutos).replace(".",",").replace("_",".")}</td>
                        </tr>
                        <tr>
                            <td>Alcançado</td>
                            <td>{"R$ {:_.2f}".format(ValorProdutos).replace(".",",").replace("_",".")}</td>
                        </tr>
                        <tr>
                            <td>Percentual</td>
                            <td>{percentualProdutos}%</td>
                        </tr>

                        <tr>
                            <th style="{cellStyleInterno}" colspan="2">Serviços internos</th>
                        </tr>
                        <tr>
                            <td>Meta</td>
                            <td>{"R$ {:_.2f}".format(metaServInterno).replace(".",",").replace("_",".")}</td>
                        </tr>
                        <tr>
                            <td>Alcançado</td>
                            <td>{"R$ {:_.2f}".format(ValorServInterno).replace(".",",").replace("_",".")}</td>
                        </tr>
                        <tr>
                            <td>Percentual</td>
                            <td>{percentualInterno}%</td>
                        </tr>
                        <tr>
                            <th style="{cellStyleExterno}" colspan="2">Serviços externos</th>
                        </tr>
                        <tr>
                            <td>Meta</td>
                            <td>{"R$ {:_.2f}".format(metaServExterno).replace(".",",").replace("_",".")}</td>
                        </tr>
                        <tr>
                            <td>Alcançado</td>
                            <td>{"R$ {:_.2f}".format(ValorServExterno).replace(".",",").replace("_",".")}</td>
                        </tr>
                        <tr>
                            <td>Percentual</td>
                            <td>{percentualExterno}%</td>
                        </tr>
                    </table>

                    <div class="content__areagrapchs" style="background-color: #f4f4f4;">
                        <p style="background-color: #f4f4f4; font-size: 2rem; margin-top: 2rem; font-weight: 500;">Faturamento por grupo de produtos</p>
                        <table>
                            <tr>
                                <th colspan="3">FATURAMENTO POR GRUPO</th>
                            </tr>
                            {"".join([f"<tr><td>{key}</td><td>{'R$ {:_.2f}'.format(value).replace('.',',').replace('_','.')}</td><td>{(value/sum(ListDataItems.values())) * 100:.2f}%</td></tr>" for key, value in ListDataItems.items()])}
                        </table> 
                    </div>
                </div>
            </div>
            <div class="footer">
                Regards,<br>
                Anndre Juan<br>
                Serra-ES Brasil<br>
                Whatsapp: +55 27 99322-0909<br>
                Email: anndret26@gmail.com<br>
            </div>
            </body>
            </html>
        """

        HeaderImage = f'./SetupFiles/headerImg.png'

        #Incorporando as imagens ao HTML do email
        html_with_images = html.replace('<img src="cid:HeaderImage" alt="Header Image">', '<img src="cid:HeaderImage" alt="Header Image" width="614">')
        
        # Criando a parte MIMEText para o email com o HTML modificado
        part = MIMEText(html_with_images, "html")
        message.attach(part)

        # Anexando a segunda imagem (header_image) ao email
        fp_header = open(HeaderImage, 'rb')
        msgHeaderImage = MIMEImage(fp_header.read())
        fp_header.close()
        msgHeaderImage.add_header('Content-ID', 'HeaderImage')
        message.attach(msgHeaderImage)

        # FUNÇÃO QUE ENVIA O E-MAIL
        server.sendmail(sender_email, receiver_email, message.as_string())
        sleep(2)

    except Exception as e:

        # Caso dê algum erro, printa na tela o que aconteceu
        print(e)
    finally:

        # No final de tudo, quita do servidor
        server.quit()
    print('E-mails Enviados com Êxito!')
