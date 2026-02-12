import wikipedia # type: ignore

# Wikipedia dilini Türkçe yapıyoruz
wikipedia.set_lang("tr")

def search_wiki(query: str):
    """
    Wikipedia'dan özet bilgi getirir.
    """
    try:
        # sentences=2 ile kısa bir özet alıyoruz
        summary = wikipedia.summary(query, sentences=2)
        return f"Wikipedia Özeti: {summary}"
    except wikipedia.exceptions.PageError:
        return "Wikipedia'da bu konu bulunamadı."
    except wikipedia.exceptions.DisambiguationError:
        return "Konu çok genel, daha spesifik olmalısın."
    except Exception as e:
        return f"Araştırma hatası: {str(e)}"