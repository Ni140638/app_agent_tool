import streamlit as st
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]

# เตรียม state เริ่มต้น
if "selected_topic" not in st.session_state:
    st.session_state["selected_topic"] = None
if "input_topic" not in st.session_state:
    st.session_state["input_topic"] = ""

for i in range(1, 4):
    if f"messages_bot{i}" not in st.session_state:
        st.session_state[f"messages_bot{i}"] = []
    if f"input_bot{i}" not in st.session_state:
        st.session_state[f"input_bot{i}"] = ""

# ฟังก์ชันเรียก OpenAI

def ask_openai(messages, system_prompt):
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=full_messages
    )
    return response.choices[0].message["content"]

# -------------------------------
# STEP 1: ให้บอทถามก่อนว่าผู้ใช้ต้องการคุยเรื่องอะไร
# -------------------------------
if st.session_state["selected_topic"] is None:
    st.chat_message("assistant").markdown(
        "สวัสดีค่ะ 😊 คุณอยากสอบถามเรื่องอะไร?\n\n"
        "กรุณาพิมพ์หัวข้อที่คุณสนใจ ได้แก่: `Asset Allocation`, `Motor Insurance`, หรือ `Credit card` หากต้องการเปลี่ยนหัวข้อให้พิมพ์ว่า `เปลี่ยนหัวข้อ` ค่ะ\n\n"
    )

    with st.form(key="topic_form"):
        st.session_state["input_topic"] = st.text_input("หัวข้อที่คุณต้องการพูดคุย...")
        submitted = st.form_submit_button("ส่ง")

    if submitted:
        topic = st.session_state["input_topic"].strip().lower()
        if topic in ["asset allocation", "asset","Asset Allocation"]:
            st.session_state["selected_topic"] = "asset"
        elif topic in ["motor insurance", "motor",'Motor Insurance']:
            st.session_state["selected_topic"] = "motor"
        elif topic in ["credit card", "credit",'Credit card']:
            st.session_state["selected_topic"] = "credit"
        else:
            st.warning("กรุณาพิมพ์เฉพาะ asset allocation, motor insurance, หรือ credit card เท่านั้นนะคะ")

