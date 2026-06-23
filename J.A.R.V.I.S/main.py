import streamlit as st
from llm_handler import LLMHandler
from prompts import PROMPT_MODES, PROMPT_EVALUATOR_SYSTEM
from intents import check_and_execute_intent
from image_handler import ImageHandler
from image_styles import IMAGE_STYLES, DEFAULT_NEGATIVE_PROMPT

# Configure Streamlit page
st.set_page_config(page_title="Prompt Engineering Chatbot", page_icon="🤖", layout="wide")

import base64

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# Load background if it exists
bg_base64 = get_base64_of_bin_file('/home/indubrata/.gemini/antigravity/brain/0d8f6fde-5161-4575-84a6-63ddb478f587/ui_background_1781176515768.png')
bg_css = f"""
    body {{
        background-color: #000000 !important;
        background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url("data:image/jpeg;base64,{bg_base64}");
        background-size: contain;
        background-position: top center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background: transparent !important;
    }}
""" if bg_base64 else ""

# Load custom icon if it exists
icon_base64 = get_base64_of_bin_file('/home/indubrata/TechFiles/TDA_Bootcamp/AI/Week2/icon.png')
icon_css = f"""
    /* Hide default SVGs only in the sidebar toggle button */
    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="stSidebarCollapseControl"] svg {{
        display: none !important;
    }}
    
    /* Set custom icon as background */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseControl"] {{
        background-image: url("data:image/png;base64,{icon_base64}") !important;
        background-size: 28px 28px !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
    }}
""" if icon_base64 else ""

