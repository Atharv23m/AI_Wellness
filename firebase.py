import firebase_admin
from firebase_admin import credentials, firestore

class FirebaseChat:
    def __init__(self):
        # Initialize Firebase
        cred = credentials.Certificate(r"/etc/secrets/firebase.json")
        firebase_admin.initialize_app(cred)
        
        # Firestore client
        self.db = firestore.client()

    def add_abc_chart(self, phone_number,  abc_chart):
        abc_ref = self.db.collection("abc").document(phone_number)
        timestamp = firestore.SERVER_TIMESTAMP
        
        # Add each ABC entry with timestamp
        for entry in abc_chart:
            abc_ref.collection("entries").add({
            "a": entry["activatingEvent"],
            "b": entry["belief"],
            "c": entry["consequence"],
            "timestamp": timestamp
            })

    def fetch_abc_chart(self, phone_number):
        abc_ref = self.db.collection("abc").document(phone_number)
        entries = abc_ref.collection("entries").stream()
        
        abc_list = []
        for entry in entries:
            entry_data = entry.to_dict()
            abc_list.append({
                "activatingEvent": entry_data["a"],
                "belief": entry_data["b"],
                "consequence": entry_data["c"],
                "timestamp": entry_data["timestamp"]
            })
        
        return abc_list

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

# # Test data
# abc_data = [
#     {
#         "activatingEvent": "Failed an exam",
#         "belief": "I'm not smart enough",
#         "consequence": "Feeling depressed"
#     },
#     {
#         "activatingEvent": "Friend didn't respond",
#         "belief": "They don't like me",
#         "consequence": "Anxiety and withdrawal"
#     }
# ]

# # Add entries
# phone_number = "1234567"
# # fb.add_abc_chart(phone_number, abc_data)

# # Fetch and print entries
# results = fb.fetch_abc_chart(phone_number)
# for entry in results:
#     print(f"A: {entry['activatingEvent']}")
#     print(f"B: {entry['belief']}")
#     print(f"C: {entry['consequence']}")
#     print("---")


# # Example usage
# fb = FirebaseChat()
# phone_number = "8319212398"
# session_id = "session6"
# chats = fb.fetch_chats(phone_number, session_id)

# for chat in chats:
#     print(chat)
