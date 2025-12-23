from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from openai import OpenAI
import pandas as pd
import re
from thefuzz import fuzz
from dotenv import load_dotenv
import os
import webbrowser
import random


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI(title="TI-Bot (Service + Room + Dept Version)")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




photo_dir = os.path.join(os.path.dirname(__file__), "..", "datasets", "Staff_Photos_V2")
if os.path.exists(photo_dir):
    print(f"✅ Serving photos from: {photo_dir}")
else:
    print("⚠️ Photo folder not found!")
app.mount("/photos", StaticFiles(directory=photo_dir), name="photos")





image_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "image")
if os.path.exists(image_dir):
    print(f"✅ Serving images from: {image_dir}")
else:
    print("⚠️ Image folder not found!")
app.mount("/image", StaticFiles(directory=image_dir), name="image")



mp4_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "mp4")
if os.path.exists(mp4_dir):
    print(f"✅ Serving videos from: {mp4_dir}")
else:
    print("⚠️ MP4 folder not found!")
app.mount("/mp4", StaticFiles(directory=mp4_dir), name="mp4")




@app.get("/")
async def serve_homepage():
    """Serve the main chatbot interface"""
    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
    return FileResponse(os.path.join(frontend_dir, "index2.html"))


@app.get("/about")
async def serve_about():
    """Serve the about page"""
    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
    return FileResponse(os.path.join(frontend_dir, "about_us", "about.html"))



about_us_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "about_us")
if os.path.exists(about_us_dir):
    print(f"✅ Serving about_us from: {about_us_dir}")
    app.mount("/about_us", StaticFiles(directory=about_us_dir, html=True), name="about_us")
else:
    print("⚠️ about_us folder not found!")




datasets_dir = os.path.join(os.path.dirname(__file__), "..", "datasets")
staff_rooms = pd.read_excel(os.path.join(datasets_dir, "STAFF_ROOM_Dataset_V3.xlsx")).fillna("")
general_rooms = pd.read_excel(os.path.join(datasets_dir, "ROOMS.xlsx")).fillna("")
departments = pd.read_excel(os.path.join(datasets_dir, "University_Departments_Dataset_Beautiful.xlsx")).fillna("")
general = pd.read_excel(os.path.join(datasets_dir, "University_Chatbot_Dataset_v2.xlsx")).fillna("")




def clean(text):
    return re.sub(r"[^a-z0-9\s-]", "", str(text).lower())




def detect_intent(q):
    qn = clean(q)

    if any(w in qn for w in [
        "who are you", "what are you", "why were you made", "about ti bot", "what is ti bot",
        "tell me about yourself", "information about you"
    ]):
        return "about_bot"

    if any(w in qn for w in
           ["tiu", "tishk", "tishk international university", "tiu-sulaimani", "tiu sulaimani", "university info"]):
        return "university"

    if any(w in qn for w in ["i want to", "i wanna", "where can i", "i need to", "i need", "i want"]):
        return "service"


    if "who is" in qn and any(
            title in qn for title in ["head of", "dean of", "president", "vice president", "director"]):
        return "staff"

    if any(t in qn for t in ["mr", "ms", "mrs", "dr", "professor", "lecturer"]) and "where" in qn:
        return "staff"

    if any(w in qn for w in ["who is", "whos", "mr", "ms", "lecturer", "professor"]):
        return "staff"




    if any(w in qn for w in
           ["department", "major", "study", "graduate", "engineering", "architecture", "civil", "computer",
            "information technology", "nursing", "dentistry", "pharmacy", "physiotherapy", "english language"]):
        return "department"

    if "how many" in qn:
        return "room"





    if any(x in qn for x in ["g-", "room", "office"]):
        return "room"



    if ("what is" in qn or "where is" in qn):
        # Check if it has a room number pattern (G-X or X-X)
        if re.search(r'\b[gG]-?\d+\b|\b\d-\d+\b', qn):
            return "room"
        # If no room number, check if it's asking about department
        if any(dept_word in qn for dept_word in
               ["engineering", "department", "technology", "architecture", "civil", "computer"]):
            return "department"

    if any(w in qn for w in
           ["hi", "hello", "hey", "how are you", "joke", "good", "great", "fine", "well", "excellent", "awesome",
            "thank you", "thanks", "im good", "im great", "im fine", "doing good", "doing great", "doing well",
            "not good", "bad", "sad", "tired"]):
        return "chat"

    return "general"





