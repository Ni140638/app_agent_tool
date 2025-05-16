import streamlit as st
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]

# -------------------------------
# Inject custom CSS
# -------------------------------
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        .element-container {
            margin-bottom: 0.3rem;
        }
        button[kind="primary"] {
            margin-top: 0.3rem;
        }
        button {
            margin: 0.2rem 0 !important;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# เตรียม state
# -------------------------------
if "selected_topic" not in st.session_state:
    st.session_state["selected_topic"] = None
if "input_topic" not in st.session_state:
    st.session_state["input_topic"] = ""

for i in range(1, 4):
    st.session_state.setdefault(f"messages_bot{i}", [])
    st.session_state.setdefault(f"prefill_input_{i}", "")

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
# STEP 1: เลือกหัวข้อหลัก
# -------------------------------
if st.session_state["selected_topic"] is None:
    st.chat_message("assistant").markdown(
        "สวัสดีค่ะ 😊 คุณอยากสอบถามเรื่องอะไร?\n\n"
        "กรุณาพิมพ์หัวข้อที่คุณสนใจ ได้แก่: `Asset Allocation`, `Motor Insurance`, หรือ `Credit card` หากต้องการเปลี่ยนหัวข้อให้พิมพ์ว่า `เปลี่ยนหัวข้อ` ค่ะ"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Asset Allocation"):
            st.session_state["input_topic"] = "Asset Allocation"
            st.rerun()
    with col2:
        if st.button("Motor Insurance"):
            st.session_state["input_topic"] = "Motor Insurance"
            st.rerun()
    with col3:
        if st.button("Credit card"):
            st.session_state["input_topic"] = "Credit Card"
            st.rerun()

    with st.form(key="topic_form"):
        input_topic = st.text_input("หัวข้อที่คุณต้องการพูดคุย...", value=st.session_state["input_topic"])
        submitted = st.form_submit_button("ส่ง")
        if submitted:
            topic = input_topic.strip().lower()
            topic_map = {
                "asset allocation": "asset",
                "asset": "asset",
                "motor insurance": "motor",
                "motor": "motor",
                "credit card": "credit",
                "credit": "credit"
            }
            if topic in topic_map:
                st.session_state["selected_topic"] = topic_map[topic]
                st.rerun()
            else:
                st.warning("กรุณาพิมพ์เฉพาะ asset allocation, motor insurance, หรือ credit card เท่านั้นนะคะ")

# -------------------------------
# STEP 2: แสดงแชทตามหัวข้อ
# -------------------------------
def chat_tab(title, bot_index, system_prompt, preset_buttons):
    tabs = st.tabs([title])
    with tabs[0]:
        st.subheader(title)

        # แสดงข้อความสนทนาก่อนหน้า
        for msg in st.session_state[f"messages_bot{bot_index}"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # ปุ่ม preset → prefill
        col1, col2, col3 = st.columns(3)
        for i, (col, text) in enumerate(zip((col1, col2, col3), preset_buttons)):
            if col.button(f"📌 {text}", key=f"btn{bot_index}_{i}"):
                st.session_state[f"prefill_input_{bot_index}"] = text
                st.rerun()

        # กล่องแชท
        cols = st.columns([10, 1])
        with cols[0]:
            user_input = st.text_input(
                "ถามคำถาม...",
                value=st.session_state[f"prefill_input_{bot_index}"],
                key=f"text_input_{bot_index}",
                label_visibility="collapsed",
                placeholder="ถามคำถาม..."
            )
        with cols[1]:
            send = st.button("➤", key=f"send_btn_{bot_index}")

        if send and user_input.strip():
            prompt = user_input.strip()
            st.session_state[f"prefill_input_{bot_index}"] = ""

            if prompt == "เปลี่ยนหัวข้อ":
                st.session_state[f"messages_bot{bot_index}"] = []
                st.session_state["selected_topic"] = None
                st.rerun()
            else:
                st.session_state[f"messages_bot{bot_index}"].append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                reply = ask_openai(st.session_state[f"messages_bot{bot_index}"], system_prompt)
                st.chat_message("assistant").markdown(reply)
                st.session_state[f"messages_bot{bot_index}"].append({"role": "assistant", "content": reply})
                st.rerun()

# -------------------------------
# STEP 3: เปิดแชทตามหัวข้อ
# -------------------------------
if st.session_state["selected_topic"] == "asset":
    chat_tab("💵 Asset Allocation", 1, prompt_mf, [
        "ลูกค้ามีเงินเย็นอยู่กี่บาท วางเป็นระยะเท่าไร",
        "เงินเย็นของลูกค้าสามารถทำอย่างไรได้บ้างเพื่อให้ผลกำไรงอกเงย",
        "ผลิตภัณฑ์ Portfolio และ Matual Fund ที่แนะนำคืออะไร"
    ])
elif st.session_state["selected_topic"] == "motor":
    chat_tab("🚗 Motor Insurance", 2, prompt_motor, [
        "ข้อมูลรถ(ปี/model/ยี่ห้อ)",
        "VMI ที่เหมาะกับลูกค้าคืออะไร",
        "ช่องทางที่ลูกค้าจ่ายได้"
    ])
elif st.session_state["selected_topic"] == "credit":
    chat_tab("💳 Credit Card", 3, prompt_credit, [
        "ลูกค้าถือบัตรประเภทไหน status ของบัตรเป็นอย่างไร",
        "ลูกค้ามี Lifestyle เป็นอย่างไร",
        "Promotion/Privilage ที่เหมาะกับลูกค้า"
    ])
