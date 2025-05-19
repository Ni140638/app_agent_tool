import streamlit as st
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]

# -------------------------------
# Inject custom CSS
# -------------------------------


# CSS สำหรับปุ่มแต่ละแบบ
st.markdown("""
<style>
div.stButton > button {
    background-color: #002f6c;      /* สีส้ม */
    color: white;                   /* ตัวอักษรสีขาว */
    font-size: 12px;                /* ขนาดตัวอักษร */
    border-radius: 12px;            /* มุมโค้ง */
    border: none;
    padding: 10px 24px;
     width: 100%;
     height: 100%;
}
div.stButton > button:hover {
    background-color: #e67300;      /* สีตอน hover */
/* เส้นใต้กล่องปุ่ม */
.button-wrapper {
    border-bottom: 2px solid #002f6c;
    padding-bottom: 16px;
    margin-bottom: 24px;
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
with open("genai-cc-prompt-for-first-draft.txt", "r", encoding="utf-8") as f:
    prompt_cc = f.read()
     

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

st.markdown(
    """
    <div style='text-align: center; margin-top: -20px;'>
    <br>
        <img src="https://www.ttbbank.com/global/assets/img/media-img/ttb_primary-logo-RGB-01.png" width="120">
        <div style='margin-top: -5px;'>
        </div>
        <h4 style='margin: 8px 0 4px 0;'>Segment of One</h4>
        <hr style='width: 85%; margin: 6px auto; border: 1px solid #aaa;' />
        <p style='font-size: 16px; margin: 0;'>Personalized Financial Solution for Wealth Customer</p>
    </div>
    """,
    unsafe_allow_html=True
)



if st.session_state["selected_topic"] is None:
    st.chat_message("assistant").markdown(
        "สวัสดีค่ะคุณอยากสอบถามเรื่องอะไร?\n\n"
        "กรุณาพิมพ์หัวข้อที่คุณสนใจ ได้แก่: `Asset Allocation`, `Motor Insurance`, หรือ `Credit card` หากต้องการเปลี่ยนหัวข้อให้พิมพ์ว่า `เปลี่ยนหัวข้อ` ค่ะ"
      
    )
    # เส้นแบ่งด้านล่าง
    st.markdown(
    "<hr style='border: 1.5px solid #002f6c; margin-top: 30px; margin-bottom: 30px;' />",
    unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
      if st.button("   Asset Allocation   "):
        st.session_state["input_topic"] = "Asset Allocation"
        st.rerun()

    with col2: 
        if st.button("   Motor Insurance    "):
            st.session_state["input_topic"] = "Motor Insurance"
            st.rerun()

    with col3:
        if st.button("   Credit card    "):
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
        cols = st.columns(len(preset_buttons))  # สร้าง columns ตามจำนวน preset
        for i, (col, text) in enumerate(zip(cols, preset_buttons)):
            if col.button(f" {text}", key=f"btn{bot_index}_{i}"):
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
    chat_tab("Asset Allocation", 1, prompt_mf, [
        "ลูกค้ามี AUM เท่าไหร่ และ Trend AUM ของลูกค้าเป็นอย่างไรใน 1 ปี  ",
        "ลูกค้าจัดสรรเงินส่วนใหญ่ไว้ในผลิตภัณฑ์เงินฝากและกองทุนอย่างไร  ",
        "กองทุนของลูกค้ามี Exposure อย่างไร ทั้งในอดีต ปัจจุบัน และอนาคต  ",
        "ลูกค้ามีเงินเย็นอยู่กี่บาท และวางได้เป็นระยะเวลาเท่าไหร่ นำไปจัดสรรอย่างไร",
        "ผลิตภัณฑ์ Portfolio และ MF ที่แนะนำคืออะไร Potential Gain เป็นเท่าไหร่",
    ])
elif st.session_state["selected_topic"] == "motor":
    chat_tab("Motor Insurance", 2, prompt_motor, [
        "ข้อมูลรถของลูกค้า เช่น ยี่ห้อรถ",
        "ประกันที่ลูกค้าถือก่อนหน้าคือ",
        "VMI ที่เหมาะกับลูกค้าคืออะไร",
        "VMI ที่เสนอประหยัดไปได้เท่าไหร่",
        "ช่องทางที่ลูกค้าจ่ายได้"
    ])
elif st.session_state["selected_topic"] == "credit":
    chat_tab("Credit Card", 3, prompt_cc, [
        "ลูกค้าถือบัตรประเภทไหน status เป็นอย่างไร",
        "พฤติกรรมการใช้จ่ายของลูกค้าเป็นอย่างไร",
        "ลูกค้ามี  Lifestyle การใช้จ่ายเป็นอย่างไร",
        "Promotion/Privilage ที่เหมาะกับลูกค้า",
        "Benefit ที่ลูกค้าควรจะได้รับคืออะไร"
    ])





