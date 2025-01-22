import tkinter as tk
from tkinter import ttk, scrolledtext
import asyncio
from models import GeminiService
import json

class TherapyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Therapy Chat")
        self.root.geometry("800x600")
        
        # Initialize Gemini service (you'll need to add your API key)
        self.gemini = GeminiService("")
        
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Create chat display
        self.chat_display = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, height=20)
        self.chat_display.pack(expand=True, fill='both')
        
        # Create input frame
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill='x', pady=5)
        
        # Create input field
        self.input_field = ttk.Entry(self.input_frame)
        self.input_field.pack(side='left', expand=True, fill='x', padx=(0, 5))
        
        # Create send button
        self.send_button = ttk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side='left')
        
        # Create ABC chart button
        self.abc_button = ttk.Button(self.input_frame, text="Generate ABC Chart", command=self.generate_abc)
        self.abc_button.pack(side='left', padx=5)
        
        # Create ABC chart display
        self.abc_display = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, height=10)
        self.abc_display.pack(expand=True, fill='both', pady=5)
        
        # Bind enter key to send message
        self.input_field.bind("<Return>", lambda e: self.send_message())

    def send_message(self):
        message = self.input_field.get().strip()
        if message:
            self.chat_display.insert(tk.END, f"You: {message}\n")
            self.input_field.delete(0, tk.END)
            self.chat_display.see(tk.END)
            
            # Get AI response asynchronously
            self.root.after(100, self.get_ai_response, message)

    async def async_get_response(self, message):
        response = await self.gemini.chat_with_system(message)
        return response

    def get_ai_response(self, message):
        # Run async code in a separate thread
        async def process():
            response = await self.async_get_response(message)
            self.chat_display.insert(tk.END, f"Therapist: {response}\n")
            self.chat_display.see(tk.END)
        
        asyncio.run(process())

    def generate_abc(self):
        async def process():
            chart = await self.gemini.get_abc_chart()
            try:
                # Try to format as JSON if possible
                formatted_chart = json.dumps(json.loads(chart), indent=2)
            except:
                formatted_chart = chart
                
            self.abc_display.delete(1.0, tk.END)
            self.abc_display.insert(tk.END, formatted_chart)
        
        asyncio.run(process())

def main():
    root = tk.Tk()
    app = TherapyApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()