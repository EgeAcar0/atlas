import os
import json
import uvicorn
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv


# .env dosyasını yükle
load_dotenv()

app = FastAPI()

# --- AYARLAR ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY") 
MEMORY_FILE = "atlas_memory.json"
MODEL_NAME = "openai/gpt-oss-120b"

client = Groq(api_key=GROQ_API_KEY)

class ChatRequest(BaseModel):
    user_input: str

# --- GELİŞMİŞ HAFIZA SİSTEMİ ---
class MemorySystem:
    def __init__(self):
        self.memory = self.load_memory()

    def load_memory(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {"knowledges": []}
        return {"knowledges": []}

    def save_to_file(self):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=4)

    def add_memory(self, content):
        """Yeni bilgi ekler"""
        new_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": content
        }
        self.memory["knowledges"].append(new_entry)
        self.save_to_file()
        print(f"[HAFIZA] Eklendi: {content}")

    def delete_memory(self, content_fragment):
        """İçinde 'content_fragment' geçen hafıza kayıtlarını siler"""
        original_count = len(self.memory["knowledges"])
        # Eşleşmeyenleri tut, eşleşenleri at (Filtreleme)
        self.memory["knowledges"] = [
            k for k in self.memory["knowledges"] 
            if content_fragment.lower() not in k["content"].lower()
        ]
        if len(self.memory["knowledges"]) < original_count:
            self.save_to_file()
            print(f"[HAFIZA] Silindi: {content_fragment}")

    def update_memory(self, old_fragment, new_content):
        """Eskiyi siler, yeniyi ekler"""
        self.delete_memory(old_fragment)
        self.add_memory(new_content)
        print(f"[HAFIZA] Güncellendi: {old_fragment} -> {new_content}")

    def get_context(self):
        context = ""
        # Son 15 bilgiyi al (Context window şişmesin diye)
        recent_memories = self.memory.get("knowledges", [])[-15:]
        for item in recent_memories:
            context += f"- {item['content']}\n"
        return context

brain = MemorySystem()

# --- FONKSİYONLAR ---
try:
    from backend.functions.weather_func import get_weather
    from backend.functions.general_func import open_website, get_system_stats
    from backend.functions.search_wiki_func import search_wiki
    from backend.functions.play_on_youtube_func import play_on_youtube
    from backend.functions.open_app_func import open_app
    from backend.functions.homework_func import add_homework, check_homework
except ImportError:
    # Fallback if imports are tricky due to directory structure
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), 'functions'))
    from weather_func import get_weather
    from general_func import open_website, get_system_stats
    from search_wiki_func import search_wiki
    from play_on_youtube_func import play_on_youtube
    from open_app_func import open_app
    from homework_func import add_homework, check_homework

# --- GLOBAL KONUŞMA GEÇMİŞİ ---
conversation_history = []

