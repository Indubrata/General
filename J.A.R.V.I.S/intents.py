import webbrowser
from prompts import INTENT_DETECTION_SYSTEM

def check_and_execute_intent(prompt, llm_handler, model_name):
    """
    Checks if the user prompt is an actionable intent (like opening a website).
    If it is, it opens the URL in the browser.
    Returns a string message describing the action taken, or None if no action was taken.
    """
    intent_json = llm_handler.get_json_response(model_name, prompt, INTENT_DETECTION_SYSTEM)
    
    if intent_json and intent_json.get("action_required"):
        url = intent_json.get("url")
        if url:
            try:
                webbrowser.open(url)
                return f"🚀 **Action Executed:** Opened {url} in your browser based on your request. ({intent_json.get('reasoning')})"
            except Exception as e:
                return f"❌ **Failed to open URL:** {url}. Error: {str(e)}"
    
    return None