def is_not_found_answer(answer):
    """Check if the answer indicates information was not found"""
    not_found_phrases = [
        "don't have information",
        "don't have any information",
        "don't have that information",
        "can't find information",
        "not available",
        "please check the name",
        "double-check",
        "doesn't exist",
        "might not exist",
        "sorry",
        "i don't know",
        "at the moment",
        "right now",
        "currently"
    ]
    answer_lower = answer.lower()
    return any(phrase in answer_lower for phrase in not_found_phrases)








def about_bot_answer(q):
    text = (
        "I am TI BOT 🤖 — an intelligent assistant developed for Tishk International University – Sulaimani. "
        "I was created to help students, staff, and visitors by providing accurate information about rooms, "
        "departments, staff locations, services, and general university assistance.\n\n"
        "TI BOT was designed and developed as a modern AI solution to support digital transformation at TIU-Sulaimani — "
        "and to make university services faster, smarter, and more accessible. "
        "I'm here to assist you with any questions about the university!"
    )
    return {"text": text, "photo": None}  # No photo







def university_answer(q):
    text = (
        "Tishk International University – Sulaimani (TIU-Sulaimani) is one of the region's leading private "
        "universities, established in 2014 with a mission to deliver world-class education and contribute to "
        "scientific progress and community development. The university offers diverse undergraduate programs "
        "across Engineering, Health Sciences, Architecture, Education, Computer Science, and Business, all taught "
        "in English to meet global academic and industrial standards."
    )
    photo_url = "http://127.0.0.1:8002/photos/tiu-campus.jpg"
    return {"text": text, "photo": photo_url}








def staff_answer(q):
    q_clean = clean(q)
    best_row, best_score = None, 0

    # Search in staff_rooms dataset only
    for _, row in staff_rooms.iterrows():
        name_text = clean(row["Person_in_Room"])
        role_text = clean(row["Purpose"])
        combined = f"{name_text} {role_text}"

        score = max(
            fuzz.partial_ratio(q_clean, name_text),
            fuzz.partial_ratio(q_clean, role_text),
            fuzz.token_set_ratio(q_clean, combined),
        )

        if score > best_score:
            best_row, best_score = row, score

    if best_score < 60:
        return {
            "text": "Sorry, I don't have any information about this person. Please check the name.",
            "photo": None
        }

    person = best_row["Person_in_Room"]
    role = best_row["Purpose"]
    floor = best_row["Floor"]
    room_num = best_row["Room_Number"]
    desc = best_row["Description"]
    photo_name = str(best_row["Photo"]).strip()

    if "where" in q_clean:
        text = f"{person} is in room {room_num} on the {floor} floor."
    else:
        text = f"{person} is our {role}, in room {room_num} on the {floor} floor. {desc}"

    photo_url = None
    if photo_name and photo_name.lower() not in ["nan", "", "none"]:
        photo_url = f"http://127.0.0.1:8002/photos/{photo_name}"

    return {"text": text, "photo": photo_url}








def service_answer(q):
    q_clean = clean(q)

    visit_keywords = ["see", "visit", "meet", "talk to", "speak to", "go to"]
    wants_to_visit_someone = any(k in q_clean for k in visit_keywords)

    if wants_to_visit_someone:
        best_row, best_score = None, 0
        # Search in staff_rooms dataset only
        for _, row in staff_rooms.iterrows():
            name_text = clean(row["Person_in_Room"])
            score = fuzz.partial_ratio(q_clean, name_text)
            if score > best_score:
                best_row, best_score = row, score

        if best_row is not None and best_score >= 65:
            person = best_row["Person_in_Room"]
            room_num = best_row["Room_Number"]
            floor = best_row["Floor"]
            role = best_row["Purpose"]
            return f"You can visit {person}, {role}, in room {room_num} on the {floor} floor."

    service_map = {
        "register": ("G-16", "Ms. Eman Nasih", "registration officer"),
        "registration": ("G-16", "Ms. Eman Nasih", "registration officer"),
        "admission": ("G-16", "Ms. Eman Nasih", "registration officer"),
        "enroll": ("G-16", "Ms. Eman Nasih", "registration officer"),
        "enrol": ("G-16", "Ms. Eman Nasih", "registration officer"),
        "accounting": ("G-17", "Mr. Muhammed Jamal", "accounting officer"),
        "pay": ("G-17", "Mr. Muhammed Jamal", "accounting officer"),
        "payment": ("G-17", "Mr. Muhammed Jamal", "accounting officer"),
        "fees": ("G-17", "Mr. Muhammed Jamal", "accounting officer"),
        "tuition": ("G-17", "Mr. Muhammed Jamal", "accounting officer"),
    }

    for key, (room, person, job) in service_map.items():
        if key in q_clean:
            return f"You can go to room {room} and meet {person}, the {job}."

    return "Could you tell me a bit more about what you want to do? I'll guide you to the right place."








