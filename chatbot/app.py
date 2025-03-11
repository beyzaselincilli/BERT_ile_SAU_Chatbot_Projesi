import streamlit as st
from chatbot import ask_chatbot

st.set_page_config(page_title="SAÜ Yönetmelik Chatbot", page_icon="🎓")

st.title("📚 SAÜ Yönetmelik Chatbot")
st.markdown("""
Bu chatbot, Sakarya Üniversitesi'nin yönetmelik ve yönergelerini anlayıp cevaplayabilir.
Örnek sorular:
- Staj yönergesi hakkında bilgi verir misin?
- Muafiyet ve intibak yönergesinde hangi maddeler var?
- İngilizce hazırlık sınıfı esasları nelerdir?
""")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Sorunuzu yazın...", "")

if user_input:
    with st.spinner('Cevap hazırlanıyor...'):
        response = ask_chatbot(user_input)
        st.session_state.chat_history.append((user_input, response))

if st.session_state.chat_history:
    st.markdown("### Sohbet Geçmişi")
    for i, (question, answer) in enumerate(reversed(st.session_state.chat_history)):
        st.markdown(f"**Soru {len(st.session_state.chat_history)-i}:** {question}")
        st.markdown(f"**Cevap:** {answer}")
        st.markdown("---")
