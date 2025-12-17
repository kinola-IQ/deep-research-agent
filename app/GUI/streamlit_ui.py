"""module to create the minimal graphical user interface"""
import streamlit as st
import requests
import time

API_BASE = st.sidebar.text_input("API base URL", "http://127.0.0.1:8501")


def check_health():
    """Query the backend /v1/health endpoint and return (model_loaded, payload)."""
    try:
        resp = requests.get(f"{API_BASE}/v1/health", timeout=2)
        resp.raise_for_status()
        data = resp.json()
        return data.get("model_loaded", False), data
    except Exception:
        return False, {}


def user_interface():
    st.title("Deep Research — Minimal UI")

    # Show backend health in the sidebar
    model_loaded, health_payload = check_health()
    if model_loaded:
        st.sidebar.success("Backend: Model loaded ✅")
    else:
        st.sidebar.warning("Backend: Model not ready (check /v1/health)")

    # Allow manual refresh of health
    if st.sidebar.button("Refresh health"):
        st.rerun()

    # Main page health banner + auto-retry
    status_placeholder = st.empty()
    if model_loaded:
        status_placeholder.success("Backend ready — model loaded ✅")
    else:
        status_placeholder.warning("Backend not ready — model is still loading or unavailable.")

        # allow user to start an auto-retry/polling sequence
        if st.button("Auto-retry health"):
            max_tries = 12  # retry up to 12 times (~1 minute with 5s interval)
            interval = 5
            progress = st.progress(0)
            info = st.empty()
            for i in range(max_tries):
                info.info(f"Retrying health check... (attempt {i+1}/{max_tries})")
                ok, _ = check_health()
                progress.progress(int((i / max_tries) * 100))
                if ok:
                    st.success("Model loaded — backend is ready ✅")
                    st.rerun()
                    break
                # show countdown
                for sec in range(interval, 0, -1):
                    info.info(f"Next attempt in {sec}s — attempt {i+1}/{max_tries}")
                    time.sleep(1)
            else:
                info.error("Model did not become ready within the retry window. Please check logs and try again.")

    query = st.text_area("Research query", height=160)

    # also show a small inline readiness note
    if model_loaded:
        st.caption("Backend ready — you can run a research query.")
    else:
        st.caption("Backend not ready — use Auto-retry or Refresh health.")

    if st.button("Run Research"):
        if not model_loaded:
            st.error("Model is not loaded yet. Please wait for the backend to be ready and try again.")
            return
        if not query.strip():
            st.warning("Please enter a research query.")
            return

        with st.spinner("Running..."):
            try:
                resp = requests.post(f"{API_BASE}/v1/agent", json={"text": query}, timeout=120)
                resp.raise_for_status()
                body = resp.json().get("response", "")
                st.markdown(body)  # backend returns final markdown
            except requests.RequestException as e:
                st.error(f"Request failed: {e}")


if __name__ == "__main__":
    user_interface()
    

