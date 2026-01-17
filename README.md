# 📚 StudyBuddy AI (SDG 4 – Quality Education)

A modular, local-first learning assistant built with **Streamlit** and **Ollama**.  
No API keys or external billing are required: all AI calls go to your local Ollama server.

The app provides:
- **Tab 1 – Text Chat Tutor**: conversational tutor with student level and task type controls
- **Tab 2 – Image Doubt Solver**: upload an image → OCR → AI explains or solves
- **Tab 3 – Explain My Notes**: paste text or upload an image → AI explains only that content

---

## 🧱 Architecture Overview

The project is split into 5 clear layers:

- **FRONTEND** (`frontend/ui.py`): Streamlit UI (tabs, inputs, buttons, chat display)
- **BACKEND** (`backend/controller.py`): app logic and routing between tabs/services
- **MODEL / AI LAYER** (`model/llm_client.py`): calls to local Ollama models via HTTP
- **PROMPT LAYER** (`prompts/templates.py`): prompt templates for different tasks
- **UTILITIES / DATA LAYER** (`utils/*.py`): OCR, validation, formatting, and session state

Project structure:

```text
StudyBuddyAI/
  app.py                     # Minimal entrypoint – wires Streamlit to controller
  requirements.txt
  README.md

  frontend/
    __init__.py
    ui.py                    # All Streamlit UI components

  backend/
    __init__.py
    controller.py            # High-level app logic & routing

  model/
    __init__.py
    llm_client.py            # Ollama HTTP client and model selection

  prompts/
    __init__.py
    templates.py             # Prompt builders for all modes

  utils/
    __init__.py
    ocr.py                   # OCR via pytesseract
    formatters.py            # Markdown/text formatting helpers
    validators.py            # Input validation helpers
    state.py                 # st.session_state chat handling
```

---

## ✅ Prerequisites

- **Python** 3.8 or higher
- **Ollama** installed and running locally
- **Tesseract OCR** installed (for OCR using `pytesseract`)

### 1) Install Ollama

Download and install Ollama from the official site:

- `https://ollama.com/`

After installing, make sure the Ollama service is running (usually automatic).

### 2) Pull the model

Open a terminal and run:

```bash
ollama pull llama3.2
```

If you prefer (or if `llama3.2` is unavailable), you can also:

```bash
ollama pull mistral
```

The app will try `llama3.2` first and fall back to `mistral` if needed.

### 3) Install Tesseract OCR

On **Windows**:

- Download the Tesseract installer from:
  - `https://github.com/tesseract-ocr/tesseract`
- Install it and ensure “Add to PATH” is enabled, or manually add the install path (e.g. `C:\Program Files\Tesseract-OCR`) to your system PATH.

On **Linux/macOS**:

- Use your package manager, for example:

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS (Homebrew)
brew install tesseract
```

### 4) Install Python dependencies

From the `StudyBuddyAI` directory:

```bash
pip install -r requirements.txt
```

This installs:
- `streamlit` – UI framework
- `requests` – HTTP client for Ollama
- `pillow` – image handling
- `pytesseract` – OCR wrapper for Tesseract

---

## 🚀 Run the Streamlit App

From the `StudyBuddyAI` directory, run:

```bash
streamlit run app.py
```

Your browser should open at `http://localhost:8501` (or similar).

Make sure:
- Ollama is running (`ollama serve` if needed)
- The model `llama3.2` (or `mistral`) has been pulled

---

## 🧭 How Each Tab Works

### 1. 💬 Text Chat Tutor

- Choose **Student Level**: Beginner / Intermediate / Advanced
- Choose **Task Type**:
  - Explain
  - Examples
  - Practice Questions
  - Quiz
  - Study Plan
- Type your question or topic and send.
- Chat history is stored in `st.session_state` via `utils/state.py`.
- The prompt is built by `prompts/templates.py` and sent to Ollama via `model/llm_client.py`.

### 2. 🖼️ Image Doubt Solver

- Upload a **JPG/PNG** image of notes, textbook content, or a problem.
- A checkbox lets you specify whether it is a **question/problem** or just **notes/theory**.
- `utils/ocr.py` uses Tesseract (via `pytesseract`) to extract text.
- The extracted text is fed into a tailored prompt, then to Ollama.
- The app shows both the extracted text and the AI’s explanation/solution.

