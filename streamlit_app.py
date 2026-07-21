import streamlit as st
from src.cards.registry import card_registry
from src.cards.reactive import reactive_executor
from src.cards.executor import execute_card_safely
from src.cards.versioning import get_versions, rollback
from src.cards.graphiti_integration import search_cards_in_graphiti
from src.observability import list_traces, get_trace
import asyncio

st.set_page_config(page_title="Data Cards • Agent System", layout="wide")
st.title("📦 Data Cards • Multi-Agent System")

tab1, tab2, tab3 = st.tabs(["Data Cards", "Трассы (Observability)", "Поиск в Graphiti"])

with tab1:
    st.subheader("Все Data Cards")
    cards = card_registry.list_all()
    
    if not cards:
        st.info("Пока нет ни одной Data Card.")
    else:
        for card in cards:
            is_stale = card.id in reactive_executor.stale_cards
            status = "🔴 Устарела" if is_stale else "🟢 Актуальна"
            
            with st.expander(f"{status}  **{card.name}**  v{card.version}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(card.description)
                    if card.source_code:
                        with st.expander("Код"):
                            st.code(card.source_code, language="python")
                    versions = get_versions(card.id)
                    if versions:
                        st.write("Версии:", ", ".join([f"v{v['version']}" for v in versions]))
                with col2:
                    if st.button("▶ Выполнить", key=f"exec_{card.id}"):
                        result = execute_card_safely(card.id)
                        if result.get("success"):
                            st.success("OK")
                            st.code(result.get("stdout", ""))
                        else:
                            st.error(result.get("error"))

with tab2:
    st.subheader("Трассы выполнения агентов")
    traces = list_traces(limit=30)
    
    if not traces:
        st.info("Трасс пока нет. Запустите задачу через main.py или API.")
    else:
        for t in traces:
            with st.expander(f"{t['trace_id']}  |  {t['status']}  |  событий: {t['events_count']}"):
                st.write(f"**Начало:** {t.get('started_at', '')[:19]}")
                st.write("**Метрики:**", t.get("metrics", {}))
                
                full = get_trace(t["trace_id"])
                if full and full.get("events"):
                    st.write("**События:**")
                    for e in full["events"]:
                        st.write(f"- `{e['timestamp'][11:19]}` **{e['type']}** — {e.get('data', {})}")

with tab3:
    query = st.text_input("Поиск в Graphiti")
    if st.button("Искать") and query:
        results = asyncio.run(search_cards_in_graphiti(query))
        for r in results:
            st.write(r)
