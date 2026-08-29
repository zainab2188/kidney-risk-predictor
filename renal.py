import os
import urllib.parse
import telebot
from telebot import types
from dotenv import load_dotenv

# تحميل التوكن بأمان من ملف .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

user_states = {}
user_scores = {}
user_weights = {}

QUIZ_QUESTIONS = [
    {
        "q": "1️⃣ ما هي الوظيفة الأساسية للكليتين في الجسم؟",
        "options": ["تصفية الدم وإزالة السموم", "ضخ الدم للجسم", "هضم الطعام"],
        "answer": 0
    },
    {
        "q": "2️⃣ ما هو المسبب الأول والرئيسي لمرض الفشل الكلوي المزمن؟",
        "options": ["ارتفاع ضغط الدم والسكري", "البرد الشديد", "قلة الحركة"],
        "answer": 0
    },
    {
        "q": "3️⃣ هل يسبب مرض الكلى المبكر أي ألام واضحة دائماً؟",
        "options": ["نعم، ألم شديد فوراً", "لا، غالباً ما يبدأ بدون ألم (مرض صامت)", "يسبب صداع فقط"],
        "answer": 1
    },
    {
        "q": "4️⃣ ما هي الكمية اليومية الموصى بها عادة للماء للأشخاص الأصحاء؟",
        "options": ["أقل من 1 لتر", "2 إلى 3 لترات", "أكثر من 6 لترات"],
        "answer": 1
    },
    {
        "q": "5️⃣ كيف تؤثر المسكنات (مثل الإيبوبروفين) عند الاستخدام المفرط؟",
        "options": ["تقوي الكلى", "قد تسبب تلفاً وتراجعاً بوظائف الكلى", "لا تؤثر أبداً"],
        "answer": 1
    },
    {
        "q": "6️⃣ حسب إرشادات NKF، ما هو العنصر الغذائي الذي يجب على مرضى الكلى تقليله للحد من احتباس السوائل؟",
        "options": ["الصوديوم (الملح)", "الفيتامينات", "الألياف"],
        "answer": 0
    },
    {
        "q": "7️⃣ أي من هذه العلامات قد تدل على احتباس السوائل وفشل الكلى؟",
        "options": ["تساقط الشعر", "تورم القدمين والوجه", "جفاف العيون"],
        "answer": 1
    },
    {
        "q": "8️⃣ ما العنصر الذي يحتاج مريض الكلى للرقابة عليه لمنع اضطراب ضربات القلب؟",
        "options": ["البوتاسيوم", "الحديد", "الكالسيوم فقط"],
        "answer": 0
    },
    {
        "q": "9️⃣ ما هي الديلزة (الغسيل الكلوي)؟",
        "options": ["عملية جراحية لتغيير الكلى", "تقنية تنقية الدم البديلة عند الفشل الكلوي", "علاج بالأعشاب"],
        "answer": 1
    },
    {
        "q": "🔟 هل الفحص الدوري لـ (وظائف الكلى والسكر والضغط) يقي من تدهور الكلى؟",
        "options": ["نعم، الاكتشاف المبكر يمنع المضاعفات", "لا، الفحص لا يفيد", "فقط عند الشعور بالألم"],
        "answer": 0
    }
]

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    btn1 = types.KeyboardButton("⚖️ حاسبة الوزن السوائل")
    btn2 = types.KeyboardButton("🥗 دليل التغذية والأطعمة")
    btn3 = types.KeyboardButton("📋 قائمة تفقد يوم الجلسة")
    btn4 = types.KeyboardButton("📅 مواعيد الجلسات")
    btn5 = types.KeyboardButton("📝 اختبار الوعي الصحي (10 أسئلة)")
    btn6 = types.KeyboardButton("📚 تحميل الكتيب التثقيفي")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_states[message.chat.id] = None
    welcome_text = (
        "أهلاً بك في دليل صحة الكلى التفاعلي 🩺✨\n\n"
        "البوت المصمم للتثقيف الصحي والعناية بالمرضى.\n"
        "اختر إحدى الخدمات التفاعلية من القائمة أدناه:"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown', reply_markup=main_menu())

# ----------------------------------------------------

# ----------------------------------------------------
# ⚖️ 2. حاسبة الزيادة في الوزن
# ----------------------------------------------------
@bot.message_handler(func=lambda m: m.text == "⚖️ حاسبة الوزن السوائل")
def start_weight_calc(message):
    msg = bot.send_message(
        message.chat.id,
        "📏 حاسبة زيادة السوائل بين الجلسات:\n\nأدخل وزنك المستهدف بعد الجلسة الماضية بالكيلوغرام (مثال: 65):"
    )
    bot.register_next_step_handler(msg, process_dry_weight)

def process_dry_weight(message):
    try:
        dry_weight = float(message.text)
        user_weights[message.chat.id] = dry_weight
        msg = bot.send_message(
            message.chat.id,
            "⚖️ ممتاز، الآن أدخل وزنك الحالي اليوم بالكيلوغرام (مثال: 67.5):"
        )
        bot.register_next_step_handler(msg, process_current_weight)
    except ValueError:
        bot.send_message(message.chat.id, "❌ يرجى إدخال رقم صحيح لوزنك.")

def process_current_weight(message):
    try:
        current_weight = float(message.text)
        dry_weight = user_weights.get(message.chat.id, 0)
        weight_gain = current_weight - dry_weight
        
        if weight_gain < 0:
            res_text = f"⚖️ الوزن الحالي أقل من المستهدف بـ {abs(weight_gain):.1f} كغم. انتبه من انخفاض الضغط."
        elif weight_gain <= 1.5:
            res_text = f"✅ زيادة آمنة: ({weight_gain:.1f} كغم أو لتر سوائل)."
        elif 1.5 < weight_gain <= 2.5:
            res_text = f"⚠️ زيادة متوسطة: ({weight_gain:.1f} كغم).\nيُفضل تقليل السوائل والأملاح."
        else:
            res_text = f"🚨 تحذير - زيادة عالية: ({weight_gain:.1f} كغم).\nاحتباس عالي للسوائل، تواصل مع الطبيب فوراً."
            
        bot.send_message(message.chat.id, res_text, parse_mode="Markdown", reply_markup=main_menu())
    except ValueError:
        bot.send_message(message.chat.id, "❌ يرجى إدخال رقم صحيح.")

# ----------------------------------------------------
# 🥗 3. دليل التغذية والأطعمة
# ----------------------------------------------------
@bot.message_handler(func=lambda m: m.text == "🥗 دليل التغذية والأطعمة")
def nutrition_guide(message):
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    btn_banana = types.InlineKeyboardButton("🍌 الموز", callback_data="food_banana")
    btn_pot = types.InlineKeyboardButton("🥔 البطاطا", callback_data="food_potato")
    btn_cheese = types.InlineKeyboardButton("🧀 الأجبان والمالح", callback_data="food_cheese")
    btn_apple = types.InlineKeyboardButton("🍎 التفاح", callback_data="food_apple")
    btn_rice = types.InlineKeyboardButton("🍚 الأرز الأبيض", callback_data="food_rice")
    btn_dates = types.InlineKeyboardButton("🌴 التمر", callback_data="food_dates")
    inline_markup.add(btn_banana, btn_pot, btn_cheese, btn_apple, btn_rice, btn_dates)
    
    bot.send_message(
        message.chat.id,
        "🥗 دليل الأطعمة لمرضى الغسيل الكلوي:\nاختر الطعام لمعرفة نسبة البوتاسيوم/الفوسفور ومدى أمانه:",
        reply_markup=inline_markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('food_'))
def handle_food_query(call):
    food_info = {
        "food_banana": "🔴 الموز: عالي جداً بالبوتاسيوم ⚠️! يُفضل تجنبه.",
        "food_potato": "🟠 البطاطا: عالية بالبوتاسيوم. قشرها وقطعها وانقعها بالماء الدافئ قبل الطهي.",
        "food_cheese": "🔴 الأجبان والمالح: عالية بالفوسفور والصوديوم ⚠️!",
        "food_apple": "🟢 التفاح: آمن وصحي كخيار فاكهة منخفض البوتاسيوم 👍.",
        "food_rice": "🟢 الأرز الأبيض: خيار آمن وجيد ومنخفض الفوسفور والبوتاسيوم 👍.",
        "food_dates": "🔴 التمر: عالي جداً بالبوتاسيوم! يُنصح بالحذر الشديد منه."
    }
    text = food_info.get(call.data, "لا تتوفر معلومات عن هذا الطعام حالياً.")
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

# ----------------------------------------------------
# 📋 4. قائمة تفقد يوم الجلسة
# ----------------------------------------------------
@bot.message_handler(func=lambda m: m.text == "📋 قائمة تفقد يوم الجلسة")
def send_dialysis_checklist(message):
    checklist_text = (
        "📋 قائمة تفقد يوم الجلسة (Dialysis Checklist):\n\n"
        "1️⃣ علاج الضغط: هل أخذت علاج الضغط حسب تعليمات الطبيب؟\n"
        "2️⃣ وصلة الغسيل: هل تأكدت من نظافة وحماية مكان القسطرة أو الفيستولا؟\n"
        "3️⃣ العلامات الحيوية: هل قست وزنك وضغطك في المنزل؟\n"
        "4️⃣ الوجبة والماء: هل أخذت وجبة خفيفة ومطارة ماء محددة؟\n"
        "5️⃣ الملابس: هل ترتدي ملابس واسعة تتيح الوصول لوصلة الغسيل؟"
    )
    bot.send_message(message.chat.id, checklist_text, parse_mode="Markdown")

# ----------------------------------------------------
# 📅 5. مواعيد الجلسات
# ----------------------------------------------------

# ----------------------------------------------------
# 📅 5. مواعيد الجلسات (تخصيص حر للأيام)
# ----------------------------------------------------
user_selected_days = {}

DAYS_MAP = {
    "SAT": ("السبت", "SA"),
    "SUN": ("الأحد", "SU"),
    "MON": ("الإثنين", "MO"),
    "TUE": ("الثلاثاء", "TU"),
    "WED": ("الأربعاء", "WE"),
    "THU": ("الخميس", "TH"),
    "FRI": ("الجمعة", "FR")
}

def build_days_keyboard(chat_id):
    selected = user_selected_days.get(chat_id, [])
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    
    for code, (name, _) in DAYS_MAP.items():
        # إذا كان اليوم مختاراً نضع أمامه علامة صح ✅
        label = f"✅ {name}" if code in selected else name
        buttons.append(types.InlineKeyboardButton(label, callback_data=f"day_toggle_{code}"))
        
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("📥 تأكيد وإنشاء التنبيهات", callback_data="day_confirm"))
    return markup

