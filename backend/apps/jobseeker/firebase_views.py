from django.http import JsonResponse
from firebase.firebase_config import db

def test_firestore(request):
    if db is None:
        return JsonResponse({
            "status": "error",
            "message": "Firebase is not configured or service key is missing."
        }, status=503)

    db.collection("test").add({
        "name": "Prasad",
        "message": "Hello Firebase!"
    })

    return JsonResponse({
        "status": "success"
    })