from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from env_loader import load_lab_env
from providers import make_provider
from providers.base import ToolCall
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
load_lab_env(ROOT)


def execute_tool_call(call: ToolCall) -> dict[str, Any]:
    func = TOOL_FUNCTIONS.get(call.name)
    if not func:
        return {"tool": call.name, "args": call.args, "result": {"error": "unknown_tool"}}
    try:
        result = func(**call.args)
    except Exception as exc:
        result = {"error": type(exc).__name__, "message": str(exc)}
    return {"tool": call.name, "args": call.args, "result": result}


def run_model_tool_loop(
    provider: Any,
    messages: list[dict[str, str]],
    tools: list[dict[str, Any]],
    model: str | None,
    max_tool_rounds: int,
    status_placeholder: Any,
) -> dict[str, Any]:
    working_messages = list(messages)
    rounds: list[dict[str, Any]] = []
    all_tool_events: list[dict[str, Any]] = []

    for round_index in range(1, max_tool_rounds + 1):
        status_placeholder.text(f"Round {round_index}: Thinking...")
        response = provider.complete(working_messages, tools, model=model, temperature=0.0)
        calls = response.tool_calls
        round_record: dict[str, Any] = {
            "round": round_index,
            "assistant_text": response.text,
            "tool_calls": [{"name": call.name, "args": call.args} for call in calls],
            "tool_results": [],
        }

        if not calls:
            rounds.append(round_record)
            return {
                "status": "answered",
                "assistant_text": response.text or "",
                "rounds": rounds,
                "tool_events": all_tool_events,
            }

        from chat import assistant_tool_message, tool_results_message

        working_messages.append(assistant_tool_message(response.text, calls))
        non_clarification_events: list[dict[str, Any]] = []

        for call in calls:
            status_placeholder.text(f"Round {round_index}: Running {call.name}...")
            event = execute_tool_call(call)
            round_record["tool_results"].append(event)
            all_tool_events.append(event)

            result = event.get("result", {})
            if isinstance(result, dict) and result.get("awaiting_user"):
                question = result.get("question") or call.args.get("question") or "Please provide more information."
                rounds.append(round_record)
                return {
                    "status": "waiting_for_user",
                    "assistant_text": question,
                    "rounds": rounds,
                    "tool_events": all_tool_events,
                }

            non_clarification_events.append(event)

        rounds.append(round_record)
        working_messages.append(tool_results_message(non_clarification_events))

    return {
        "status": "max_tool_rounds",
        "assistant_text": f"Stopped after {max_tool_rounds} tool rounds.",
        "rounds": rounds,
        "tool_events": all_tool_events,
    }


def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "transcript" not in st.session_state:
        st.session_state.transcript = {
            "transcript_id": datetime.now().strftime("%Y%m%dT%H%M%S"),
            "created_at": datetime.now().isoformat(),
            "turns": [],
        }


def save_transcript():
    transcript_dir = ROOT / "transcripts"
    transcript_dir.mkdir(exist_ok=True)
    path = transcript_dir / f"{st.session_state.transcript['transcript_id']}.transcript.json"
    st.session_state.transcript["updated_at"] = datetime.now().isoformat()
    path.write_text(json.dumps(st.session_state.transcript, ensure_ascii=False, indent=2, default=str))
    return path


