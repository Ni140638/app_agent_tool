import streamlit as st
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]

# กำหนดชื่อแท็บ
tabs = st.tabs(["💵 Assest Allocation", "🚗 Motorinsurance", "💳 Credit card"])

# เก็บ state แยกสำหรับแต่ละบอท
if "messages_bot1" not in st.session_state:
    st.session_state["messages_bot1"] = []

if "messages_bot2" not in st.session_state:
    st.session_state["messages_bot2"] = []

if "messages_bot3" not in st.session_state:
    st.session_state["messages_bot3"] = []

# ฟังก์ชันถามบอท
def ask_openai(messages, system_prompt):
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=full_messages
    )
    return response.choices[0].message["content"]

# 💵 Tab 1 – GPT-3.5 ปกติ
with tabs[0]:
    st.subheader("💵 Assest Allocation")
    for msg in st.session_state["messages_bot1"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("พิมพ์คำถาม... ", key="input1"):
        st.session_state["messages_bot1"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        reply = ask_openai(st.session_state["messages_bot1"], "คุณคือ AI อัจฉริยะทั่วไป")
        st.chat_message("assistant").markdown(reply)
        st.session_state["messages_bot1"].append({"role": "assistant", "content": reply})

# 🚗 Tab 2 – Bot Tutor
with tabs[1]:
    st.subheader("🚗 Motorinsurance")
    for msg in st.session_state["messages_bot2"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("ถามเคำถาม", key="input2"):
        st.session_state["messages_bot2"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        reply = ask_openai(st.session_state["messages_bot2"], "คุณคือครูอธิบายเข้าใจง่าย ใช้ภาษาคนทั่วไป")
        st.chat_message("assistant").markdown(reply)
        st.session_state["messages_bot2"].append({"role": "assistant", "content": reply})

# 💳 Tab 3 – Bot Assistant
with tabs[2]:
    st.subheader("💳 Credit card")
    for msg in st.session_state["messages_bot3"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("ถามคำถาม", key="input3"):
        st.session_state["messages_bot3"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        reply = ask_openai(st.session_state["messages_bot3"], "คุณคือเลขาส่วนตัวที่ช่วยสรุปงานและวางแผน")
        st.chat_message("assistant").markdown(reply)
        st.session_state["messages_bot3"].append({"role": "assistant", "content": reply})
