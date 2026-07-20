from django.http import JsonResponse
from firebase.firebase_config import db

def test_firestore(request):
    db.collection("test").add({
        "name": "Prasad",
        "message": "Hello Firebase!"
    })

    return JsonResponse({
        "status": "success"
    })