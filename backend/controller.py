"""
backend/controller.py

Application controller layer for StudyBuddy AI.

Responsibilities:
- Initialize app layout via the frontend UI module
- Orchestrate interactions between UI, LLM model, OCR, prompts, and state
- Contain all high-level application logic and routing between tabs
"""

from typing import Any, Dict
import os

import streamlit as st

from frontend import ui
from model.llm_client import generate_llm_response
from prompts.templates import (
    build_text_tutor_prompt,
    build_image_solver_prompt,
    build_explain_notes_text_prompt,
    build_explain_notes_image_prompt,
)
from utils.ocr import extract_text_from_image
from utils.state import (
    init_chat_state,
    get_chat_history,
    add_chat_message,
    clear_chat_history,
    get_messages,
    add_message,
)
from utils.validators import validate_text_input, validate_image_file
from utils.image_fetcher import detect_image_request, extract_query, fetch_images


def _resolve_openrouter_api_key(sidebar_key: str) -> str:
    """
    Resolve OpenRouter API key from multiple sources in safe priority order:
    1) Sidebar input (if provided and non-empty)
    2) Environment variable (.env loaded into env): OPENROUTER_API_KEY
    3) Streamlit secrets: OPENROUTER_API_KEY
    
    Returns empty string if no key found.
    """
    # 1) Sidebar override (highest priority)
    if sidebar_key and sidebar_key.strip():
        return sidebar_key.strip()

    # 2) Environment variable (from .env or system env)
    env_key = os.getenv("OPENROUTER_API_KEY", "")
    if env_key and env_key.strip():
        return env_key.strip()

    # 3) Streamlit secrets (for deployment)
    try:
        secret_key = st.secrets.get("OPENROUTER_API_KEY", "")
        if secret_key and secret_key.strip():
            return secret_key.strip()
    except Exception:  # noqa: BLE001
        pass

    return ""


def _handle_text_chat_tab(api_key: str, model: str) -> None:
    """Controller for the Text Chat Tutor tab with ChatGPT-style interface."""
    messages = get_messages()
    ui_data: Dict[str, Any] = ui.render_text_chat_tab(messages)

    if ui_data.get("clear_clicked"):
        clear_chat_history()
        st.rerun()
        return

    user_input = ui_data.get("user_input")
    if user_input:
        # Validate input
        is_valid, error_msg = validate_text_input(user_input, field_name="question/topic")
        if not is_valid:
            ui.show_warning(error_msg)
            return

        student_level = ui_data.get("student_level", "Beginner")
        task_type = ui_data.get("task_type", "Explain")

        # Chat history for OpenRouter (before adding the new user message)
        chat_history_for_llm = messages

        # Add user message to chat
        add_message("user", user_input)

        # Check if user is requesting an image
        if detect_image_request(user_input):
            query = extract_query(user_input)

            with st.spinner("🔍 Searching for images..."):
                image_urls, source = fetch_images(query, limit=3)

            if image_urls:
                # Generate a brief text response along with images
                info_prompt = (
                    f"Provide a brief (2-3 sentence) informative response about: {query}. "
                    f"Keep it concise since images will also be shown."
                )

                try:
                    with st.spinner("💡 Generating explanation..."):
                        text_response = generate_llm_response(
                            prompt=info_prompt,
                            api_key=api_key,
                            model=model,
                            chat_history=chat_history_for_llm,
                        )
                except Exception:  # noqa: BLE001
                    text_response = f"Here are images related to {query}."

                # Add assistant message with images
                source_note = f"\n\n*Images from {source.title()}*" if source != "none" else ""
                response_content = f"{text_response}{source_note}"
                add_message("assistant", response_content, images=image_urls)
            else:
                # If image fetch fails, provide text-only response
                add_message(
                    "assistant",
                    "I couldn't find images for your request. Let me provide a text explanation instead.",
                )

                # Generate regular text response
                prompt = build_text_tutor_prompt(
                    user_input=user_input,
                    student_level=student_level,
                    task_type=task_type,
                    chat_history=get_chat_history(),
                )

                try:
                    with st.spinner("🤔 Thinking..."):
                        response = generate_llm_response(
                            prompt=prompt,
                            api_key=api_key,
                            model=model,
                            chat_history=chat_history_for_llm,
                        )
                    add_message("assistant", response)
                except Exception as exc:  # noqa: BLE001
                    # Don't expose full error details - show user-friendly message
                    error_msg = str(exc)
                    if "401" in error_msg or "authentication" in error_msg.lower() or "invalid" in error_msg.lower():
                        ui.show_error("❌ Authentication failed. Please check your API key in the .env file.")
                    else:
                        ui.show_error(f"❌ Something went wrong while talking to the AI. Please try again.")
                    return
        else:
            # Regular text response (no images requested)
            prompt = build_text_tutor_prompt(
                user_input=user_input,
                student_level=student_level,
                task_type=task_type,
                chat_history=get_chat_history(),
            )

            try:
                with st.spinner("🤔 Thinking..."):
                    response = generate_llm_response(
                        prompt=prompt,
                        api_key=api_key,
                        model=model,
                        chat_history=chat_history_for_llm,
                    )
            except Exception as exc:  # noqa: BLE001
                # Don't expose full error details - show user-friendly message
                error_msg = str(exc)
                if "401" in error_msg or "authentication" in error_msg.lower() or "invalid" in error_msg.lower():
                    ui.show_error("❌ Authentication failed. Please check your API key in the .env file.")
                else:
                    ui.show_error(f"❌ Something went wrong while talking to the AI. Please try again.")
                return

            add_message("assistant", response)
            # Also add to legacy chat history for compatibility with prompt building
            add_chat_message(user_input=user_input, assistant_response=response)

        st.rerun()


