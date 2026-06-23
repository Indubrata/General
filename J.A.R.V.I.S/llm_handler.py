import os
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq
import json

load_dotenv()

class LLMHandler:
    def __init__(self):
        # Initialize clients
        if os.getenv("GEMINI_API_KEY"):
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.gemini_available = True
        else:
            self.gemini_available = False
            
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None

    def get_available_models(self):
        models = []
        if self.gemini_available:
            models.append("Gemini 3.5 Flash")
        if self.groq_client:
            models.append("Llama 3.3 70B Versatile (Groq)")
            models.append("OpenAI GPT-OSS-120B (Groq)")
        return models

    def generate_response_stream(self, provider_model, prompt, system_prompt, history=None):
        if history is None:
            history = []
            
        if provider_model.endswith("(Groq)"):
            yield from self._stream_groq(provider_model, prompt, system_prompt, history)
        elif "Gemini" in provider_model:
            yield from self._stream_gemini(provider_model, prompt, system_prompt, history)
        else:
            yield "Model not supported or API key missing."

    def _stream_gemini(self, model_name, prompt, system_prompt, history):
        # Map nice names to API names
        model_id = "gemini-3.5-flash"
        
        try:
            model = genai.GenerativeModel(
                model_name=model_id,
                system_instruction=system_prompt
            )
            
            # Convert history to Gemini format
            formatted_history = []
            for msg in history:
                role = "user" if msg["role"] == "user" else "model"
                formatted_history.append({"role": role, "parts": [msg["content"]]})
                
            chat = model.start_chat(history=formatted_history)
            response = chat.send_message(prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"Error with Gemini API: {str(e)}"


    def _stream_groq(self, model_name, prompt, system_prompt, history):
        if "GPT-OSS-120B" in model_name:
            model_id = "openai/gpt-oss-120b"
        else:
            model_id = "llama-3.3-70b-versatile"
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": prompt})
        
        try:
            stream = self.groq_client.chat.completions.create(
                model=model_id,
                messages=messages,
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error with Groq API: {str(e)}"
            
    def get_json_response(self, provider_model, prompt, system_prompt):
        # A non-streaming helper for things like intent detection
        history = []
        full_response = ""
        for chunk in self.generate_response_stream(provider_model, prompt, system_prompt, history):
            full_response += chunk
        
        # Try to parse JSON from the response
        try:
            # Clean up markdown if the LLM wrapped it in ```json ... ```
            clean_str = full_response.strip()
            if clean_str.startswith("```json"):
                clean_str = clean_str[7:]
            if clean_str.startswith("```"):
                clean_str = clean_str[3:]
            if clean_str.endswith("```"):
                clean_str = clean_str[:-3]
            return json.loads(clean_str.strip())
        except Exception as e:
            return {"action_required": False, "url": None, "reasoning": f"Failed to parse JSON. Error: {str(e)}. Raw: {full_response}"}
