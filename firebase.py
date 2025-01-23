import firebase_admin
from firebase_admin import credentials, firestore

class FirebaseChat:
    def __init__(self):
        # Initialize Firebase
        cred = credentials.Certificate(r"/etc/secrets/firebase.json")
        firebase_admin.initialize_app(cred)
        
        # Firestore client
        self.db = firestore.client()

    def fetch_chats(self, phone_number, session_id):
        chats_ref = self.db.collection("chats").document(phone_number).collection("chats").document(session_id).collection("chat")
        
        # Fetch chats ordered by timestamp
        chats = chats_ref.order_by("timestamp").stream()
        
        # Role mapping
        role_map = {
            "user": "user",
            "bot": "model",
            "assistant": "model",
            "system": "model"
        }
        
        gemini_history = []
        for chat in chats:
            chat_data = chat.to_dict()
            # Skip if no text content
            if not chat_data.get('text'):
                continue
                
            # Map the role
            role = role_map.get(chat_data.get('role', 'user'), 'user')
            
            # Add formatted message to history
            gemini_history.append({
                "role": role,
                "parts": chat_data['text']
            })

        return gemini_history



# # Example usage
# fb = FirebaseChat()
# phone_number = "8319212398"
# session_id = "session6"
# chats = fb.fetch_chats(phone_number, session_id)

# for chat in chats:
#     print(chat)
