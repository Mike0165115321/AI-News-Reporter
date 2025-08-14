# news_generation.py

import google.generativeai as genai
from core.config import settings
from core.prompts import NEWS_PERSONA_PROMPT

class NewsGenerator:
    def __init__(self, model_name: str = "gemini-1.5-flash-latest"):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in the .env file.")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        self.model = genai.GenerativeModel(model_name)
        self.prompt_template = NEWS_PERSONA_PROMPT
        print(f"🤖 News Generator initialized with model: {model_name}")

    def generate_answer(self, query: str, context: str) -> str:
        """
        สร้างคำตอบจาก Query และ Context ที่ได้รับมา
        """
        try:
            prompt = self.prompt_template.format(context_from_rag=context, user_query=query)
            
            print("  - Sending prompt to Gemini API...")
            response = self.model.generate_content(prompt)
            
            if response.parts:
                final_answer = response.text.strip()
                print("  - Successfully received answer from Gemini.")
                return final_answer
            else:
                print("  - ⚠️ Gemini response was empty or blocked.")
                return "ขออภัยค่ะ ระบบไม่สามารถสร้างคำตอบได้ในขณะนี้ อาจเนื่องมาจากข้อจำกัดด้านความปลอดภัย"

        except Exception as e:
            print(f"❌ Gemini API Error: {e}")
            return "ขออภัยค่ะ เกิดข้อผิดพลาดระหว่างการประมวลผลกับ AI ค่ะ"

if __name__ == '__main__':
    try:
        generator = NewsGenerator()
        
        test_context = """
--- ข่าวอ้างอิง 1 ---
หัวข้อ: Apple เปิดตัวชิป M4 ใหม่ใน iPad Pro, เร็วกว่า M2 ถึง 50%
แหล่งข่าว: TechCrunch
URL: http://example.com/m4
เนื้อหา: Apple ประกาศเปิดตัวชิป M4 ที่ผลิตบนสถาปัตยกรรม 3nm รุ่นที่สอง มาพร้อม Neural Engine ที่เร็วที่สุดเท่าที่เคยมีมา ประมวลผลได้ 38 ล้านล้านคำสั่งต่อวินาที ทำให้เหมาะกับงาน AI และ Machine Learning

--- ข่าวอ้างอิง 2 ---
หัวข้อ: iPad Pro รุ่นใหม่บางเฉียบ พร้อมจอ Tandem OLED สุดล้ำ
แหล่งข่าว: The Verge
URL: http://example.com/ipad
เนื้อหา: นอกจากชิป M4 แล้ว iPad Pro ใหม่ยังมากับหน้าจอ Ultra Retina XDR ที่ใช้เทคโนโลยี Tandem OLED ทำให้สว่างและแม่นยำกว่าเดิม ตัวเครื่องบางเบาเป็นประวัติการณ์
"""
        test_query = "ชิป M4 ของ Apple มีอะไรใหม่บ้าง?"
        
        answer = generator.generate_answer(query=test_query, context=test_context)
        
        print("\n--- Generated Answer ---")
        print(answer)

    except (ValueError, Exception) as e:
        print(f"Error: {e}")