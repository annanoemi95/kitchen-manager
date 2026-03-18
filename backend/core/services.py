import os
import json
import re
from google import genai
from django.conf import settings
from dotenv import load_dotenv

# Carichiamo le variabili d'ambiente per lo sviluppo locale
load_dotenv()

class AIService:
    """
    Service Layer per gestire l'integrazione con Google Gemini (SDK 2026).
    Isola la logica AI dal resto del framework Django per garantire manutenibilità.
    """
    
    @staticmethod
    def analyze_reviews(reviews_queryset):
        # 1. Recupero configurazione (da settings di Django o file .env)
        api_key = getattr(settings, 'GEMINI_API_KEY', os.getenv("GEMINI_API_KEY"))
        
        if not api_key:
            return {"error": "Configurazione AI mancante. Verificare GEMINI_API_KEY."}

        try:
            # 2. Inizializzazione del nuovo Client ufficiale
            client = genai.Client(api_key=api_key)
            model_id = 'gemini-2.5-flash'

            # 3. Preparazione dei dati delle recensioni per il prompt
            data_text = "\n".join([
                f"- Valutazione {r.rating}/5: {r.comment}" 
                for r in reviews_queryset if r.comment
            ])

            if not data_text:
                return {"error": "Non ci sono recensioni con commenti sufficienti per l'analisi."}

            # 4. Prompt Engineering strutturato per output JSON
            prompt = f"""
            Sei un analista esperto del progetto 'Kitchen Manager'.
            Analizza i seguenti feedback dei clienti e restituisci ESCLUSIVAMENTE un oggetto JSON.
            
            Feedback da analizzare:
            {data_text}
            
            Struttura JSON richiesta:
            {{
              "sentiment_score": 1-5,
              "main_complaint": "descrizione sintetica della lamentela principale o null",
              "top_dish": "nome del piatto più apprezzato o null",
              "advice": "consiglio pratico e strategico per lo chef"
            }}
            """

            # 5. Chiamata all'API tramite il nuovo metodo generate_content
            response = client.models.generate_content(
                model=model_id,
                contents=prompt
            )
            
            # Recupero del testo della risposta
            raw_text = response.text
            
            # 6. Parsing robusto del JSON tramite espressione regolare
            json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            
            if json_match:
                return json.loads(json_match.group())
            
            return {"error": "L'IA non ha restituito un formato JSON valido."}

        except Exception as e:
            # Gestione errori centralizzata
            return {"error": f"Errore durante l'interazione con l'AI: {str(e)}"}