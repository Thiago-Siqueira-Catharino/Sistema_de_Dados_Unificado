from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from pymongo import MongoClient
from bson import ObjectId
import os, json, re

#paradas do google drive, apenas para teste:
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.discovery import build
import io

def salvar_arq(arquivo):
    service_account_file = 'client_secret_988952397907-5m0r2q39cncojrjd2tqcs17ome0hroh4.apps.googleusercontent.com.json'
    scopes = ['https://www.googleapis.com/auth/drive.file']
    creds = Credentials.from_service_account_file(service_account_file, scopes=scopes)
    
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name':arquivo.name}
    file_bytes = arquivo.read()
    mime_type = arquivo.content_type
    media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=mime_type)

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    service.permissions().create(
        fileId=file.get('id'),
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    link = f"https://drive.google.com/uc?id={file.get('id')}&export=download"
    return link

client = MongoClient(settings.MONGO_URI)
db = client.get_database("SDU")

# Create your views here.
def search_data(request):
    if request.method == "POST":
        body = json.loads(request.body.decode("utf-8"))
        cpf = body.get("cpf")
    elif request.method == "GET":
        cpf = request.GET.get("cpf")
    else:
        return JsonResponse({"error":"Metódo inválid"}, status = 405)

    if cpf:
        cpf_tratado = re.sub(r"\D", "", cpf)
    if len(cpf_tratado) == 11:
        query = {"cpf":cpf_tratado}
    else: return JsonResponse({"error":"Parametro inválido"}, status = 400)
    data = list(db["exames"].find(query, {"_id": 0}))

    return JsonResponse(data, safe=False)

#@ensure_csrf_cookie
@csrf_exempt
def receive_data(request):
    if request.method == 'POST':
        nome = request.POST.get("name")
        cpf = request.POST.get("cpf")
        arquivo = request.FILES['arquivo']

        link = salvar_arq(arquivo)

        return JsonResponse({'nome':nome, 'cpf':cpf, 'link':link})
    