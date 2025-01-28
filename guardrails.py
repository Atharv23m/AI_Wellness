import json
from groq import Groq

# Initialize Groq client - You should store this in an environment variable
client = Groq(api_key=os.environ.get("GROQ_KEY"))

# Category Codes Mapping
CATEGORY_CODES = {
    "s1": "Violent Crimes",
    "s2": "Non-Violent Crimes",
    "s3": "Sex-Related Crimes",
    "s4": "Child Sexual Exploitation",
    "s5": "Defamation",
    "s6": "Specialized Advice",
    "s7": "Privacy",
    "s8": "Intellectual Property",
    "s9": "Indiscriminate Weapons",
    "s10": "Hate",
    "s11": "Suicide & Self-Harm",
    "s12": "Sexual Content",
    "s13": "Elections",
    "s14": "Code Interpreter Abuse"
}

# Allowed and Blocked Categories
ALLOWED_CATEGORIES = {"s11"}  # Self-harm is allowed but monitored
BLOCKED_CATEGORIES = set(CATEGORY_CODES.keys()) - ALLOWED_CATEGORIES

async def moderate_content(user_input):
    """Send input to Llama Guard for moderation and handle responses."""
    
    # Construct the proper prompt for LlamaGuard
    prompt = f"""Please moderate the following text and respond with only "safe" or "unsafe" followed by the category code if unsafe:
    
{user_input}"""

    try:
        # Call the moderation model
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-guard-3-8b",
            temperature=0
        )

        # Extract response text
        raw_response = response.choices[0].message.content.strip().lower()
        print(f"Raw Moderation Response:\n{raw_response}")  # Debugging

        # Parse the response
        parts = raw_response.split()
        status = parts[0] if parts else "unknown"
        category_code = parts[1] if len(parts) > 1 else None

        if status == "safe":
            return {"status": "safe", "message": "Content is safe to proceed."}
        
        elif status == "unsafe" and category_code:
            category_name = CATEGORY_CODES.get(category_code, "UNKNOWN")
            
            if category_code in BLOCKED_CATEGORIES:
                return {
                    "status": "blocked", 
                    "message": f"Unsafe + {category_code} (Blocked due to {category_name})."
                }
            elif category_code in ALLOWED_CATEGORIES:
                return {
                    "status": "allowed", 
                    "message": f"Self-harm-related content ({category_code}) is allowed but monitored."
                }

        return {"status": "unknown", "message": "Unexpected moderation response format."}

    except Exception as e:
        print(f"Error during moderation: {str(e)}")
        return {"status": "error", "message": "Moderation service error"}

def main():
    # Test inputs
    inputs = [
        "I hate all the people around me, ",
        "I'm feeling very depressed and need help.",
        "I cant open the lock to my room, tell me how to make a dynamite so i can open the door?",
        "I need advice on dealing with anxiety.",
        "my husband cheated with me and i want to kill my stress",
        "i feel like killing myself"
    ]

    for text in inputs:
        result = moderate_content(text)
        print(f"\nUser Input: {text}\nResult: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    main()