@bot.message_handler(func=lambda m: m.text == "📅 مواعيد الجلسات")
def start_custom_schedule(message):
    user_selected_days[message.chat.id] = []  # تفريغ الاختيارات القديمة
    bot.send_message(
        message.chat.id,
        "📅 تحديد أيام الجلسات الخاص بك:\n"
        "اضغط على الأيام التي تجري فيها جلسات الغسيل لتحديدها، ثم اضغط على زر (تأكيد):",
        parse_mode="Markdown",
        reply_markup=build_days_keyboard(message.chat.id)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('day_toggle_'))
def toggle_day_selection(call):
    chat_id = call.message.chat.id
    day_code = call.data.replace('day_toggle_', '')
    
    if chat_id not in user_selected_days:
        user_selected_days[chat_id] = []
        
    if day_code in user_selected_days[chat_id]:
        user_selected_days[chat_id].remove(day_code)
    else:
        user_selected_days[chat_id].append(day_code)
        
    bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=call.message.message_id,
        reply_markup=build_days_keyboard(chat_id)
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "day_confirm")
def confirm_custom_schedule(call):
    chat_id = call.message.chat.id
    selected = user_selected_days.get(chat_id, [])
    
    if not selected:
        bot.answer_callback_query(call.id, "⚠️ يرجى اختيار يوم واحد على الأقل!", show_alert=True)
        return
        
    selected_names = [DAYS_MAP[code][0] for code in selected]
    byday_codes = ",".join([DAYS_MAP[code][1] for code in selected])
    
    days_text = "، ".join(selected_names)
    
    title = "🩺 موعد جلسة الغسيل الكلوي"
    details = f"تذكير بموعد الجلسة الميدانية في أيام: ({days_text})."
    
    google_cal_url = (
        "https://calendar.google.com/calendar/render?action=TEMPLATE"
        f"&text={urllib.parse.quote(title)}"
        f"&details={urllib.parse.quote(details)}"
        f"&recur=RRULE:FREQ=WEEKLY;BYDAY={byday_codes}"
    )
    
    inline_markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="📲 إضافة الجدول المخصص لتقويم هاتفك", url=google_cal_url)
    inline_markup.add(btn)
    
    bot.answer_callback_query(call.id)
    bot.send_message(
        chat_id,
        f"✅ تم تحديد جدولك بنجاح!\nالأيام المختارة: {days_text}\n\nاضغط على الزر أدناه لحفظ التنبيهات في تقويمك 🔔:",
        parse_mode="Markdown",
        reply_markup=inline_markup
    )

