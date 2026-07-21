import streamlit as st
from src.cards.registry import card_registry
from src.cards.reactive import reactive_executor
from src.cards.executor import execute_card_safely
from src.cards.versioning import get_versions, rollback
from src.cards.marimo_export import export_card_to_marimo, list_exported_notebooks
from src.cards.marketplace import (
    export_card_package, publish_card,
    list_shared_cards, install_shared_card, list_local_packages
)
from src.cards.graphiti_integration import search_cards_in_graphiti
from src.observability import list_traces, get_trace
import asyncio

st.set_page_config(page_title="Data Cards • Agent System", layout="wide")
st.title("📦 Data Cards • Multi-Agent System")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Data Cards",
    "Marketplace",
    "Трассы",
    "marimo Export",
    "Graphiti"
])

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
                with col2:
                    if st.button("▶ Выполнить", key=f"exec_{card.id}"):
                        result = execute_card_safely(card.id)
                        if result.get("success"):
                            st.success("OK")
                            st.code(result.get("stdout", ""))
                        else:
                            st.error(result.get("error"))
                    if st.button("📦 Export package", key=f"pkg_{card.id}"):
                        path = export_card_package(card.id)
                        if path:
                            st.success(f"Пакет: {path.name}")
                    if st.button("📢 Publish", key=f"pub_{card.id}"):
                        path = publish_card(card.id)
                        if path:
                            st.success("Опубликовано в Marketplace")
                    if st.button("📓 marimo", key=f"marimo_{card.id}"):
                        path = export_card_to_marimo(card)
                        st.success(f"{path.name}")

with tab2:
    st.subheader("Card Marketplace")
    st.caption("Локальный обмен карточками между проектами и пользователями")

    st.write("### Опубликованные карточки")
    shared = list_shared_cards()
    if not shared:
        st.info("Пока никто не опубликовал карточки. Нажмите «Publish» на любой карточке.")
    else:
        for item in shared:
            with st.expander(f"**{item['name']}**  v{item.get('version')}  ({item.get('owner')})"):
                st.write(item.get("description"))
                st.write(f"ID: `{item.get('id')}`")
                if st.button("⬇️ Установить", key=f"install_{item['file']}"):
                    card = install_shared_card(item["file"])
                    if card:
                        st.success(f"Установлено: {card.name}")
                        st.rerun()

    st.write("### Локальные пакеты")
    packages = list_local_packages()
    if packages:
        for p in packages:
            st.write(f"📦 `{p.name}`")

with tab3:
    st.subheader("Трассы выполнения агентов")
    traces = list_traces(limit=30)
    if not traces:
        st.info("Трасс пока нет.")
    else:
        for t in traces:
            with st.expander(f"{t['trace_id']}  |  {t['status']}  |  событий: {t['events_count']}"):
                st.write(t.get("metrics", {}))
                full = get_trace(t["trace_id"])
                if full and full.get("events"):
                    for e in full["events"]:
                        st.write(f"- `{e['timestamp'][11:19]}` **{e['type']}**")

with tab4:
    st.subheader("Экспортированные marimo-ноутбуки")
    st.code("marimo edit data/marimo_export/имя_файла.py")
    notebooks = list_exported_notebooks()
    if not notebooks:
        st.info("Пока нет экспортированных ноутбуков.")
    else:
        for nb in notebooks:
            st.write(f"📓 `{nb.name}`")

with tab5:
    query = st.text_input("Поиск в Graphiti")
    if st.button("Искать") and query:
        results = asyncio.run(search_cards_in_graphiti(query))
        for r in results:
            st.write(r)
