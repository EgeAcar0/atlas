import os
import sys
import json
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# --- AYARLAR ---
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "atlas_memory.json")
MODEL_NAME = "kimi" # Ollama'daki modelinin tam adı

# Ollama İstemcimiz (Yerel Yapay Zeka)
llm_client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama_sifresi_onemsiz"
)

# Global MCP Değişkenleri
mcp_session = None
mcp_stdio = None
openai_araclari = []
conversation_history = []

# --- GELİŞMİŞ HAFIZA SİSTEMİ (Senin Mükemmel Yapın) ---
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

    def add_knowledge(self, info: str):
        if info not in self.memory["knowledges"]:
            self.memory["knowledges"].append(info)
            self.save_to_file()
            return True
        return False

    def get_context(self):
        if not self.memory["knowledges"]:
            return "Şu an hafızanda özel bir bilgi yok."
        return "\n".join([f"- {k}" for k in self.memory["knowledges"]])

brain = MemorySystem()

# --- FASTAPI LIFESPAN (Uygulama Açılırken MCP'yi Başlatır) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global mcp_session, mcp_stdio, openai_araclari
    
    print("⏳ A.T.L.A.S. Sunucusu ve MCP Alet Çantası Başlatılıyor...")
    
    # mcp_server.py dosyamızın yolunu buluyoruz
    mcp_server_path = os.path.join(os.path.dirname(__file__), "mcp_server.py")
    
    server_ayarlari = StdioServerParameters(
        command=sys.executable,
        args=[mcp_server_path]
    )
    
    mcp_stdio_context = stdio_client(server_ayarlari)
    mcp_stdio = await mcp_stdio_context.__aenter__()
    okuyucu, yazici = mcp_stdio
    
    mcp_session_context = ClientSession(okuyucu, yazici)
    mcp_session = await mcp_session_context.__aenter__()
    await mcp_session.initialize()
    
    # Sunucudaki araçları çekip OpenAI (Ollama) formatına çeviriyoruz
    araclar = await mcp_session.list_tools()
    for arac in araclar.tools:
        openai_araclari.append({
            "type": "function",
            "function": {
                "name": arac.name,
                "description": arac.description,
                "parameters": arac.inputSchema
            }
        })
    print("✅ MCP Bağlantısı Kuruldu! Araçlar Yüklendi.")
    
    yield # Uygulama çalışıyor...
    
    print("🛑 A.T.L.A.S. Kapanıyor, MCP bağlantısı kesiliyor...")
    await mcp_session_context.__aexit__(None, None, None)
    await mcp_stdio_context.__aexit__(None, None, None)

app = FastAPI(lifespan=lifespan)

class ChatRequest(BaseModel):
    user_input: str

# --- API ENDPOINT ---
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    global conversation_history
    
    user_text = request.user_input.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Boş mesaj gönderilemez.")

    # V2.0 System Prompt (Çok daha sade, çünkü model aletleri otomatik tanıyor)
    system_prompt = f"""
    Sen A.T.L.A.S.'sın. (Automated Tech & Life Assistance System). Kullanıcının (Ege) asistanısın.
    Konuşma tarzın: Kısa, net, doğal ve seslendirmeye uygun. (Markdown yok, Madde işareti yok).
    Kullanıcıya daima "Efendim" diye hitap et.
    
    HAFIZANDAKİ BİLGİLER:
    {brain.get_context()}
    
    GÖREVİN:
    Sana verilen fonksiyonları/araçları kullanarak kullanıcının isteklerini yerine getir.
    Eğer bir araç çalıştırırsan, kendi bilgini uydurma, doğrudan araçtan gelen veriyi kullanıcıya doğal bir dille söyle.
    
    HAFIZA VE DURUM KOMUTLARI (Bunları metnin sonuna ekle):
    - Hafızaya yeni bilgi eklemen gerekirse: <CMD:SAVE>Bilgi</CMD:SAVE>
    - Seansı açık tutmak (dinlemeye devam etmek) için: <CMD:STAY_ACTIVE></CMD:STAY_ACTIVE>
    - Kullanıcı işini bitirdiğinde: <CMD:GO_STANDBY></CMD:GO_STANDBY>
    """

    messages = [{"role": "system", "content": system_prompt}] + conversation_history
    messages.append({"role": "user", "content": user_text})

    try:
        # 1. Ollama'yı Çağırıyoruz (Aletlerle Birlikte)
        yanit = await llm_client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=openai_araclari
        )
        
        asistan_mesaji = yanit.choices[0].message
        final_cevap = asistan_mesaji.content or ""

        # 2. Model Bir Araç Kullanmak İstedi Mi?
        if asistan_mesaji.tool_calls:
            messages.append(asistan_mesaji)
            
            for tool_call in asistan_mesaji.tool_calls:
                fonksiyon_adi = tool_call.function.name
                parametreler_json = tool_call.function.arguments
                
                import json
                param_dict = json.loads(parametreler_json)
                print(f"🛠️ MCP Aracı Tetiklendi: {fonksiyon_adi} -> {param_dict}")
                
                # Aracı MCP üzerinden çalıştırıyoruz
                arac_sonucu = await mcp_session.call_tool(fonksiyon_adi, param_dict)
                
                # Sonucu modele geri veriyoruz
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": fonksiyon_adi,
                    "content": str(arac_sonucu.content)
                })
            
            # 3. Model araçtan aldığı veriyi okuyup bize son bir Türkçe cevap üretiyor
            ikinci_yanit = await llm_client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages
            )
            final_cevap = ikinci_yanit.choices[0].message.content or ""

        clean_response = final_cevap

        # 4. HİBRİT YAPI: Hafıza ve Seans Kontrollerini Yakala (Eski sistemin en iyi özelliği)
        if "<CMD:SAVE>" in clean_response:
            try:
                parts = clean_response.split("<CMD:SAVE>")
                info = parts[1].split("</CMD:SAVE>")[0].strip()
                brain.add_knowledge(info)
                print(f"🧠 Hafızaya Eklendi: {info}")
                clean_response = clean_response.replace(f"<CMD:SAVE>{info}</CMD:SAVE>", "").strip()
            except:
                pass

        # Geçmişi Güncelle
        conversation_history.append({"role": "user", "content": user_text})
        conversation_history.append({"role": "assistant", "content": clean_response})
        if len(conversation_history) > 15:
            conversation_history = conversation_history[-15:]

        # Frontend'e sadece temiz metni gönder
        return {"response": clean_response}

    except Exception as e:
        print(f"❌ Kritik Hata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Terminalden çalıştırmak için: python atlas_v2.py
    uvicorn.run(app, host="127.0.0.1", port=8000)