# -------------------------------
# STEP 2: แสดงแท็บตามหัวข้อที่เลือก
# -------------------------------
if st.session_state["selected_topic"] == "asset":
    tabs = st.tabs(["\U0001F4B5 Asset Allocation"])
    with tabs[0]:
        st.subheader("💵 Asset Allocation")

        col1, col2, col3 = st.columns(3)
        if col1.button("📌 ลูกค้ามีเงินเย็นอยู่กี่บาท วางเป็นระยะเท่าไร", key="btn1a"):
            st.session_state["input_bot1"] = "ลูกค้ามีเงินเย็นอยู่กี่บาท วางเป็นระยะเท่าไร"
        if col2.button("📌 เงินเย็นของลูกค้าสามารถทำอย่างไรได้บ้างเพื่อให้ผลกำไรงอกเงย", key="btn1b"):
            st.session_state["input_bot1"] = "เงินเย็นของลูกค้าสามารถทำอย่างไรได้บ้างเพื่อให้ผลกำไรงอกเงย"
        if col3.button("📌 ผลิตภัณฑ์ Portfolio และ Matual Fund ที่แนะนำคืออะไร", key="btn1c"):
            st.session_state["input_bot1"] = "ผลิตภัณฑ์ Portfolio และ Matual Fund ที่แนะนำคืออะไร"

        for msg in st.session_state["messages_bot1"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        with st.form(key="form1"):
            cols = st.columns([10, 1])
            with cols[0]:
                st.session_state["input_bot1"] = st.text_input(
                    "พิมพ์คำถาม...",
                    value=st.session_state["input_bot1"],
                    key="input1",
                    label_visibility="collapsed",
                    placeholder="พิมพ์คำถาม..."
                )
            with cols[1]:
                submitted = st.form_submit_button("➤")

        if submitted and st.session_state["input_bot1"]:
            prompt = st.session_state["input_bot1"].strip()
            if prompt == "เปลี่ยนหัวข้อ":
                st.chat_message("assistant").markdown("รับทราบค่ะ เปลี่ยนหัวข้อให้แล้วนะคะ ✨")
                st.session_state["selected_topic"] = None
                st.rerun()  # แทนที่ experimental_rerun()
            else:
                st.session_state["messages_bot1"].append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                reply = ask_openai(st.session_state["messages_bot1"], "คุณคือ AI ด้านการวางแผนการลงทุน")
                st.chat_message("assistant").markdown(reply)
                st.session_state["messages_bot1"].append({"role": "assistant", "content": reply})
                st.session_state["input_bot1"] = ""

elif st.session_state["selected_topic"] == "motor":
    tabs = st.tabs(["\U0001F697 Motor Insurance"])
    with tabs[0]:
        st.subheader("🚗 Motor Insurance")

        col1, col2, col3 = st.columns(3)
        if col1.button("📌 ข้อมูลรถ(ปี/model/ยี่ห้อ)", key="btn2a"):
            st.session_state["input_bot2"] = "ข้อมูลรถ(ปี/model/ยี่ห้อ)"
        if col2.button("📌 VMI ที่เหมาะกับลูกค้าคืออะไร", key="btn2b"):
            st.session_state["input_bot2"] = "VMI ที่เหมาะกับลูกค้าคืออะไร"
        if col3.button("📌 ช่องทางที่ลูกค้าจ่ายได้", key="btn2c"):
            st.session_state["input_bot2"] = "ช่องทางที่ลูกค้าจ่ายได้"

        for msg in st.session_state["messages_bot2"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        with st.form(key="form2"):
            cols = st.columns([10, 1])
            with cols[0]:
                st.session_state["input_bot2"] = st.text_input(
                    "ถามคำถาม...",
                    value=st.session_state["input_bot2"],
                    key="input2",
                    label_visibility="collapsed",
                    placeholder="ถามคำถาม..."
                )
            with cols[1]:
                submitted = st.form_submit_button("➤")

        if submitted and st.session_state["input_bot2"]:
            prompt = st.session_state["input_bot2"].strip()
            if prompt == "เปลี่ยนหัวข้อ":
                st.chat_message("assistant").markdown("เปลี่ยนหัวข้อให้แล้วค่ะ 😊")
                st.session_state["selected_topic"] = None
                st.rerun()  # แทนที่ experimental_rerun()
            else:
                st.session_state["messages_bot2"].append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                reply = ask_openai(st.session_state["messages_bot2"], "คุณคือผู้ให้คำแนะนำด้านประกันภัยรถยนต์")
                st.chat_message("assistant").markdown(reply)
                st.session_state["messages_bot2"].append({"role": "assistant", "content": reply})
                st.session_state["input_bot2"] = ""

elif st.session_state["selected_topic"] == "credit":
    tabs = st.tabs(["\U0001F4B3 Credit Card"])
    with tabs[0]:
        st.subheader("💳 Credit Card")

        col1, col2, col3 = st.columns(3)
        if col1.button("📌 ลูกค้าถือบัตรประเภทไหน status ของบัตรเป็นอย่างไร", key="btn3a"):
            st.session_state["input_bot3"] = "ลูกค้าถือบัตรประเภทไหน status ของบัตรเป็นอย่างไร"
        if col2.button("📌 ลูกค้ามี Lifestyle เป็นอย่างไร", key="btn3b"):
            st.session_state["input_bot3"] = "ลูกค้ามี Lifestyle เป็นอย่างไร"
        if col3.button("📌 Promotion/Privilage ที่เหมาะกับลูกค้า", key="btn3c"):
            st.session_state["input_bot3"] = "Promotion/Privilage ที่เหมาะกับลูกค้า"

        for msg in st.session_state["messages_bot3"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        with st.form(key="form3"):
            cols = st.columns([10, 1])
            with cols[0]:
                st.session_state["input_bot3"] = st.text_input(
                    "ถามคำถาม...",
                    value=st.session_state["input_bot3"],
                    key="input3",
                    label_visibility="collapsed",
                    placeholder="ถามคำถาม..."
                )
            with cols[1]:
                submitted = st.form_submit_button("➤")

        if submitted and st.session_state["input_bot3"]:
            prompt = st.session_state["input_bot3"].strip()
            if prompt == "เปลี่ยนหัวข้อ":
                st.chat_message("assistant").markdown("เปลี่ยนหัวข้อเรียบร้อยค่ะ ยินดีให้บริการเรื่องอื่น ๆ ได้เสมอ 💁‍♀️")
                st.session_state["selected_topic"] = None
                st.rerun()  # แทนที่ experimental_rerun()
            else:
                st.session_state["messages_bot3"].append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                reply = ask_openai(st.session_state["messages_bot3"], "คุณคือเลขาส่วนตัวที่ช่วยสรุปงานและแนะนำการใช้บัตรเครดิตอย่างชาญฉลาด")
                st.chat_message("assistant").markdown(reply)
                st.session_state["messages_bot3"].append({"role": "assistant", "content": reply})
                st.session_state["input_bot3"] = ""