def _handle_image_solver_tab(api_key: str, model: str) -> None:
    """Controller for the Image Doubt Solver tab."""
    ui_data: Dict[str, Any] = ui.render_image_solver_tab()
    uploaded_file = ui_data.get("uploaded_file")
    is_question = ui_data.get("is_question", True)

    if not ui_data.get("solve_clicked"):
        return

    is_valid, error_msg = validate_image_file(uploaded_file)
    if not is_valid:
        ui.show_warning(error_msg)
        return

    try:
        with st.spinner("🔍 Reading text from image..."):
            image_bytes = uploaded_file.read()
            ocr_text = extract_text_from_image(image_bytes)
    except Exception as exc:  # noqa: BLE001
        ui.show_error(f"❌ Could not read the image: {exc}")
        return

    if not ocr_text or not ocr_text.strip():
        ui.show_warning("I couldn't detect any readable text in the image. Please try a clearer photo.")
        return

    prompt = build_image_solver_prompt(ocr_text=ocr_text, is_question=is_question)

    try:
        with st.spinner("🧠 Analyzing and generating explanation..."):
            response = generate_llm_response(
                prompt=prompt,
                api_key=api_key,
                model=model,
            )
    except Exception as exc:  # noqa: BLE001
        # Don't expose full error details - show user-friendly message
        error_msg = str(exc)
        if "401" in error_msg or "authentication" in error_msg.lower() or "invalid" in error_msg.lower():
            ui.show_error("❌ Authentication failed. Please check your API key in the .env file.")
        else:
            ui.show_error(f"❌ Something went wrong while talking to the AI. Please try again.")
        return

    combined = f"### Extracted Text\n\n{ocr_text}\n\n---\n\n### AI Explanation\n\n{response}"
    ui.show_markdown_section("📝 Explanation", combined)


def _handle_explain_notes_tab(api_key: str, model: str) -> None:
    """Controller for the Explain My Notes tab."""
    ui_data: Dict[str, Any] = ui.render_explain_notes_tab()

    if not ui_data.get("explain_clicked"):
        return

    mode = ui_data.get("mode", "text")

    if mode == "text":
        notes_text = ui_data.get("notes_text", "")
        is_valid, error_msg = validate_text_input(notes_text, field_name="notes")
        if not is_valid:
            ui.show_warning(error_msg)
            return

        prompt = build_explain_notes_text_prompt(notes_text=notes_text)

        try:
            with st.spinner("📖 Reading and explaining your notes..."):
                response = generate_llm_response(
                    prompt=prompt,
                    api_key=api_key,
                    model=model,
                )
        except Exception as exc:  # noqa: BLE001
            # Don't expose full error details - show user-friendly message
            error_msg = str(exc)
            if "401" in error_msg or "authentication" in error_msg.lower() or "invalid" in error_msg.lower():
                ui.show_error("❌ Authentication failed. Please check your API key in the .env file.")
            else:
                ui.show_error(f"❌ Something went wrong while talking to the AI. Please try again.")
            return

        ui.show_markdown_section("📝 Explanation", response)
        return

    # Image mode
    uploaded_file = ui_data.get("uploaded_file")
    is_valid, error_msg = validate_image_file(uploaded_file)
    if not is_valid:
        ui.show_warning(error_msg)
        return

    try:
        with st.spinner("📖 Reading text from your notes image..."):
            image_bytes = uploaded_file.read()
            ocr_text = extract_text_from_image(image_bytes)
    except Exception as exc:  # noqa: BLE001
        ui.show_error(f"❌ Could not read the image: {exc}")
        return

    if not ocr_text or not ocr_text.strip():
        ui.show_warning("I couldn't detect any readable text in the image. Please try a clearer photo.")
        return

    prompt = build_explain_notes_image_prompt(ocr_text=ocr_text)

    try:
        with st.spinner("📖 Explaining the content of your notes..."):
            response = generate_llm_response(
                prompt=prompt,
                api_key=api_key,
                model=model,
            )
    except Exception as exc:  # noqa: BLE001
        # Don't expose full error details - show user-friendly message
        error_msg = str(exc)
        if "401" in error_msg or "authentication" in error_msg.lower() or "invalid" in error_msg.lower():
            ui.show_error("❌ Authentication failed. Please check your API key in the .env file.")
        else:
            ui.show_error(f"❌ Something went wrong while talking to the AI. Please try again.")
        return

    combined = f"### Extracted Notes Text\n\n{ocr_text}\n\n---\n\n### AI Explanation\n\n{response}"
    ui.show_markdown_section("📝 Explanation", combined)


