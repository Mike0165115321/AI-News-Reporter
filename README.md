# 🤖 AI News Reporter

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**AI News Reporter** คือโปรเจคเว็บแอปพลิเคชัน AI อัจฉริยะที่สามารถค้นหาและสรุปข่าวสารล่าสุดจากหลากหลายแหล่งข่าวทั่วโลกได้แบบเรียลไทม์ ผู้ใช้สามารถถามคำถามเกี่ยวกับสถานการณ์ปัจจุบัน แล้ว AI จะทำการค้นหาข้อมูลจากแหล่งข่าวที่น่าเชื่อถือและสรุปเป็นภาษาไทยที่เข้าใจง่าย

โปรเจคนี้ถูกสร้างขึ้นด้วยสถาปัตยกรรม RAG (Retrieval-Augmented Generation) ซึ่งเป็นเทคโนโลยีที่ทันสมัยและมีประสิทธิภาพสูง

<!-- เพิ่ม GIF การทำงานของโปรแกรมที่นี่จะทำให้ README น่าสนใจขึ้นมาก! -->
<!-- ![Demo GIF](link_to_your_demo.gif) -->

---

## 🚀 คุณสมบัติเด่น (Features)

-   **หน้าบ้าน (Frontend):** UI แบบแชทที่สวยงามและใช้งานง่ายในธีม Dark Mode สร้างด้วย HTML, CSS, และ JavaScript
-   **หลังบ้าน (Backend):** API Server ที่ทรงพลัง สร้างด้วย Python และ FastAPI
-   **สมองของ AI:** ขับเคลื่อนด้วย Google Gemini (ผ่าน API) พร้อม Prompt Engineering ที่ออกแบบมาอย่างดี
-   **ระบบค้นหาอัจฉริยะ (RAG):**
    -   รวบรวมข่าวจากหลายแหล่ง (NewsAPI, RSS Feeds)
    -   ใช้ Sentence Transformers (`paraphrase-multilingual-MiniLM-L12-v2`) ในการสร้าง Vector Embeddings
    -   ใช้ FAISS ในการทำ Vector Search ที่รวดเร็วและแม่นยำ
-   **หลายภาษา:** สามารถค้นหาและสรุปข่าวได้ทั้งจากแหล่งข่าวภาษาไทยและภาษาอังกฤษ
-   **แสดงแหล่งข่าวอ้างอิง:** เพิ่มความน่าเชื่อถือโดยการแสดง Context ที่ AI ใช้ในการสร้างคำตอบ

---

## 🛠️ การติดตั้งและเริ่มต้นใช้งาน (Setup & Installation)

ทำตามขั้นตอนเหล่านี้เพื่อรันโปรเจคบนเครื่องของคุณ

### 1. โคลนโปรเจค (Clone Repository)

```
git clone https://github.com/Mike0165115321/AI-News-Reporter.git
cd AI-News-Reporter
```

###  2. สร้างและเปิดใช้งาน Virtual Environment
การสร้างสภาพแวดล้อมเสมือนจะช่วยให้ไลบรารีของโปรเจคนี้ไม่ไปปะปนกับโปรเจคอื่น

สำหรับ macOS / Linux:
```
python3 -m venv venv
source venv/bin/activate
```

สำหรับ Windows:
```
python -m venv venv
venv\Scripts\activate
```
หลังจากรันคำสั่ง activate คุณจะเห็น (venv) ขึ้นมาหน้าชื่อ Terminal

### 3. ติดตั้ง Dependencies ที่จำเป็น
ติดตั้งไลบรารีทั้งหมดที่โปรเจคต้องการจากไฟล์ requirements.txt
```
pip install -r requirements.txt
```

### 4. ตั้งค่า API Keys
โปรเจคนี้ต้องการ API Key 2 ตัวในการทำงาน
สร้างไฟล์ .env: สร้างไฟล์ใหม่ชื่อ .env ในโฟลเดอร์หลักของโปรเจค
เปิดไฟล์ .env แล้วใส่ Key ของคุณ:

```
# Key จาก https://newsapi.org/
NEWS_KEY="ใส่คีย์_NewsAPI_ของคุณที่นี่"

# Key จาก Google AI Studio (https://aistudio.google.com/app/apikey)
GEMINI_API_KEY="ใส่คีย์_Gemini_ของคุณที่นี่"
```


