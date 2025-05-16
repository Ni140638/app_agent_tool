import streamlit as st
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]

# เตรียม state เริ่มต้น
if "selected_topic" not in st.session_state:
    st.session_state["selected_topic"] = None
if "input_topic" not in st.session_state:
    st.session_state["input_topic"] = ""

for i in range(1, 4):
    st.session_state.setdefault(f"messages_bot{i}", [])
    st.session_state.setdefault(f"input_bot{i}", "")
    st.session_state.setdefault(f"input{i}", "")  # key ของ text_input แต่ละช่อง

# โหลด system prompts
with open("genai-mf-prompt-for-first-draft.txt", "r", encoding="utf-8") as file:
    prompt_mf = file.read()
with open("gen-ai-motor-first-draft.txt", "r", encoding="utf-8") as file:
    prompt_motor = file.read()
prompt_credit = "คุณคือเลขาส่วนตัวที่ช่วยสรุปงานและแนะนำการใช้บัตรเครดิตอย่างชาญฉลาด"

# ฟังก์ชันเรียก OpenAI
def ask_openai(messages, system_prompt):
    full_messages = [{"role": "system", "content": system_prompt}] + messages[-10:]  # limit history
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=full_messages
        )
        return response.choices[0].message["content"]
    except Exception as e:
        st.error(f"OpenAI Error: {e}")
        return "ขออภัยค่ะ เกิดข้อผิดพลาดจากระบบ AI"

# STEP 1: ถามหัวข้อ
if st.session_state["selected_topic"] is None:
    st.chat_message("assistant").markdown(
        "สวัสดีค่ะ 😊 คุณอยากสอบถามเรื่องอะไร?\n\n"
        "กรุณาพิมพ์หัวข้อที่คุณสนใจ ได้แก่: `Asset Allocation`, `Motor Insurance`, หรือ `Credit card` หากต้องการเปลี่ยนหัวข้อให้พิมพ์ว่า `เปลี่ยนหัวข้อ` ค่ะ"
    )
    with st.form(key="topic_form"):
        st.session_state["input_topic"] = st.text_input("หัวข้อที่คุณต้องการพูดคุย...")
        submitted = st.form_submit_button("ส่ง")

    if submitted:
        topic = st.session_state["input_topic"].strip().lower()
        mapping = {
            "asset allocation": "asset", "asset": "asset",
            "motor insurance": "motor", "motor": "motor",
            "credit card": "credit", "credit": "credit"
        }
        if topic in mapping:
            st.session_state["selected_topic"] = mapping[topic]
        else:
            st.warning("กรุณาพิมพ์เฉพาะ asset allocation, motor insurance, หรือ credit card เท่านั้นนะคะ")

# STEP 2: ฟังก์ชันแสดง UI ตามบอท
def run_bot(tab_title, subheader_text, bot_index, preset_buttons, system_prompt):
    tabs = st.tabs([tab_title])
    with tabs[0]:
        st.subheader(subheader_text)

        col1, col2, col3 = st.columns(3)
        for i, (col, text) in enumerate(zip((col1, col2, col3), preset_buttons)):
            if col.button(f"📌 {text}", key=f"btn{bot_index}{chr(97+i)}"):
                st.session_state[f"input_bot{bot_index}"] = text

        for msg in st.session_state[f"messages_bot{bot_index}"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        with st.form(key=f"form{bot_index}"):
            cols = st.columns([10, 1])
            with cols[0]:
                user_input = st.text_input(
                    "ถามคำถาม...",
                    key=f"input{bot_index}",
                    label_visibility="collapsed",
                    placeholder="พิมพ์คำถาม..."
                )
            with cols[1]:
                submitted = st.form_submit_button("➤")

        if submitted and user_input:
            prompt = user_input.strip()
            if prompt == "เปลี่ยนหัวข้อ":
                st.session_state[f"input_bot{bot_index}"] = ""
                st.session_state[f"messages_bot{bot_index}"] = []
                st.session_state[f"input{bot_index}"] = ""
                st.session_state["selected_topic"] = None
                st.chat_message("assistant").markdown("รับทราบค่ะ เปลี่ยนหัวข้อให้แล้วนะคะ ✨")
                st.rerun()
            else:
                st.session_state[f"messages_bot{bot_index}"].append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                reply = ask_openai(st.session_state[f"messages_bot{bot_index}"], system_prompt)
                st.chat_message("assistant").markdown(reply)
                st.session_state[f"messages_bot{bot_index}"].append({"role": "assistant", "content": reply})
                st.session_state[f"input_bot{bot_index}"] = ""
                st.session_state[f"input{bot_index}"] = ""

# STEP 3: เรียกฟังก์ชันตามหัวข้อที่เลือก
if st.session_state["selected_topic"] == "asset":
    run_bot(
        tab_title="💵 Asset Allocation",
        subheader_text="💵 Asset Allocation",
        bot_index=1,
        preset_buttons=[
            "ลูกค้ามีเงินเย็นอยู่กี่บาท วางเป็นระยะเท่าไร",
            "เงินเย็นของลูกค้าสามารถทำอย่างไรได้บ้างเพื่อให้ผลกำไรงอกเงย",
            "ผลิตภัณฑ์ Portfolio และ Matual Fund ที่แนะนำคืออะไร"
        ],
        system_prompt=prompt_mf
    )

elif st.session_state["selected_topic"] == "motor":
    run_bot(
        tab_title="🚗 Motor Insurance",
        subheader_text="🚗 Motor Insurance",
        bot_index=2,
        preset_buttons=[
            "ข้อมูลรถ(ปี/model/ยี่ห้อ)",
            "VMI ที่เหมาะกับลูกค้าคืออะไร",
            "ช่องทางที่ลูกค้าจ่ายได้"
        ],
        system_prompt=prompt_motor
    )

elif st.session_state["selected_topic"] == "credit":
    run_bot(
        tab_title="💳 Credit Card",
        subheader_text="💳 Credit Card",
        bot_index=3,
        preset_buttons=[
            "ลูกค้าถือบัตรประเภทไหน status ของบัตรเป็นอย่างไร",
            "ลูกค้ามี Lifestyle เป็นอย่างไร",
            "Promotion/Privilage ที่เหมาะกับลูกค้า"
        ],
        system_prompt=prompt_credit
    )