### 3. 📚 Explain My Notes

- Choose:
  - **Paste Text** – paste your notes directly, or
  - **Upload Image** – upload a clear image of your notes.
- For text, the prompt is built with a **strict “no extra info” rule**:
  - The AI explains and clarifies only what is present in the notes.
- For image, OCR extracts text first, then the same “explain-only” logic is applied.

---

## 🔒 Error Handling & Robustness

- All key operations (LLM calls, OCR, parsing) use `try/except` with user-friendly errors.
- Input validation via `utils/validators.py`:
  - Non-empty text
  - Reasonable length
  - Valid image types (JPG/PNG)
- If OCR fails or finds no text, the app guides the user to try a clearer image.
- If the LLM cannot be reached, the user is told to check that Ollama is installed, running, and the models are pulled.

---

## 🧩 Extending the App

- Add more task types to the **Text Tutor** by editing `prompts/templates.py`.
- Plug in new models by adjusting `DEFAULT_MODEL` / `FALLBACK_MODEL` in `model/llm_client.py`.
- Add new tabs or features by extending `frontend/ui.py` and wiring them through `backend/controller.py`.

---

Made for **SDG 4 – Quality Education**, enabling local, privacy-friendly AI-assisted learning. 

# 📚 StudyBuddy AI

A beginner-friendly AI learning assistant built with Streamlit and Google Gemini API. This application supports SDG 4: Quality Education by providing accessible, personalized learning support.

## 🌟 Features

### 1. Text Chat Tutor 💬
- Interactive chatbot for asking questions and learning topics
- Customizable by student level (Beginner/Intermediate/Advanced)
- Multiple task types: Explain, Examples, Practice Questions, Quiz, Study Plan
- Persistent chat history using session state
- Clear chat functionality

### 2. Image Doubt Solver 🖼️
- Upload images of notes, textbooks, or problems
- Get step-by-step solutions for questions
- Simple explanations of educational content
- Supports JPG, JPEG, and PNG formats

### 3. Explain My Notes 📚
- Paste text or upload images of your notes
- Get explanations that stay strictly within your provided content
- No additional information unless explicitly requested
- Perfect for understanding your own study materials

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key (get it from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API key (choose one method):

   **Method 1: Environment Variable (Recommended)**
   ```bash
   # Windows (PowerShell)
   $env:GEMINI_API_KEY="your-api-key-here"
   
   # Windows (CMD)
   set GEMINI_API_KEY=your-api-key-here
   
   # Linux/Mac
   export GEMINI_API_KEY="your-api-key-here"
   ```

   **Method 2: Sidebar Input**
   - Run the app and enter your API key in the sidebar

4. Run the application:
```bash
streamlit run app.py
```

5. Open your browser and navigate to the URL shown in the terminal (usually `http://localhost:8501`)

## 📁 Project Structure

```
StudyBuddyAI/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── prompts.py                  # Prompt templates for different modes
└── services/
    └── gemini_client.py       # Gemini API client helper functions
```

## 🔧 Configuration

### API Key Management

The app supports two methods for API key input:

1. **Environment Variable**: Set `GEMINI_API_KEY` in your environment
2. **Sidebar Input**: Enter the key in the app's sidebar (password-protected)

The environment variable takes precedence if both are set.

## 💡 Usage Tips

- **Text Chat Tutor**: Select your level and task type before asking questions for best results
- **Image Doubt Solver**: Ensure images are clear and readable for better analysis
- **Explain My Notes**: Use this when you want explanations limited to your specific content

## 🛠️ Technical Details

- **Framework**: Streamlit
- **AI Model**: Google Gemini 1.5 Flash
- **Library**: google-generativeai
- **Image Processing**: Pillow (PIL)

## ⚠️ Error Handling

The application includes robust error handling for:
- Missing or invalid API keys
- API failures
- Image processing errors
- Invalid user inputs

## 📝 License

This project is created for educational purposes in support of SDG 4: Quality Education.

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📧 Support

For issues or questions, please check the error messages in the app or review the API key configuration.

---

Made with ❤️ for quality education (SDG 4)