# ----------------------------------------------------
# 📝 6. اختبار الوعي الصحي
# ----------------------------------------------------
@bot.message_handler(func=lambda m: m.text == "📝 اختبار الوعي الصحي (10 أسئلة)")
def start_quiz(message):
    user_scores[message.chat.id] = 0
    send_quiz_question(message.chat.id, 0)

def send_quiz_question(chat_id, q_index):
    if q_index < len(QUIZ_QUESTIONS):
        q_data = QUIZ_QUESTIONS[q_index]
        markup = types.InlineKeyboardMarkup()
        for idx, option in enumerate(q_data["options"]):
            markup.add(types.InlineKeyboardButton(option, callback_data=f"q_{q_index}_{idx}"))
        bot.send_message(chat_id, q_data["q"], reply_markup=markup)
    else:
        score = user_scores.get(chat_id, 0)
        total = len(QUIZ_QUESTIONS)
        result_text = f"🏁 انتهى الاختبار!\n\nحصلت على: {score} من {total}\n\n"
        if score >= 8:
            result_text += "🥇 ممتاز جداً! لديك وعي صحي ممتاز."
        elif score >= 5:
            result_text += "🥈 جيد! معلوماتك صحيحة بشكل عام."
        else:
            result_text += "💡 فرصة للتعلم! ننصحك بقراءة دليل التغذية والكتيب."
        bot.send_message(chat_id, result_text, parse_mode='Markdown', reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data.startswith('q_'))

