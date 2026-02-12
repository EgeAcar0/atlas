# 🤖 A.T.L.A.S. (Automated Tech & Life Assistance System)

A.T.L.A.S., Groq API ve açık kaynaklı büyük dil modelleri (LLM - 120b) gücüyle çalışan, modüler ve sesli komut odaklı kişisel bir yapay zeka asistanıdır. 

Sıradan sohbotların aksine A.T.L.A.S., yerel bilgisayar sisteminizle doğrudan etkileşime girer, hafızasını dinamik olarak yönetir ve özel XML benzeri etiketler (`<CMD:...>`) kullanarak dış dünyadan gerçek zamanlı veri çeker.

## ✨ Özellikler

* **⚡ Ultra Düşük Gecikme:** Groq altyapısı sayesinde sesli asistan dinamiklerine uygun, anında yanıt süreleri.
* **🧠 Dinamik Hafıza Yönetimi:** A.T.L.A.S., öğrendiği bilgileri anlık olarak kaydedebilir, silebilir veya güncelleyebilir.
* **💻 Sistem Kontrolü:** Terminal, CMD, Paint, Spotify, Steam, Minecraft gibi uygulamaları doğrudan çalıştırabilme yeteneği.
* **🌍 Gerçek Zamanlı Veri:** * API üzerinden güncel hava durumu çekme.
  * Wikipedia entegrasyonu ile derinlemesine araştırma.
  * YouTube'dan video oynatma ve web sitelerini tarayıcıda açma.
* **📅 Görev ve Seans Yönetimi:** Ödev ekleme/kontrol etme sistemleri ve `<CMD:STAY_ACTIVE>` / `<CMD:GO_STANDBY>` komutlarıyla akıllı dinleme durum kontrolü.
* **🧩 Modüler Mimari:** Her yetenek ayrı bir Python dosyasında barınır, merkez `atlas.py` üzerinden API sunucusu olarak çalışır ve Frontend bağlantısı kurar.

## 🛠️ Kullanılan Teknolojiler

* **Ana Dil:** Python
* **LLM Sağlayıcı:** Groq API (120b Open-Source Model)
* **Araç Çağırma (Tool Calling):** Özel System Prompt ve XML tabanlı komut ayrıştırma motoru
* **İletişim:** REST API (Backend - Frontend haberleşmesi için)

## 🚀 Kurulum

1. Repoyu klonlayın:
   ```bash
   git clone [https://github.com/EgeAcar0/atlas.git](https://github.com/EgeAcar0/atlas.git)
2. Gerekli kütüphaneleri kurun:
   ```bash
   pip install -r requirements.txt
3. API Anahtarınızı Ayarlayın:
   ```bash
   .env dosyasını oluşturup içine ekleyin.
   ```
4. Frontend'i Çalıştırın:
   ```bash
   python frontend/new_frontend.py
   ```
5. Backend'i Çalıştırın:
   ```bash
   python atlas.py
   ```

Bu proje Ege Acar tarafından geliştirilmiştir.