from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from pymongo import MongoClient
from bson import ObjectId
import os, json

client = MongoClient(settings.MONGO_URI)
db = client.get_database("SDU")

# Create your views here.
def search_data(request):
    data = db["exames"].find({}, {"_id": 0})
    print(db.list_collection_names())
    print(list(data))

    return JsonResponse(list(data), safe=False)