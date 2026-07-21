import streamlit as st
from src.cards.registry import card_registry
from src.cards.reactive import reactive_executor
from src.cards.graphiti_integration import search_cards_in_graphiti
import asyncio

st.set_page_config(page_title="Data Cards • Reactive", layout="wide")
st.title("📦 Data Cards • Reactive Manager")

st.caption("Реактивная система Data Cards (по мотивам marimo + Graphiti + Multi-Agent)")

st.sidebar.header("Действия")
if st.sidebar.button("🔄 Пересчитать все устаревшие"):
    with st.spinner("Пересчёт..."):
        for card_id in list(reactive_executor.stale_cards):
            asyncio.run(reactive_executor.execute_chain(card_id))
        st.success("Все устаревшие карточки пересчитаны")

st.subheader("Все Data Cards")

cards = card_registry.list_all()

if not cards:
    st.info("Пока нет ни одной Data Card. Создайте первую через агента (main.py или API).")
else:
    for card in cards:
        is_stale = card.id in reactive_executor.stale_cards
        status = "🔴 Устарела" if is_stale else "🟢 Актуальна"
        
        with st.expander(f"{status}  **{card.name}**  (`{card.id}`)"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Описание:** {card.description}")
                st.write(f"**Версия:** {card.version} | **Владелец:** {card.owner}")
                if card.tags:
                    st.write(f"**Теги:** {', '.join(card.tags)}")
                if card.dependencies:
                    st.write(f"**Зависит от:** {', '.join(card.dependencies)}")
            
            with col2:
                if st.button("Выполнить", key=f"exec_{card.id}"):
                    with st.spinner("Выполнение..."):
                        result = asyncio.run(reactive_executor.execute_chain(card.id))
                        st.json(result)
                
                if is_stale and st.button("Принудительно пересчитать", key=f"force_{card.id}"):
                    with st.spinner("Пересчёт цепочки..."):
                        asyncio.run(reactive_executor.execute_chain(card.id))
                        st.success("Цепочка пересчитана")
                        st.rerun()

st.divider()
st.subheader("Поиск в знаниях (Graphiti)")

query = st.text_input("Что ищем?")
if st.button("Искать") and query:
    with st.spinner("Поиск..."):
        results = asyncio.run(search_cards_in_graphiti(query))
        for r in results:
            st.write(r)
