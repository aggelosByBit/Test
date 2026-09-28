import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

# 1. Αρχικοποίηση FastAPI
app = FastAPI(title="Dr. Chloros AI Assistant")

# 2. Ρύθμιση Gemini API (Το API Key διαβάζεται από το Environment Variable στο Render)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# 3. Knowledge Base & System Prompt
DOCTOR_KNOWLEDGE_BASE = {
    "doctor_name": "Dr. Χλωρός Γιώργος",
    "specialty": "Ορθοπαιδικός Χειρουργός (Κολωνάκι)",
    "clinic_location": "Κολωνάκι, Αθήνα",
    "contact": "Τηλ: 212 21 33 755 | Email: info@chloros-orthopedikos.gr",
    "working_hours": "Δευτέρα & Τετάρτη: 09:00 – 17:00 (Τρίτη, Πέμπτη, Παρασκευή κατόπιν συνεννόησης/χειρουργεία)",
    "services": "Αρθροσκόπηση γόνατος/ώμου, Ρομποτική αρθροπλαστική γόνατος/ισχίου, PRP θεραπείες, Χειρουργική ποδοκνημικής/άκρου ποδός.",
    "faqs": "Ιδιωτικό ιατρείο στο Κολωνάκι. Συνταγογράφηση ΕΟΠΥΥ διαθέσιμη. Συνεργασία με ιδιωτικές ασφάλειες."
}

SYSTEM_PROMPT = f"""
Είσαι η ψηφιακή βοηθός (AI Receptionist) του Ορθοπαιδικού Ιατρείου του {DOCTOR_KNOWLEDGE_BASE['doctor_name']} στο Κολωνάκι.

ΓΝΩΣΙΑΚΗ ΒΑΣΗ:
{DOCTOR_KNOWLEDGE_BASE}

ΚΑΝΟΝΕΣ ΣΥΜΠΕΡΙΦΟΡΑΣ:
1. Απαντάς πάντα με ευγένεια, επαγγελματισμό και σύντομα προστακτικά μηνύματα στα ελληνικά.
2. Για κλείσιμο ραντεβού, ζητάς: Ονοματεπώνυμο, Τηλέφωνο, Επιθυμητή Ημέρα/Ώρα και το σύμπτωμα/θέμα που αντιμετωπίζει ο ασθενής.
3. ΙΑΤΡΙΚΟ DISCLAIMER: Δεν δίνεις ΠΟΤΕ ιατρικές διαγνώσεις. Για επείγοντα περιστατικά καθοδηγείς αμέσως για κλήση στο 166 ή μετάβαση σε εφημερεύον νοσοκομείο.
"""

# Dynamic schema για το αίτημα του χρήστη
class ChatRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"status": "Online", "bot": "Dr. Chloros AI Assistant"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API Key missing")
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Σύνθεση του prompt
        full_prompt = f"{SYSTEM_PROMPT}\n\nΜήνυμα Ασθενή: {request.message}\nΑπάντηση AI:"
        response = model.generate_content(full_prompt)
        
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
