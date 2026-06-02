from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)


def _new_transcript(
    *,
    provider_name: str,
    model: str | None,
    version: str,
    system_prompt_path: Path,
    tools_path: Path,
    history_window: int,
    max_tool_rounds: int,
) -> dict[str, Any]:
    artifact_version = build_artifact_version(version, system_prompt_path, tools_path)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), "ui", timestamp])
    return {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }


def _transcript_path(transcript: dict[str, Any]) -> Path:
    return TRANSCRIPTS_DIR / f"{transcript['transcript_id']}.transcript.json"


def _ensure_session(
    *,
    provider_name: str,
    model: str | None,
    version: str,
    system_prompt_path: Path,
    tools_path: Path,
    history_window: int,
    max_tool_rounds: int,
) -> None:
    config_key = {
        "provider_name": provider_name,
        "model": model,
        "version": version,
        "system_prompt_path": str(system_prompt_path),
        "tools_path": str(tools_path),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
    }
    if "config_key" not in st.session_state or st.session_state.config_key != config_key:
        st.session_state.config_key = config_key
        st.session_state.messages = []
        st.session_state.history = []
        st.session_state.turn_index = 0
        st.session_state.transcript = _new_transcript(
            provider_name=provider_name,
            model=model,
            version=version,
            system_prompt_path=system_prompt_path,
            tools_path=tools_path,
            history_window=history_window,
            max_tool_rounds=max_tool_rounds,
        )


def main() -> None:
    st.set_page_config(page_title="Research Agent", page_icon=None, layout="wide")
    st.title("Research Agent")

    with st.sidebar:
        st.header("Run Settings")
        provider_name = st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini"], index=0)
        version = st.text_input("Version", value="v3")
        model_input = st.text_input("Model override", value="")
        model = model_input.strip() or None
        history_window = st.number_input("History window", min_value=0, max_value=20, value=5, step=1)
        max_tool_rounds = st.number_input("Max tool rounds", min_value=1, max_value=8, value=4, step=1)
        system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
        tools_path = ARTIFACTS_DIR / "tools.yaml"
        if st.button("New chat", use_container_width=True):
            for key in ["config_key", "messages", "history", "turn_index", "transcript"]:
                st.session_state.pop(key, None)
            st.rerun()

    _ensure_session(
        provider_name=provider_name,
        model=model,
        version=version,
        system_prompt_path=system_prompt_path,
        tools_path=tools_path,
        history_window=int(history_window),
        max_tool_rounds=int(max_tool_rounds),
    )

    transcript = st.session_state.transcript

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_text = st.chat_input("Ask the research agent")
    if not user_text:
        return

    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(tools_path)
    openai_tools = to_openai_tools(tool_declarations)
    provider = make_provider(provider_name)
    selected_model = model or getattr(provider, "default_model", None)

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, int(history_window)),
        {"role": "user", "content": user_text},
    ]

    st.session_state.turn_index += 1
    turn_record: dict[str, Any] = {
        "turn_index": st.session_state.turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    with st.chat_message("assistant"):
        with st.spinner("Running agent..."):
            try:
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=selected_model,
                    max_tool_rounds=int(max_tool_rounds),
                )
                assistant_text = result["assistant_text"]
                st.markdown(assistant_text)
                turn_record.update(result)
                st.session_state.history.append({"role": "user", "content": user_text})
                st.session_state.history.append({"role": "assistant", "content": assistant_text})
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_text,
                    "rounds": result.get("rounds", []),
                })
            except Exception as exc:
                error_text = f"{type(exc).__name__}: {exc}"
                st.error(error_text)
                turn_record.update({"status": "provider_error", "error": error_text})
                st.session_state.messages.append({"role": "assistant", "content": error_text, "rounds": []})

    turn_record["ended_at"] = now_iso()
    transcript["model"] = selected_model
    transcript["turns"].append(turn_record)
    write_transcript(_transcript_path(transcript), transcript)


if __name__ == "__main__":
    main()