def _load_env_key_from_file() -> str:
    """
    Directly read OPENROUTER_API_KEY from .env file as fallback.
    Checks multiple locations: project root, utils folder, etc.
    This ensures we can read the key even if load_dotenv() didn't work in Streamlit context.
    """
    from pathlib import Path
    
    # Try multiple locations
    base_dir = Path(__file__).resolve().parent.parent
    possible_paths = [
        base_dir / ".env",  # Project root (preferred)
        base_dir / "utils" / ".env",  # Fallback: utils folder
    ]
    
    for env_path in possible_paths:
        try:
            if env_path.exists():
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        # Skip comments and empty lines
                        if not line or line.startswith("#"):
                            continue
                        # Look for OPENROUTER_API_KEY
                        if line.startswith("OPENROUTER_API_KEY"):
                            # Handle both KEY=value and KEY="value" formats
                            if "=" in line:
                                key_part, value_part = line.split("=", 1)
                                value = value_part.strip()
                                # Remove quotes if present
                                if value.startswith('"') and value.endswith('"'):
                                    value = value[1:-1]
                                elif value.startswith("'") and value.endswith("'"):
                                    value = value[1:-1]
                                if value:
                                    return value
        except Exception:  # noqa: BLE001
            continue
    
    return ""


def run_app() -> None:
    """Entry point for the StudyBuddy AI application controller."""
    # CRITICAL: Reload .env in Streamlit context (Streamlit runs in subprocess)
    from pathlib import Path
    from dotenv import load_dotenv
    
    base_dir = Path(__file__).resolve().parent.parent
    # Try project root first, then utils folder as fallback
    env_path = base_dir / ".env"
    if not env_path.exists():
        env_path = base_dir / "utils" / ".env"
    
    load_dotenv(dotenv_path=env_path, override=False)
    
    ui.setup_page()
    ui.render_main_header()
    init_chat_state()

    # Get API key from environment/secrets only (no sidebar input)
    # Method 1: Environment variable (from os.getenv)
    env_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    
    # Method 2: Direct file read (fallback if load_dotenv didn't work)
    if not env_key:
        env_key = _load_env_key_from_file()
    
    # Method 3: Streamlit secrets
    secret_key = ""
    try:
        secret_key = st.secrets.get("OPENROUTER_API_KEY", "").strip()
    except Exception:  # noqa: BLE001
        pass

    # Use env key or secret key (no sidebar override)
    api_key = env_key or secret_key

    # Validate API key format if present
    if api_key:
        api_key_clean = api_key.strip()
        # Allow both sk-or-v1- and sk-or-v1 formats, and also check for common variations
        valid_prefixes = ["sk-or-v1-", "sk-or-v1", "sk-"]
        if not any(api_key_clean.startswith(prefix) for prefix in valid_prefixes):
            st.error(
                "⚠️ **Invalid API Key Format**\n\n"
                "Your OpenRouter API key format is incorrect. Keys should start with 'sk-or-v1-' or 'sk-'.\n\n"
                "Please check your `.env` file and ensure it contains:\n"
                "`OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here`\n\n"
                "**Troubleshooting:**\n"
                "1. Make sure there are no extra spaces or quotes around the key\n"
                "2. The key should be on a single line\n"
                "3. Get a new key at: https://openrouter.ai/keys if needed\n\n"
                "**Note:** If your key is valid but still shows this error, it may be expired or invalid."
            )
            st.stop()
        api_key = api_key_clean

    # Set default model (no user selection)
    model = "xiaomi/mimo-v2-flash:free"

    # Show warning in main page if key is missing
    if not api_key:
        env_file_exists = env_path.exists()
        st.warning(
            "⚠️ **OpenRouter API Key Required**\n\n"
            "Set it using one of these methods:\n"
            "- `.env` file: `OPENROUTER_API_KEY=sk-or-v1-...` (in project root)\n"
            "- Environment variable: `OPENROUTER_API_KEY`\n"
            "- Streamlit secrets: `OPENROUTER_API_KEY`\n\n"
            f"**Status:** .env file {'found' if env_file_exists else 'NOT FOUND'} at: `{env_path.name}`\n\n"
            "Get your free API key at: https://openrouter.ai/keys"
        )
        st.stop()

    # --- TABS ---
    tab1, tab2, tab3 = ui.get_tabs()

    with tab1:
        _handle_text_chat_tab(api_key, model)
    with tab2:
        _handle_image_solver_tab(api_key, model)
    with tab3:
        _handle_explain_notes_tab(api_key, model)
