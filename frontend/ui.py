"""
frontend/ui.py

All Streamlit UI components for StudyBuddy AI:
- Page layout and styling
- Tabs and input widgets
- Chat interface and result displays

This module should NOT contain any AI or business logic.
"""

import streamlit as st
from typing import List, Dict, Any, Tuple


def setup_page() -> None:
    """Configure the Streamlit page and apply modern styling."""
    try:
        st.set_page_config(
            page_title="StudyBuddy AI",
            page_icon="📚",
            layout="wide",
            initial_sidebar_state="collapsed",
        )
    except Exception:
        # set_page_config can only be called once; ignore if already set
        pass

    st.markdown(
        """
        <style>
        /* COMPLETELY HIDE SIDEBAR */
        [data-testid="stSidebar"] {
            display: none !important;
        }
        
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        
        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }
        
        /* Expand main content to full width */
        .block-container {
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 1200px !important;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Import modern font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Global styling */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Main container styling */
        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 2rem 1rem;
        }
        
        /* Premium title with gradient */
        .main-header {
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-align: center;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            letter-spacing: -0.5px;
        }
        
        /* Badge/pill next to title */
        .title-badge {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-left: 0.5rem;
            vertical-align: middle;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        }
        
        /* Card styling for tabs */
        .stTabs {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
            margin-top: 2rem;
        }
        
        /* Tab button styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            background-color: transparent;
            transition: all 0.3s ease;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
        }
        
        /* Button styling */
        .stButton>button {
            width: 100%;
            border-radius: 10px;
            font-weight: 600;
            padding: 0.6rem 1.2rem;
            border: none;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }
        
        .stButton>button[kind="primary"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Input fields styling */
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea,
        .stSelectbox>div>div>select {
            border-radius: 10px;
            border: 2px solid #e0e0e0;
            padding: 0.75rem;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .stTextInput>div>div>input:focus,
        .stTextArea>div>div>textarea:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        /* Chat message styling */
        .stChatMessage {
            background: white;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.75rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        /* Chat input at bottom */
        .stChatInputContainer {
            border-top: 2px solid #e0e0e0;
            padding-top: 1rem;
            background: white;
        }
        
        /* File uploader styling */
        .stFileUploader {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 1rem;
            border: 2px dashed #d0d0d0;
        }
        
        /* Image styling */
        .stImage {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Info/warning/error boxes */
        .stAlert {
            border-radius: 10px;
            border-left-width: 4px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> Dict[str, Any]:
    """
    Render the sidebar with app info, API key input, and model selection.
    
    Returns:
        Dict with "api_key" and "model" keys
    """
    import os
    
    with st.sidebar:
        st.header("📚 StudyBuddy AI")
        st.markdown(
            """
            **Your friendly AI learning assistant.**

            - 💬 Text chat tutor
            - 🖼️ Image doubt solver
            - 📚 Explain your own notes

            **Backend:** OpenRouter AI
            """
        )
        st.markdown("---")
        
        # Check if API key exists in environment (from .env or system env)
        api_key_env = os.getenv("OPENROUTER_API_KEY", "").strip()
        api_key_from_env = bool(api_key_env)
        
        # Show status if key is loaded from .env
        if api_key_from_env:
            st.success("✅ API key loaded from `.env` file")
        
        # API Key input (optional - only needed if not in .env/secrets)
        api_key_sidebar = st.text_input(
            "OpenRouter API Key (optional)" if api_key_from_env else "OpenRouter API Key",
            type="password",
            help="Enter your OpenRouter API key to override .env/secrets. Get one at https://openrouter.ai/keys",
            placeholder="sk-or-v1-..." if not api_key_from_env else "Leave empty to use .env key",
        )
        
        # Check Streamlit secrets
        api_key_secrets = ""
        try:
            api_key_secrets = st.secrets.get("OPENROUTER_API_KEY", "").strip()
        except Exception:  # noqa: BLE001
            pass
        
        # Determine final API key (precedence: sidebar > env > secrets)
        # Sidebar key takes priority if provided
        if api_key_sidebar and api_key_sidebar.strip():
            api_key = api_key_sidebar.strip()
        elif api_key_env:
            api_key = api_key_env
        elif api_key_secrets:
            api_key = api_key_secrets
        else:
            api_key = ""
        
        # Model selection
        available_models = [
            "xiaomi/mimo-v2-flash:free",
            "mistralai/devstral-2-2512:free",
            "tngtech/deepseek-r1t2-chimera:free",
        ]
        
        model = st.selectbox(
            "Model",
            available_models,
            index=0,
            help="Select the AI model to use. Free models are available.",
        )
        
        st.markdown("---")
        st.markdown(
            """
            💡 **Get API Key:**
            - Visit [openrouter.ai/keys](https://openrouter.ai/keys)
            - Create a free account
            - Copy your API key
            """
        )
    
    return {
        "api_key": api_key,
        "model": model,
    }


def render_main_header() -> None:
    """Render the main page header with premium styling."""
    st.markdown(
        '''
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 class="main-header">
                📚 StudyBuddy AI
                <span class="title-badge">AI Learning Assistant</span>
            </h1>
        </div>
        ''',
        unsafe_allow_html=True,
    )


def get_tabs() -> Tuple[Any, Any, Any]:
    """Create and return the three main tabs."""
    return st.tabs(
        [
            "💬 Text Chat Tutor",
            "🖼️ Image Doubt Solver",
            "📚 Explain My Notes",
        ]
    )


def render_text_chat_tab(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Render the Text Chat Tutor tab with ChatGPT-style interface.

    Returns a dict with:
        - student_level
        - task_type
        - user_input (from chat_input)
        - clear_clicked
    """
    st.header("💬 Text Chat Tutor")
    st.markdown("Ask questions or enter a topic, and I'll help you learn!")

    # Settings row
    col1, col2, col3 = st.columns([3, 3, 2])
    with col1:
        student_level = st.selectbox(
            "Student Level",
            ["Beginner", "Intermediate", "Advanced"],
            help="Select your current learning level",
        )
    with col2:
        task_type = st.selectbox(
            "Task Type",
            ["Explain", "Examples", "Practice Questions", "Quiz", "Study Plan"],
            help="What kind of help do you need?",
        )
    with col3:
        clear_clicked = st.button("🗑️ Clear Chat", use_container_width=True)

    st.markdown("---")

    # Chat message history
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        images = msg.get("images", [])
        
        with st.chat_message(role):
            if images:
                # Filter out invalid URLs - only keep valid http/https strings
                valid_images = [
                    url for url in images 
                    if isinstance(url, str) and url.startswith("http")
                ]
                
                if valid_images:
                    # Display valid images in columns
                    if len(valid_images) == 1:
                        st.image(valid_images[0], use_container_width=True)
                    elif len(valid_images) == 2:
                        cols = st.columns(2)
                        for idx, img_url in enumerate(valid_images):
                            with cols[idx]:
                                st.image(img_url, use_container_width=True)
                    else:
                        # 3 or more images
                        cols = st.columns(3)
                        for idx, img_url in enumerate(valid_images[:3]):
                            with cols[idx]:
                                st.image(img_url, use_container_width=True)
                else:
                    st.info("No valid images found.")
            
            st.markdown(content)

    # Chat input fixed at bottom
    user_input = st.chat_input("Ask a question or enter a topic...")

    return {
        "student_level": student_level,
        "task_type": task_type,
        "user_input": user_input,
        "clear_clicked": clear_clicked,
    }


def render_image_solver_tab() -> Dict[str, Any]:
    """
    Render the Image Doubt Solver tab and return user interactions.

    Returns a dict with:
        - uploaded_file
        - is_question
        - solve_clicked
    """
    st.header("🖼️ Image Doubt Solver")
    st.markdown(
        "Upload an image of your notes, textbook, or a problem. "
        "I'll read the text and explain or solve it step by step."
    )
    
    st.markdown("<br>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["jpg", "jpeg", "png"],
        help="Upload a clear JPG, JPEG, or PNG image",
    )

    if uploaded_file is not None:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    is_question = st.checkbox(
        "This is a question/problem to solve",
        value=True,
        help="Uncheck if it's just notes or theory to explain",
    )

    solve_clicked = st.button("🔍 Solve & Explain", type="primary", use_container_width=True)

    return {
        "uploaded_file": uploaded_file,
        "is_question": is_question,
        "solve_clicked": solve_clicked,
    }


def render_explain_notes_tab() -> Dict[str, Any]:
    """
    Render the Explain My Notes tab and return user interactions.

    Returns a dict with:
        - mode ("text" or "image")
        - notes_text
        - uploaded_file
        - explain_clicked
    """
    st.header("📚 Explain My Notes")
    st.markdown(
        "Paste your notes or upload an image. I'll explain **only** what you provide, "
        "without adding extra knowledge unless you ask."
    )
    
    st.markdown("<br>", unsafe_allow_html=True)

    mode_label = st.radio(
        "Choose input method",
        ["📝 Paste Text", "🖼️ Upload Image"],
        horizontal=True,
    )
    mode = "text" if "Paste" in mode_label else "image"

    notes_text = ""
    uploaded_file = None

    if mode == "text":
        notes_text = st.text_area(
            "Paste your notes here",
            placeholder="Paste your notes or study material. The AI will only explain this content.",
            height=250,
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload an image of your notes",
            type=["jpg", "jpeg", "png"],
            help="Upload a clear image of your notes or textbook page",
            key="notes_image_uploader",
        )
        if uploaded_file is not None:
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                st.image(uploaded_file, caption="Uploaded Notes", use_container_width=True)

    explain_clicked = st.button("📖 Explain Notes", type="primary", use_container_width=True)

    return {
        "mode": mode,
        "notes_text": notes_text,
        "uploaded_file": uploaded_file,
        "explain_clicked": explain_clicked,
    }


def show_warning(message: str) -> None:
    """Display a warning message."""
    st.warning(message)


def show_error(message: str) -> None:
    """Display an error message."""
    st.error(message)


def show_info(message: str) -> None:
    """Display an informational message."""
    st.info(message)


def show_markdown_section(title: str, content: str) -> None:
    """Display a titled markdown section."""
    st.markdown("---")
    if title:
        st.subheader(title)
    st.markdown(content)

