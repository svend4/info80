import streamlit as st
from src.cards.registry import card_registry
from src.cards.reactive import reactive_executor
from src.cards.executor import execute_card_safely
from src.cards.graphiti_integration import search_cards_in_graphiti
import asyncio

st.set_page_config(page_title="Data Cards • Reactive", layout="wide")
st.title("📦 Data Cards • Reactive Manager")

st.caption("Реактивная система Data Cards + безопасный sandbox")

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
                
                if card.source_code:
                    with st.expander("Показать код"):
                        st.code(card.source_code, language="python")
            
            with col2:
                if st.button("▶ Безопасно выполнить", key=f"safe_exec_{card.id}"):
                    with st.spinner("Выполнение в sandbox..."):
                        result = execute_card_safely(card.id)
                        if result.get("success"):
                            st.success("Успешно выполнено")
                            if result.get("stdout"):
                                st.code(result["stdout"])
                        else:
                            st.error(result.get("error") or "Ошибка выполнения")
                            if result.get("stderr"):
                                st.code(result["stderr"])
                
                if st.button("Реактивная цепочка", key=f"chain_{card.id}"):
                    with st.spinner("Выполнение цепочки..."):
                        result = asyncio.run(reactive_executor.execute_chain(card.id))
                        st.json(result)
                
                if is_stale and st.button("Принудительно пересчитать", key=f"force_{card.id}"):
                    with st.spinner("Пересчёт..."):
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