def main() -> None:
    st.set_page_config(
        page_title="Research Agent",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state()

    st.title("🔬 Research Agent")
    st.caption("AI Research Assistant with Tool Calling - Day04 Lab")

    with st.sidebar:
        st.header("⚙️ Settings")

        provider_name = st.selectbox(
            "Provider",
            ["openrouter", "openai", "anthropic", "gemini"],
            index=0,
        )

        system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
        tools_path = ARTIFACTS_DIR / "tools.yaml"

        system_prompt = system_prompt_path.read_text(encoding="utf-8")
        tool_declarations = load_tool_declarations(tools_path)
        openai_tools = to_openai_tools(tool_declarations)
        provider = make_provider(provider_name)
        selected_model = getattr(provider, "default_model", None)

        max_rounds = st.slider("Max Tool Rounds", 1, 8, 4)
        history_window = st.slider("History Window", 1, 10, 5)

        st.divider()
        st.subheader("🛠️ Available Tools")
        for decl in tool_declarations:
            with st.expander(f"📌 {decl['name']}"):
                st.caption(decl.get("description", "")[:150] + "...")

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.transcript = {
                    "transcript_id": datetime.now().strftime("%Y%m%dT%H%M%S"),
                    "created_at": datetime.now().isoformat(),
                    "turns": [],
                }
                st.rerun()
        with col2:
            if st.button("💾 Save Transcript", use_container_width=True):
                path = save_transcript()
                st.success(f"Saved: {path.name}")

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("tool_events"):
                    with st.expander("🔧 Tool Calls Details", expanded=False):
                        for i, evt in enumerate(msg["tool_events"]):
                            tool_name = evt.get("tool", "unknown")
                            tool_args = evt.get("args", {})
                            tool_result = evt.get("result", {})

                            st.markdown(f"**{i+1}. `{tool_name}`**")
                            st.json({"args": tool_args, "result": tool_result})
                            if i < len(msg["tool_events"]) - 1:
                                st.divider()

    if user_input := st.chat_input("Ask about research, news, tweets, papers..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)

        history: list[dict[str, str]] = []
        for msg in st.session_state.messages[-history_window * 2:]:
            if msg["role"] in ("user", "assistant"):
                history.append({"role": msg["role"], "content": msg["content"]})

        messages = [
            {"role": "system", "content": system_prompt},
            *history[:-1],
            {"role": "user", "content": user_input},
        ]

        with chat_container:
            with st.chat_message("assistant"):
                status = st.empty()
                try:
                    result = run_model_tool_loop(
                        provider=provider,
                        messages=messages,
                        tools=openai_tools,
                        model=selected_model,
                        max_tool_rounds=max_rounds,
                        status_placeholder=status,
                    )
                    status.empty()
                    assistant_text = result["assistant_text"]
                    st.markdown(assistant_text)

                    if result["tool_events"]:
                        with st.expander("🔧 Tool Calls Details", expanded=False):
                            for i, evt in enumerate(result["tool_events"]):
                                tool_name = evt.get("tool", "unknown")
                                tool_args = evt.get("args", {})
                                tool_result = evt.get("result", {})

                                st.markdown(f"**{i+1}. `{tool_name}`**")
                                st.json({"args": tool_args, "result": tool_result})
                                if i < len(result["tool_events"]) - 1:
                                    st.divider()

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_text,
                        "tool_events": result["tool_events"],
                    })

                    turn_record = {
                        "turn_index": len(st.session_state.transcript["turns"]) + 1,
                        "started_at": datetime.now().isoformat(),
                        "user": user_input,
                        "status": result["status"],
                        "assistant_text": assistant_text,
                        "tool_events": result["tool_events"],
                        "rounds": result["rounds"],
                    }
                    st.session_state.transcript["turns"].append(turn_record)

                except Exception as exc:
                    status.empty()
                    st.error(f"Error: {type(exc).__name__}: {exc}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Error: {type(exc).__name__}: {exc}",
                        "tool_events": [],
                    })

    with st.sidebar:
        st.divider()
        st.subheader("📊 Session Stats")
        st.metric("Messages", len(st.session_state.messages))
        st.metric("Turns", len(st.session_state.transcript.get("turns", [])))

        if st.session_state.transcript.get("turns"):
            total_tools = sum(
                len(turn.get("tool_events", []))
                for turn in st.session_state.transcript["turns"]
            )
            st.metric("Tool Calls", total_tools)


if __name__ == "__main__":
    main()
