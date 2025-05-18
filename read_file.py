import streamlit as st
import openai
import fitz  # PyMuPDF
import pandas as pd

# ตั้งค่า API Key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# -------------------------------
# ฟังก์ชันอ่านไฟล์
# -------------------------------
def read_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def read_txt(file):
    return file.read().decode("utf-8")

def read_csv(file):
    df = pd.read_csv(file)
    return df.to_string()

# -------------------------------
# ฟังก์ชันถาม GPT
# -------------------------------
def ask_gpt(content, question):
    messages = [
        {"role": "system", "content": "คุณคือผู้ช่วยที่ช่วยอ่านเอกสารและตอบคำถามอย่างชัดเจน"},
        {"role": "user", "content": f"เอกสาร:\n{content}\n\nคำถาม:\n{question}"}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.3,
        max_tokens=1024
    )
    return response["choices"][0]["message"]["content"]

# -------------------------------
# ส่วน UI ด้วย Streamlit
# -------------------------------
st.title("📄🧠 GPT ช่วยอ่านไฟล์แล้วตอบคำถาม")

uploaded_file = st.file_uploader("อัปโหลดไฟล์ (PDF, TXT, CSV)", type=["pdf", "txt", "csv"])
question = st.text_input("พิมพ์คำถามที่คุณอยากรู้จากไฟล์")

if uploaded_file and question:
    # อ่านเนื้อหาไฟล์
    if uploaded_file.name.endswith(".pdf"):
        content = read_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".txt"):
        content = read_txt(uploaded_file)
    elif uploaded_file.name.endswith(".csv"):
        content = read_csv(uploaded_file)
    else:
        st.error("ไฟล์ไม่รองรับ")
        content = None

    # ถ้ามีเนื้อหาให้ส่งไปยัง GPT
    if content:
        with st.spinner("กำลังวิเคราะห์ด้วย GPT..."):
            answer = ask_gpt(content, question)
            st.success("✅ คำตอบจาก GPT:")
            st.write(answer)