def handle_quiz_callback(call):
    parts = call.data.split('_')
    q_index = int(parts[1])
    selected_option = int(parts[2])
    
    if selected_option == QUIZ_QUESTIONS[q_index]["answer"]:
        user_scores[call.message.chat.id] = user_scores.get(call.message.chat.id, 0) + 1
        bot.answer_callback_query(call.id, "إجابة صحيحة! أحسنت ✅")
    else:
        bot.answer_callback_query(call.id, "إجابة خاطئة ❌")
        
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    send_quiz_question(call.message.chat.id, q_index + 1)

# ----------------------------------------------------
# 📚 7. تحميل الكتيب
# ----------------------------------------------------
@bot.message_handler(func=lambda m: m.text == "📚 تحميل الكتيب التثقيفي")
def send_pdf_booklet(message):
    bot.send_message(message.chat.id, "⏳ جاري إرسال الكتيب التثقيفي...")
    try:
        with open("guide.pdf", "rb") as pdf_file:
            bot.send_document(
                message.chat.id, 
                pdf_file, 
                caption="📖 كتيب التثقيف الصحي وصحة الكلى 🩺"
            )
    except FileNotFoundError:
        bot.send_message(
            message.chat.id, 
            "❌ لم يتم العثور على الملف! تأكدي من وجود guide.pdf في نفس مجلد الكود."
        )

# ----------------------------------------------------
# 🚀 تشغيل البوت الصحيح
# ----------------------------------------------------
print("🚀 البوت المتكامل يعمل الآن بنجاح...")
bot.remove_webhook()
bot.infinity_polling()
