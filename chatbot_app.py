import streamlit as st
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]

# -------------------------------
# เตรียม state
# -------------------------------
tabs = st.tabs(["💵 Asset Allocation", "🚗 Motor Insurance", "💳 Credit Card"])

for i in range(1, 4):
    st.session_state.setdefault(f"messages_bot{i}", [])
    st.session_state.setdefault(f"input{i}", "")

# -------------------------------
# โหลด system prompt
# -------------------------------
with open("genai-mf-prompt-for-first-draft.txt", "r", encoding="utf-8") as f:
    prompt_mf = f.read()
with open("gen-ai-motor-first-draft.txt", "r", encoding="utf-8") as f:
    prompt_motor = f.read()
prompt_credit = "คุณคือเลขาส่วนตัวที่ช่วยสรุปงานและแนะนำการใช้บัตรเครดิตอย่างชาญฉลาด"

# -------------------------------
# ฟังก์ชันเรียก OpenAI
# -------------------------------
def ask_openai(messages, system_prompt, max_history=10):
    full_messages = [{"role": "system", "content": system_prompt}] + messages[-max_history:]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=full_messages
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"เกิดข้อผิดพลาด: {e}"

# -------------------------------
# ฟังก์ชันแสดงบอทในแต่ละแท็บ
# -------------------------------
def chat_tab(tab, bot_index, preset_buttons, system_prompt):
    with tab:
        st.subheader(preset_buttons["title"])

        # ปุ่ม preset
        col1, col2, col3 = st.columns(3)
        for i, (col, text) in enumerate(preset_buttons["items"]):
            if col.button(f"📌 {text}", key=f"btn{bot_index}_{i}"):
                st.session_state[f"input{bot_index}"] = text

        # แสดงประวัติการสนทนา
        for msg in st.session_state[f"messages_bot{bot_index}"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # ช่องพิมพ์ + ปุ่มส่ง
        cols = st.columns([10, 1])
        with cols[0]:
            user_input = st.text_input(
                "พิมพ์คำถาม...",
                key=f"input{bot_index}",
                label_visibility="collapsed",
                placeholder="พิมพ์คำถาม..."
            )
        with cols[1]:
            send_clicked = st.button("➤", key=f"send_btn{bot_index}")

        # เมื่อคลิกส่ง
        if send_clicked and user_input.strip():
            prompt = user_input.strip()
            st.session_state[f"messages_bot{bot_index}"].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            reply = ask_openai(st.session_state[f"messages_bot{bot_index}"], system_prompt)
            st.chat_message("assistant").markdown(reply)
            st.session_state[f"messages_bot{bot_index}"].append({"role": "assistant", "content": reply})
            st.session_state[f"input{bot_index}"] = ""  # ล้างช่องหลังส่ง

# -------------------------------
# เรียกแต่ละแท็บ
# -------------------------------
chat_tab(
    tabs[0], 1,
    preset_buttons={
        "title": "💵 Asset Allocation",
        "items": [
            ("ลูกค้ามีเงินเย็นอยู่กี่บาท วางเป็นระยะเท่าไร"),
            ("เงินเย็นของลูกค้าสามารถทำอย่างไรได้บ้างเพื่อให้ผลกำไรงอกเงย"),
            ("ผลิตภัณฑ์ Portfolio และ Matual Fund ที่แนะนำคืออะไร")
        ]
    },
    system_prompt=prompt_mf
)

chat_tab(
    tabs[1], 2,
    preset_buttons={
        "title": "🚗 Motor Insurance",
        "items": [
            ("ข้อมูลรถ(ปี/model/ยี่ห้อ)"),
            ("VMI ที่เหมาะกับลูกค้าคืออะไร"),
            ("ช่องทางที่ลูกค้าจ่ายได้")
        ]
    },
    system_prompt=prompt_motor
)

chat_tab(
    tabs[2], 3,
    preset_buttons={
        "title": "💳 Credit Card",
        "items": [
            ("ลูกค้าถือบัตรประเภทไหน status ของบัตรเป็นอย่างไร"),
            ("ลูกค้ามี Lifestyle เป็นอย่างไร"),
            ("Promotion/Privilage ที่เหมาะกับลูกค้า")
        ]
    },
    system_prompt=prompt_credit
)
