# J.A.R.V.I.S - AI Chatbot & Image Generator

This project is a comprehensive submission for AI Bootcamp Week 2 and Task 3. J.A.R.V.I.S is a multimodal AI application that demonstrates advanced prompt engineering techniques for Large Language Models (LLMs) and Diffusion Models (Image Generation) using Streamlit.

## What This Project Does

J.A.R.V.I.S provides several distinct modes of interaction:
1. **Standard Chat**: Switch seamlessly between Gemini, OpenAI, and Llama 3 models while applying different system prompt personas (e.g., Explain Like I'm 5, Sarcastic Robot).
2. **Model A/B Arena**: Test two different LLMs side-by-side with the exact same prompt to evaluate their performance, and cast a vote on the winner.
3. **Prompt Evaluator**: Instead of answering your question, the AI scores and critiques your prompt to help you become a better prompt engineer.
4. **Image Generation**: Enter a prompt, select an art style (e.g., Cyberpunk, Steampunk), choose an aspect ratio, and generate an image using the Hugging Face Inference API (FLUX.1-schnell). Includes a downloadable image gallery and negative prompt support!

*Additional Features*: Action Intents (auto-opening URLs based on intent), full chat history memory, and chat history export.

## How to Run It Locally

1. **Clone the repository** and navigate to the project directory.
2. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Streamlit application**:
   ```bash
   streamlit run main.py
   ```

## How to Add Your API Keys

J.A.R.V.I.S uses environment variables to ensure no API keys are hardcoded.

1. Locate the `.env.example` file and copy it to a new file named `.env`.
   ```bash
   cp .env.example .env
   ```
2. Open the `.env` file and fill in your keys:
   - `HUGGINGFACE_API_KEY`: Get this for free from [Hugging Face Settings -> Access Tokens](https://huggingface.co/settings/tokens).
   - `GEMINI_API_KEY`, `OPENAI_API_KEY`, `GROQ_API_KEY`: Add whichever text models you wish to use. The app adapts to whichever keys are present!

## How to Deploy It

The easiest way to deploy this application is via **Streamlit Community Cloud**:
1. Push your code to a public GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
3. Click **"New App"** and select your repository, branch, and `main.py` file path.
4. Click on **"Advanced Settings"** before deploying.
5. In the "Secrets" text box, paste the contents of your `.env` file (e.g., `HUGGINGFACE_API_KEY="your_key_here"`).
6. Click **Deploy!**

## Known Limitations

- **Image Generation Queue**: Because the application uses the free Hugging Face Inference API, the image generation model (FLUX.1-schnell) may sometimes be "loading" or busy if you haven't used it in a while, resulting in a temporary 503 error. Waiting a few seconds and trying again resolves this.