# --- LLM FONKSİYONU ---
def get_atlas_response(user_text):
    global conversation_history
    now = datetime.now()
    
    # --- SİSTEM KOMUTLARI ---
    system_prompt = f"""
    Sen A.T.L.A.S.'sın. (Automated Tech & Life Assistance System).
    Kullanıcının (Ege) asistanısın.
    
    ŞU AN: {now.strftime("%Y-%m-%d %H:%M:%S")} ({now.strftime("%A")})
    
    BİLDİKLERİN (HAFIZA):
    {brain.get_context()}
    
    KURALLAR (ÇOK ÖNEMLİ):
    1. Konuşma tarzın: Kısa, net, doğal ve seslendirmeye uygun. (Markdown yok, Madde işareti yok).
    2. Kullanıcıya "Efendim" diye hitap et.
    3. HAFIZA YÖNETİMİ: Bilgi ekle, değiştir veya sil için şu etiketleri kullan:
       - Yeni Bilgi: <CMD:SAVE>Bilgi</CMD:SAVE>
       - Silmek için: <CMD:DELETE>Silinecek Bilgi</CMD:DELETE>
       - Güncelleme için: <CMD:UPDATE>Eski Bilgi | Yeni Bilgi</CMD:UPDATE>
    4. FONKSİYON ÇAĞRILARI VE SEANS YÖNETİMİ: 
       - Hava durumu: <CMD:WEATHER>şehir_adı</CMD:WEATHER> (ı yerine i kullan).
       - YouTube: <CMD:YOUTUBE>konu</CMD:YOUTUBE>
       - Wikipedia: <CMD:WIKI>konu</CMD:WIKI>
       - Web Sitesi: <CMD:OPEN_URL>url</CMD:OPEN_URL>
       - Uygulama Aç: <CMD:OPEN_APP>ad</CMD:OPEN_APP> (Geçerli adlar: hesap makinesi, not defteri, cmd, terminal, boya, paint, gezgin, dosyalar, steam, minecraft, modlu minecraft, spotify)
       - Ödev Ekle: <CMD:ADD_HOMEWORK>Tarih|Ders|Açıklama</CMD:ADD_HOMEWORK> (Tarih: YYYY-AA-GG)
       - Ödev Kontrol: <CMD:CHECK_HOMEWORK>Tarih</CMD:CHECK_HOMEWORK> (Tarih: YYYY-AA-GG)
       - Sistem: <CMD:GET_SYSTEM_STATS></CMD:GET_SYSTEM_STATS>
       - Kapat: <CMD:EXIT></CMD:EXIT>
       - Seans Kontrolü: <CMD:STAY_ACTIVE></CMD:STAY_ACTIVE> veya <CMD:GO_STANDBY></CMD:GO_STANDBY>
    5. WIKIPEDIA KURALI: Sadece kullanıcı açıkça "araştır", "search", "wikipedia'ya bak" veya "hakkında detaylı bilgi topla" gibi bir talepte bulunursa <CMD:WIKI> kullan. Genel sorular ("Cengiz Han kimdir?" vb.) için kendi bilgini kullan.
    6. KRİTİK KURAL: Eğer bir komut (<CMD:...>) kullanacaksan, konu hakkında KENDİ BİLGİNİ VERME. Sadece "Hemen bakıyorum efendim" de ve komutu ekle. Wikipedia veya hava durumu bilgisini asla tahmin etme.
    7. Eğer Wiki fonksiyonu uzun bir cevap verirse, kendin kısalt ve öyle söyle.
    8. Eğer kullanıcı "Günaydın" veya yeni uyandığını belli eden bir şey söylerse şöyle de "Günaydın efendim umarım güzel bir gün olur. <CMD:WEATHER>aydin</CMD:WEATHER> <CMD:STAY_ACTIVE></CMD:STAY_ACTIVE>"
    
    ÖRNEKLER:
    User: "Cengiz Han'ı araştır." -> Cevap: "Hemen araştırıyorum efendim. <CMD:WIKI>Cengiz Han</CMD:WIKI> <CMD:STAY_ACTIVE></CMD:STAY_ACTIVE>"
    User: "Aydın'da hava nasıl?" -> Cevap: "Hemen bakıyorum efendim. <CMD:WEATHER>aydin</CMD:WEATHER> <CMD:STAY_ACTIVE></CMD:STAY_ACTIVE>"
    User: "Cengiz Han kim?" -> Cevap: "Moğol İmparatorluğu'nun kurucusu ve ilk hükümdarıdır efendim. <CMD:STAY_ACTIVE></CMD:STAY_ACTIVE>"
    User: "Sağ ol Atlas, bu kadar." -> Cevap: "Rica ederim efendim, beklemedeyim. <CMD:GO_STANDBY></CMD:GO_STANDBY>"
    """

    # Mesaj geçmişini oluştur
    messages = [{"role": "system", "content": system_prompt}]
    
    # Son 10 mesaj çiftini ekle (Hafıza)
    for msg in conversation_history[-10:]:
        messages.append(msg)
    
    # Yeni kullanıcı mesajını ekle
    messages.append({"role": "user", "content": user_text})

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.6,
        max_tokens=512
    )
    
    full_response = completion.choices[0].message.content
    print(f"[DEBUG] Full Response: {full_response}")
    
    # --- KOMUT İŞLEME (PARSING) ---
    clean_response = full_response
    
    # 1. SAVE Komutu
    if "<CMD:SAVE>" in full_response:
        parts = full_response.split("<CMD:SAVE>")
        tag_content = parts[1].split("</CMD:SAVE>")[0].strip()
        brain.add_memory(tag_content)
        clean_response = clean_response.replace(f"<CMD:SAVE>{tag_content}</CMD:SAVE>", "").strip()

    # 2. DELETE Komutu
    if "<CMD:DELETE>" in full_response:
        parts = full_response.split("<CMD:DELETE>")
        tag_content = parts[1].split("</CMD:DELETE>")[0].strip()
        brain.delete_memory(tag_content)
        clean_response = clean_response.replace(f"<CMD:DELETE>{tag_content}</CMD:DELETE>", "").strip()

    # 3. UPDATE Komutu
    if "<CMD:UPDATE>" in full_response:
        parts = full_response.split("<CMD:UPDATE>")
        tag_content = parts[1].split("</CMD:UPDATE>")[0].strip()
        if "|" in tag_content:
            old_data, new_data = tag_content.split("|", 1)
            brain.update_memory(old_data.strip(), new_data.strip())
        else:
            brain.add_memory(tag_content)
        clean_response = clean_response.replace(f"<CMD:UPDATE>{tag_content}</CMD:UPDATE>", "").strip()
    
    # 4. WEATHER Komutu
    if "<CMD:WEATHER>" in full_response:
        parts = full_response.split("<CMD:WEATHER>")
        city = parts[1].split("</CMD:WEATHER>")[0].strip()
        weather_info = get_weather(city)
        # Raw tag'i hava durumu bilgisiyle değiştir
        clean_response = clean_response.replace(f"<CMD:WEATHER>{city}</CMD:WEATHER>", weather_info).strip()

    

    # 5. SEANS YÖNETİMİ (EXIT, STAY_ACTIVE, GO_STANDBY)
    # Bu etiketleri temizleyip en sona ekliyoruz (Frontend için)
    session_tag = ""
    if "<CMD:EXIT>" in full_response: session_tag = "<CMD:EXIT></CMD:EXIT>"
    elif "<CMD:STAY_ACTIVE>" in full_response: session_tag = "<CMD:STAY_ACTIVE></CMD:STAY_ACTIVE>"
    elif "<CMD:GO_STANDBY>" in full_response: session_tag = "<CMD:GO_STANDBY></CMD:GO_STANDBY>"

    # Tüm seans etiketlerini ana metinden temizle
    for tag in ["<CMD:EXIT></CMD:EXIT>", "<CMD:STAY_ACTIVE></CMD:STAY_ACTIVE>", "<CMD:GO_STANDBY></CMD:GO_STANDBY>"]:
        clean_response = clean_response.replace(tag, "").strip()

    # En sona tek bir seans etiketi ekle
    if session_tag:
        clean_response = f"{clean_response} {session_tag}"

    # 6. OPEN_URL Komutu
    if "<CMD:OPEN_URL>" in full_response:
        parts = full_response.split("<CMD:OPEN_URL>")
        url = parts[1].split("</CMD:OPEN_URL>")[0].strip()
        info = open_website(url)
        clean_response = clean_response.replace(f"<CMD:OPEN_URL>{url}</CMD:OPEN_URL>", info).strip()

    # 7. GET_SYSTEM_STATS Komutu
    if "<CMD:GET_SYSTEM_STATS>" in full_response:
        stats_info = get_system_stats()
        clean_response = clean_response.replace("<CMD:GET_SYSTEM_STATS></CMD:GET_SYSTEM_STATS>", stats_info).strip()

    # 8. YOUTUBE Komutu
    if "<CMD:YOUTUBE>" in full_response:
        parts = full_response.split("<CMD:YOUTUBE>")
        topic = parts[1].split("</CMD:YOUTUBE>")[0].strip()
        info = play_on_youtube(topic)
        clean_response = clean_response.replace(f"<CMD:YOUTUBE>{topic}</CMD:YOUTUBE>", info).strip()

    # 9. WIKI Komutu
    if "<CMD:WIKI>" in full_response:
        parts = full_response.split("<CMD:WIKI>")
        query = parts[1].split("</CMD:WIKI>")[0].strip()
        info = search_wiki(query)
        clean_response = clean_response.replace(f"<CMD:WIKI>{query}</CMD:WIKI>", info).strip()

    # 10. OPEN_APP Komutu
    if "<CMD:OPEN_APP>" in full_response:
        parts = full_response.split("<CMD:OPEN_APP>")
        app_name = parts[1].split("</CMD:OPEN_APP>")[0].strip()
        info = open_app(app_name)
        clean_response = clean_response.replace(f"<CMD:OPEN_APP>{app_name}</CMD:OPEN_APP>", info).strip()

    # 11. ADD_HOMEWORK Komutu
    if "<CMD:ADD_HOMEWORK>" in full_response:
        parts = full_response.split("<CMD:ADD_HOMEWORK>")
        content = parts[1].split("</CMD:ADD_HOMEWORK>")[0].strip()
        if "|" in content:
            try:
                date_str, lesson, description = [c.strip() for c in content.split("|", 2)]
                info = add_homework(date_str, lesson, description)
                clean_response = clean_response.replace(f"<CMD:ADD_HOMEWORK>{content}</CMD:ADD_HOMEWORK>", info).strip()
            except ValueError:
                clean_response = clean_response.replace(f"<CMD:ADD_HOMEWORK>{content}</CMD:ADD_HOMEWORK>", "Tarih formatı hatası.").strip()

    # 12. CHECK_HOMEWORK Komutu
    if "<CMD:CHECK_HOMEWORK>" in full_response:
        parts = full_response.split("<CMD:CHECK_HOMEWORK>")
        date_str = parts[1].split("</CMD:CHECK_HOMEWORK>")[0].strip()
        info = check_homework(date_str)
        clean_response = clean_response.replace(f"<CMD:CHECK_HOMEWORK>{date_str}</CMD:CHECK_HOMEWORK>", info).strip()

    

    if not clean_response.replace(session_tag, "").strip():
        clean_response = f"Anladım efendim. {session_tag}"

    # --- GEÇMİŞİ GÜNCELLE ---
    conversation_history.append({"role": "user", "content": user_text})
    conversation_history.append({"role": "assistant", "content": clean_response})
    
    # Hafızayı son 15 mesajla sınırla
    if len(conversation_history) > 15:
        conversation_history = conversation_history[-15:]

    return clean_response.strip()

# --- API ENDPOINT ---
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not request.user_input:
        raise HTTPException(status_code=400, detail="Boş mesaj")
    
    response_text = get_atlas_response(request.user_input)
    return {"response": response_text}

if __name__ == "__main__":
    print("A.T.L.A.S. Beyni (V2 - Memory Ops) Başlatılıyor...")
    uvicorn.run(app, host="127.0.0.1", port=8000)