# Inject Custom CSS
st.markdown(f"""
    <style>
    {bg_css}
    {icon_css}
    
    /* Move the Running indicator and Stop button to the bottom right */
    [data-testid="stStatusWidget"] {{
        position: fixed !important;
        bottom: 25px !important;
        right: 40px !important;
        z-index: 1000 !important;
        background-color: rgba(0,0,0,0.5);
        border-radius: 10px;
        padding: 5px;
    }}

    /* Global Text Color */
    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp label {{
        color: #E0F7FA !important;
    }}

    /* Chat Messages base styling */
    [data-testid="stChatMessage"] {{
        border-radius: 15px !important;
        padding: 15px !important;
        margin-bottom: 15px !important;
        color: #E0F7FA !important;
        width: fit-content;
        max-width: 80%;
    }}

    /* Right-align User Messages (using the injected .user-msg div) */
    [data-testid="stChatMessage"]:has(.user-msg) {{
        flex-direction: row-reverse;
        margin-left: auto !important;
        background-color: rgba(10, 40, 50, 0.85) !important;
        border: 1px solid #005f73 !important;
        border-bottom-right-radius: 0px !important;
    }}

    /* Left-align Assistant Messages (using the injected .assistant-msg div) */
    [data-testid="stChatMessage"]:has(.assistant-msg) {{
        margin-right: auto !important;
        background-color: rgba(0, 200, 220, 0.2) !important;
        border: 1px solid #00ACC1 !important;
        border-bottom-left-radius: 0px !important;
    }}

    /* Sidebar Styling - Aggressively targeting all inner wrappers */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebarContent"] {{
        background-color: transparent !important;
        border-right: 1px solid rgba(0, 172, 193, 0.3) !important;
    }}
    
    /* Top-Right Menu / Popovers (if referring to the 3-dots menu) */
    ul[data-testid="stMenu"], 
    div[role="menu"], div[role="dialog"] {{
        background-color: rgba(0, 15, 20, 0.4) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid #00ACC1 !important;
        color: #E0F7FA !important;
    }}
    
    /* Fully transparent chat input bar */
    [data-testid="stChatInput"], .stChatInputContainer, div[data-testid="stChatInput"] {{
        background-color: transparent !important;
        background: transparent !important;
        backdrop-filter: none !important;
        border: 1px solid #00ACC1 !important;
        border-radius: 20px !important;
    }}
    [data-testid="stChatInput"] textarea, .stChatInputContainer textarea {{
        color: #E0F7FA !important;
        background-color: transparent !important;
    }}

    /* Selectboxes and text areas */
    .stSelectbox > div > div, .stTextArea textarea {{
        background-color: transparent !important;
        border: 1px solid #00ACC1 !important;
        color: #E0F7FA !important;
    }}
    
    /* Shift main content exactly 38px down from previous state */
    .block-container {{
        margin-top: 1px !important;
        padding-top: 2rem !important;
    }}
    
    /* Remove default solid background behind the chat input */
    .stApp > header {{
        background: transparent !important;
    }}
    
    /* Bottom padding container for chat input */
    [data-testid="stBottomBlockContainer"],
    [data-testid="stBottom"],
    .stBottom {{
        background: transparent !important;
        background-color: transparent !important;
    }}
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_llm_handler():
    return LLMHandler()

@st.cache_resource
def get_image_handler():
    try:
        return ImageHandler()
    except ValueError:
        return None

handler = get_llm_handler()
available_models = handler.get_available_models()
image_handler = get_image_handler()

# Initialize session state for memory and app state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "arena_results" not in st.session_state:
    st.session_state.arena_results = []
if "image_gallery" not in st.session_state:
    st.session_state.image_gallery = []

def export_chat(messages):
    text = "# Chat History\n\n"
    for m in messages:
        role = "User" if m["role"] == "user" else "Assistant"
        text += f"**{role}:**\n{m['content']}\n\n"
    return text

# Sidebar configuration
with st.sidebar:
    st.title("J.A.R.V.I.S")
    
    app_mode = st.radio("App Mode", ["Standard Chat", "Model A/B Arena", "Prompt Evaluator", "🖼️ Image Generation"])
    
    st.divider()
    
    st.markdown("### Export")
    if st.session_state.messages:
        chat_str = export_chat(st.session_state.messages)
        st.download_button(
            label="Download Chat History",
            data=chat_str,
            file_name="chat_history.md",
            mime="text/markdown"
        )
    
    st.divider()
    if not available_models:
        st.error("No models available. Please set your API keys in the .env file.")
        st.stop()

# Inject the App Name into the top ribbon bar
st.markdown(f"""
    <div style="position: fixed; top: 15px; left: 50%; transform: translateX(-50%); z-index: 100000; font-size: 1.5rem; font-weight: 800; color: #00E5FF; letter-spacing: 3px;">
        J.A.R.V.I.S
    </div>
""", unsafe_allow_html=True)

# Helper to get the current system prompt
def get_system_prompt(mode_selection):
    if mode_selection == "Custom":
        return st.text_area("Enter your custom system prompt:", value="You are a helpful assistant.", height=100)
    return PROMPT_MODES[mode_selection]


if app_mode == "Standard Chat":    
    col1, col2 = st.columns(2)
    with col1:
        selected_model = st.selectbox("Select Model", available_models)
    with col2:
        prompt_mode = st.selectbox("Prompt Mode", list(PROMPT_MODES.keys()))
        
    system_prompt = get_system_prompt(prompt_mode)
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            cls = "user-msg" if message["role"] == "user" else "assistant-msg"
            st.markdown(f"<div class='{cls}'></div> {message['content']}", unsafe_allow_html=True)

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(f"<div class='user-msg'></div> {prompt}", unsafe_allow_html=True)
            
        # First, check for action intents
        intent_result = check_and_execute_intent(prompt, handler, selected_model)
        if intent_result:
            with st.chat_message("assistant"):
                st.markdown(f"<div class='assistant-msg'></div> {intent_result}", unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": intent_result})
        else:
            # Generate LLM response
            with st.chat_message("assistant"):
                # Use st.write_stream for the typewriter effect
                st.markdown("<div class='assistant-msg'></div>", unsafe_allow_html=True)
                stream = handler.generate_response_stream(selected_model, prompt, system_prompt, st.session_state.messages[:-1])
                response = st.write_stream(stream)
            
            # Store assistant response
            st.session_state.messages.append({"role": "assistant", "content": response})

elif app_mode == "Model A/B Arena":
    st.markdown("Compare how different models respond to the **exact same prompt** and system instructions.")
    
    col1, col2 = st.columns(2)
    with col1:
        model_a = st.selectbox("Model A", available_models, index=0)
    with col2:
        model_b = st.selectbox("Model B", available_models, index=1 if len(available_models) > 1 else 0)
        
    prompt_mode = st.selectbox("Prompt Mode", list(PROMPT_MODES.keys()))
    system_prompt = get_system_prompt(prompt_mode)
    
    if prompt := st.chat_input("Enter a prompt to test both models..."):
        st.markdown(f"**User:** {prompt}")
        
        # We don't use history for the arena to keep the test clean
        empty_history = []
        
        res_col1, res_col2 = st.columns(2)
        
        response_a = ""
        response_b = ""
        
        with res_col1:
            st.subheader(f"Model A: {model_a}")
            stream_a = handler.generate_response_stream(model_a, prompt, system_prompt, empty_history)
            response_a = st.write_stream(stream_a)
            
        with res_col2:
            st.subheader(f"Model B: {model_b}")
            stream_b = handler.generate_response_stream(model_b, prompt, system_prompt, empty_history)
            response_b = st.write_stream(stream_b)
            
        st.session_state.arena_results.append({
            "prompt": prompt,
            "model_a": model_a,
            "model_b": model_b,
            "response_a": response_a,
            "response_b": response_b
        })
        
    # Voting Mechanism (Display at the bottom)
    if st.session_state.arena_results:
        st.divider()
        st.markdown("### Vote for the Winner")
        vote_col1, vote_col2, vote_col3 = st.columns(3)
        with vote_col1:
            if st.button("👈 Model A is better", use_container_width=True):
                st.success("Voted for Model A!")
        with vote_col2:
            if st.button("🤝 It's a Tie", use_container_width=True):
                st.info("Voted Tie!")
        with vote_col3:
            if st.button("Model B is better 👉", use_container_width=True):
                st.success("Voted for Model B!")

elif app_mode == "Prompt Evaluator":
    st.markdown("Instead of answering your question, the AI will evaluate your prompt and help you improve it.")
    
    evaluator_model = st.selectbox("Evaluator Model", available_models)
    
    if prompt := st.chat_input("Enter the prompt you want to evaluate..."):
        st.markdown("### Your Original Prompt")
        st.info(prompt)
        
        st.markdown("### Evaluation")
        stream = handler.generate_response_stream(evaluator_model, prompt, PROMPT_EVALUATOR_SYSTEM, [])
        st.write_stream(stream)

elif app_mode == "🖼️ Image Generation":
    st.markdown("Enter a prompt and select an art style to generate an image.")
    
    provider = st.radio("Image Engine Provider", ["Hugging Face (Free)", "Stability AI (Core)"], horizontal=True)
    if provider == "Hugging Face (Free)" and not image_handler.hf_api_key:
        st.warning("HUGGINGFACE_API_KEY is missing from .env. The API may not work.")
    if provider == "Stability AI (Core)" and not image_handler.stability_api_key:
        st.warning("STABILITY_API_KEY is missing from .env. The API may not work.")
        
    col1, col2 = st.columns([3, 1])
    with col1:
        img_prompt = st.text_input("Describe the image you want to see:")
    with col2:
        img_style = st.selectbox("Art Style", list(IMAGE_STYLES.keys()))
        
    with st.expander("Advanced Settings"):
        col3, col4 = st.columns(2)
        with col3:
            img_size = st.radio("Image Ratio", ["Square (1024x1024)", "Landscape (1024x576 / 1792x1024)", "Portrait (576x1024 / 1024x1792)"])
        with col4:
            negative_prompt = st.text_area("Negative Prompt (What to avoid):", value=DEFAULT_NEGATIVE_PROMPT)
            
    if st.button("Generate Image", type="primary", use_container_width=True):
        if not img_prompt:
            st.warning("Please enter a prompt first.")
        else:
            with st.spinner(f"Generating image with {provider}... This may take a few seconds."):
                try:
                    # Apply style modifier
                    style_modifier = IMAGE_STYLES.get(img_style, "")
                    final_prompt = f"{img_prompt}, {style_modifier}" if style_modifier and style_modifier != "" else img_prompt
                    
                    # Parse dimensions
                    w, h = 1024, 1024
                    if "Landscape" in img_size:
                        w, h = 1024, 576
                    elif "Portrait" in img_size:
                        w, h = 576, 1024
                        
                    # Extract the pure provider name
                    prov_name = "Stability AI (Core)" if "Stability" in provider else "Hugging Face"
                        
                    # Generate
                    image = image_handler.generate_image(prompt=final_prompt, provider=prov_name, width=w, height=h)
                    
                    # Save to gallery
                    st.session_state.image_gallery.insert(0, {
                        "prompt": img_prompt,
                        "style": img_style,
                        "final_prompt": final_prompt,
                        "image": image
                    })
                    
                except Exception as e:
                    st.error(f"Failed to generate image: {str(e)}")
                    
    # Display Gallery
    if st.session_state.image_gallery:
        st.divider()
        st.markdown("### Image Gallery")
        
        # Display the most recent image prominently
        latest = st.session_state.image_gallery[0]
        st.image(latest["image"], caption=f"{latest['prompt']} ({latest['style']})", use_container_width=True)
        
        # Allow downloading
        import io
        img_byte_arr = io.BytesIO()
        latest["image"].save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        st.download_button(
            label="Download Latest Image",
            data=img_bytes,
            file_name="generated_image.png",
            mime="image/png"
        )
        
        # Show older images in smaller columns
        if len(st.session_state.image_gallery) > 1:
            st.markdown("#### Previous Generations")
            cols = st.columns(3)
            for i, item in enumerate(st.session_state.image_gallery[1:]):
                col = cols[i % 3]
                with col:
                    st.image(item["image"], caption=item["prompt"], use_container_width=True)
