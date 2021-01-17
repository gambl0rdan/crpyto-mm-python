import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


def connect_to_firebase():
    project_id = 'crypto-trade-5ce43'
    # Use the application default credentials
    # cred = credentials.ApplicationDefault()
    service_acc = 'firebase-adminsdk-oewn7@crypto-trade-5ce43.iam.gserviceaccount.com'
    cred = credentials.Certificate("firebaseCredentials.json")
    # firebase_admin.initialize_app(cred)
    firebase_admin.initialize_app(cred, {
        'projectId': project_id,
    })

    db = firestore.client()
    print(f'{datetime.datetime.now()} firebase connected {db}')
    return db