def room_answer(q):
    q_clean = clean(q)

    if "how many" in q_clean:
        # Count labs from general_rooms dataset
        if "it" in q_clean or "computer" in q_clean:
            count = 0
            for _, row in general_rooms.iterrows():
                purpose = clean(row["Purpose"])
                dept = clean(row["Department"])
                if "lab" in purpose and ("information technology" in dept or "computer engineering" in dept):
                    count += 1
            return f"There are {count} labs shared by IT and Computer Engineering departments."

        department_labs = {
            "nursing": "nursing",
            "dentistry": "dentistry",
            "physiotherapy": "physiotherapy",
            "architecture": "architecture",
            "pharmacy": "pharmacy"
        }

        for key, dept in department_labs.items():
            if key in q_clean:
                count = 0
                for _, row in general_rooms.iterrows():
                    purpose = clean(row["Purpose"])
                    dept_clean = clean(row["Department"])
                    if "lab" in purpose and dept in dept_clean:
                        count += 1
                return f"There are {count} {dept} labs in the university."


        total_labs = sum("lab" in clean(row["Purpose"]) for _, row in general_rooms.iterrows())
        return f"There are {total_labs} labs in the university."


    room_pattern = r"\b([Gg]-?\d{1,3}|\d-\d{1,3})\b"
    match = re.search(room_pattern, q, re.IGNORECASE)

    if match:
        rn = match.group().upper()
        if rn.startswith("G") and "-" not in rn:
            rn = "G-" + rn[1:]


        for _, row in staff_rooms.iterrows():
            if str(row["Room_Number"]).upper() == rn:
                purpose = row["Purpose"]
                person = row["Person_in_Room"]
                floor = row["Floor"]

                if person:
                    return f"Room {rn} is on the {floor} floor. It is used for {purpose}, and {person} uses this room."
                else:
                    return f"Room {rn} is on the {floor} floor. It is used for {purpose}."


        for _, row in general_rooms.iterrows():
            if str(row["Room_Number"]).upper() == rn:
                purpose = row["Purpose"]
                person = row["Person_in_Room"]
                floor = row["Floor"]

                if person:
                    return f"Room {rn} is on the {floor} floor. It is used for {purpose}, and {person} uses this room."
                else:
                    return f"Room {rn} is on the {floor} floor. It is used for {purpose}."

        return "I can't find information about this room. Please double-check the number."

    return "Could you please tell me the room number again? I want to be sure I find the right room."




def department_answer(q):
    q_clean = clean(q)

    dept_abbr = {
        "mls": "medical laboratory science",
        "it": "information technology",
        "arch": "architecture engineering",
        "architecture": "architecture engineering",
        "dent": "dentistry",
        "elt": "english language teaching",
        "physio": "physiotherapy",
        "computer": "computer engineering"
    }
    for abbr, full in dept_abbr.items():
        if f" {abbr} " in f" {q_clean} ":
            q_clean = q_clean.replace(abbr, full)

    best_row, best_score = None, 0
    for _, row in departments.iterrows():
        score = fuzz.partial_ratio(q_clean, clean(row["Department"]))
        if score > best_score:
            best_row = row
            best_score = score

    if best_row is None or best_score < 70:
        return "This department is not available in the university database. Please check the name — it might not exist."

    return (
        f"{best_row['Department']} – {best_row['Description']} "
        f"After graduation: {best_row['Career_After_Graduation']}."
    )




def general_answer(q):
    try:
        q_clean = clean(q)
        best_row = None
        best_score = 0

        for _, row in general.iterrows():
            intent_text = clean(str(row.get("Emotion_Intent", "")))
            example_text = clean(str(row.get("Example_Question", "")))

            if intent_text.strip() == "" and example_text.strip() == "":
                continue

            intent_score = fuzz.partial_ratio(q_clean, intent_text) if intent_text else 0
            example_score = fuzz.partial_ratio(q_clean, example_text) if example_text else 0

            combined = int(example_score * 0.6 + intent_score * 0.4)

            if combined > best_score:
                best_score = combined
                best_row = row

        if best_row is not None and best_score >= 70:  # ← Changed from 55 to 70
            return str(best_row["Response"])

        return "I'm not sure about that. Could you ask me something about the university? For example, room locations, staff offices, or department information."

    except Exception as e:
        return "It seems like we have a server error for this question — it will be fixed as soon as possible."