### ⚙️ ขั้นตอนการรันโปรเจค (Running the Project)
โปรเจคนี้มี 2 ขั้นตอนหลักในการทำงาน: การสร้างฐานข้อมูลข่าว และ การรันเซิร์ฟเวอร์
ขั้นตอนที่ 1: สร้างฐานข้อมูลข่าว (ทำครั้งแรก หรือเมื่อต้องการอัปเดตข่าว)
ขั้นตอนนี้คือการสั่งให้ AI ไปรวบรวมข่าวสารล่าสุดมาสร้างเป็น "ห้องสมุด" สำหรับการค้นหา
⚠️ คำเตือน: ขั้นตอนนี้อาจใช้เวลานาน (30 นาที - 1 ชั่วโมง) ขึ้นอยู่กับความเร็วอินเทอร์เน็ตและจำนวนข่าว โปรดใจเย็นๆ และปล่อยให้โปรแกรมทำงานจนเสร็จ

```
python manage_news.py
```
หลังจากรันเสร็จ คุณจะเห็นไฟล์ news_faiss.index และ news_mapping.json ถูกสร้างขึ้นในโฟลเดอร์ data/news_index/


### ขั้นตอนที่ 2: รันเซิร์ฟเวอร์ AI นักข่าว
หลังจากสร้างฐานข้อมูลข่าวเสร็จแล้ว ให้รันเซิร์ฟเวอร์เพื่อเริ่มใช้งานแอปพลิเคชัน
```
python main.py
```

เมื่อเซิร์ฟเวอร์ทำงานแล้ว คุณจะเห็นข้อความ:
INFO: Uvicorn running on http://0.0.0.0:8010

### ขั้นตอนที่ 3: เปิดใช้งาน
เปิดเว็บเบราว์เซอร์ (เช่น Chrome, Firefox)
```
เข้าไปที่ URL: http://127.0.0.1:8010
```
คุณจะเห็นหน้าแชทของ AI News Reporter และสามารถเริ่มถามคำถามได้ทันที!

### 📂 โครงสร้างโปรเจค (Project Structure)
```
AI_NEWS_REPORTER/
│
├── core/                 # ห้องเครื่องยนต์: กลไกหลักของระบบ
│   ├── config.py         # โหลดค่าจาก .env
│   ├── news_rag_engine.py# เครื่องมือค้นหาข่าว (RAG)
│   └── prompts.py        # เก็บ Persona และ Prompt ของ AI
│
├── data/                 # คลังข้อมูล
│   └── news_index/       # ที่เก็บ Index และ Mapping ของข่าว
│
├── frontend/             # ส่วนหน้าบ้าน (UI)
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── .env                  # ไฟล์เก็บ API Keys (สร้างเอง)
├── .gitignore            # ไฟล์ที่ Git จะไม่สนใจ
├── main.py               # จุดเริ่มต้น: รัน FastAPI Server
├── manage_news.py        # เครื่องมือสร้างฐานข้อมูลข่าว
├── news_generation.py    # ส่วนที่เรียก Gemini API เพื่อสร้างคำตอบ
└── requirements.txt      # รายการ Dependencies ทั้งหมด

```

### 📄 License
โปรเจคนี้อยู่ภายใต้ลิขสิทธิ์ของ MIT License

### **สรุปการเปลี่ยนแปลง:**
1.  **เพิ่มตาราง Technology Stack:** ช่วยให้คนเห็นภาพรวมเทคโนโลยีที่ใช้ได้อย่างรวดเร็ว
2.  **จัดรูปแบบ Header:** ใช้ `###` สำหรับหัวข้อย่อย ทำให้มีลำดับชั้นและอ่านง่ายขึ้น
3.  **จัดรูปแบบ Code Block:** ใส่คำสั่งทั้งหมดใน Code Block (```) ที่ถูกต้อง ทำให้คัดลอกไปใช้งานได้ง่าย
4.  **เพิ่มส่วน License:** ทำให้โปรเจคดูสมบูรณ์และเป็นมาตรฐานสากล

นอกนั้นเนื้อหาของคุณดีเยี่ยมอยู่แล้วครับ แค่ปรับการจัดรูปแบบเล็กน้อยก็ทำให้ `README.md` ของคุณดูดีขึ้นมากเลยครับ!
