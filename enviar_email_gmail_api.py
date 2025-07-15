import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os
import csv

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def autenticar():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def criar_mensagem(destinatario, assunto, corpo):
    mensagem = MIMEText(corpo)
    mensagem['to'] = destinatario
    mensagem['subject'] = assunto
    raw = base64.urlsafe_b64encode(mensagem.as_bytes())
    return {'raw': raw.decode()}

def enviar_email(servico, mensagem):
    envio = servico.users().messages().send(userId='me', body=mensagem).execute()
    print('✅ E-mail enviado! ID da mensagem:', envio['id'])

def carregar_contatos(arquivo_csv):
    contatos = []
    with open(arquivo_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            contatos.append(row)
    return contatos

def carregar_template(caminho_template):
    with open(caminho_template, 'r', encoding='utf-8') as file:
        return file.read()
    
def main():
    creds = autenticar()
    servico = build('gmail', 'v1', credentials=creds)

    contatos = carregar_contatos('contatos.csv')
    template = carregar_template('template_email.txt')

    for contato in contatos:
        corpo_personalizado = template.format(nome=contato['nome'])
        mensagem = criar_mensagem(
            destinatario=contato['email'],
            assunto='Mensagem Personalizada',
            corpo=corpo_personalizado
        )
        enviar_email(servico, mensagem)

if __name__ == '__main__':
    main()