def chat_answer(q):
    q_clean = clean(q)

    # Greetings - warmer responses
    if any(x in q_clean for x in ["hi", "hello", "hey"]):
        return random.choice([
            "Hi there! 😊 I'm doing great, thank you! How are you doing today?",
            "Hello! 😊 I'm good, thanks for asking! How about you?",
            "Hey! 😊 I'm doing well! How are you today?",
        ])




    if any(response in q_clean for response in
           ["good", "great", "fine", "well", "excellent", "awesome", "im good", "im great", "im fine", "doing good",
            "doing great", "doing well"]):
        return random.choice([
            "That's wonderful to hear! 😊 What can I help you with today?",
            "I'm so happy to hear that! 🌟 How can I assist you?",
            "Fantastic! 🎉 What brings you here today?",
            "That's great! 😊 What would you like to know about TIU?",
        ])


    if any(response in q_clean for response in
           ["not good", "bad", "sad", "tired", "exhausted", "stressed", "not well"]):
        return random.choice([
            "I'm sorry to hear that! 😔 I hope I can help brighten your day. What can I do for you?",
            "Oh no! I hope things get better soon. 💙 How can I assist you today?",
            "I'm sorry you're feeling that way. Is there anything I can help you with at TIU?",
        ])


    if "how are you" in q_clean:
        return "I'm doing great and ready to help! 😄 How about you?"


    if any(thanks in q_clean for thanks in ["thank you", "thanks", "thank u", "thx"]):
        return random.choice([
            "You're very welcome! 😊 Happy to help!",
            "My pleasure! 🌟 Anytime you need assistance, I'm here!",
            "You're welcome! 😊 Feel free to ask if you need anything else!",
        ])


    if "joke" in q_clean:
        return random.choice([
            "Why did the computer go to therapy? Because it had too many bytes! 😄",
            "Why don't robots panic? Because they have steel nerves! 🤖",
            "What's a computer's favorite snack? Microchips! 🍪",
        ])


    return "I'm always here if you want to talk or ask about the university! 😊"



def rewrite_friendly(raw_answer, intent):
    try:
        styles = {
            "staff": "friendly",
            "room": "helpful",
            "department": "informative",
            "general": "calm",
            "chat": "warm",
            "service": "friendly",
            "error": "apologetic"
        }
        style = styles.get(intent, "friendly")

        prompt = (
            f"Rewrite this in a natural, friendly tone (no greetings).\n"
            f"Style: {style}\n\n"
            f"Answer:\n{raw_answer}"
        )

        result = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return result.choices[0].message.content.strip()

    except:
        return raw_answer





def ask_router(question: str):
    intent = detect_intent(question)

    if intent == "creator":
        result = creator_answer()
        cleaned = rewrite_friendly(result["text"], intent)
        return {"intent": intent, "answer": cleaned, "photo": result["photo"], "not_found": False}

    if intent == "staff":
        result = staff_answer(question)
        cleaned = rewrite_friendly(result["text"], intent)
        not_found = is_not_found_answer(result["text"])
        return {"intent": intent, "answer": cleaned, "photo": result["photo"], "not_found": not_found}

    elif intent == "service":
        answer = service_answer(question)
    elif intent == "room":
        answer = room_answer(question)
    elif intent == "department":
        answer = department_answer(question)
    elif intent == "chat":
        answer = chat_answer(question)
    elif intent == "university":
        result = university_answer(question)
        cleaned = rewrite_friendly(result["text"], intent)
        return {"intent": intent, "answer": cleaned, "photo": result["photo"], "not_found": False}
    elif intent == "about_bot":
        result = about_bot_answer(question)
        cleaned = rewrite_friendly(result["text"], intent)
        return {"intent": intent, "answer": cleaned, "photo": result["photo"], "not_found": False}
    else:
        answer = general_answer(question)

    friendly = rewrite_friendly(answer, intent)
    not_found = is_not_found_answer(friendly)
    return {"intent": intent, "answer": friendly, "photo": None, "not_found": not_found}



@app.get("/api")
async def root():
    return {
        "message": "✅ TI-Bot API is running!",
        "endpoints": {
            "/ask": "Ask questions (e.g., /ask?question=Where is Mr. Rozh?)",
            "/docs": "Interactive API documentation",
        },
        "status": "active"
    }


@app.get("/ask")
async def ask_question(question: str):
    return ask_router(question)




if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8002)

