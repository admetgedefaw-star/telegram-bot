import os
from flask import Flask, request, jsonify, render_template_string
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

app = Flask(__name__)

# ከ Render Environment Variables የሚነበቡ (ወይም በቀጥታ ማስገባት የሚችሏቸው)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "YOUR_ADMIN_CHAT_ID_HERE")

bot = Bot(token=BOT_TOKEN)

# የውሸት ዳታቤዝ (በምርት ሰርቨር ላይ MongoDB ወይም SQLite መጠቀም ይመረታል)
user_balances = {} 

@app.route('/')
def home():
    # index.html ፋይሉን እዚህ ጋር በቀጥታ ማንበብ ይቻላል
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# ተጠቃሚው ዴፖዚት ሲያደርግ የሚላክ ሪኬስት መቀበያ
@app.route('/api/deposit', methods=['POST'])
def api_deposit():
    data = request.json
    user_id = data.get("user_id")
    user_name = data.get("user_name", "N/A")
    phone = data.get("phone")
    tx_id = data.get("tx_id")
    amount = data.get("amount")

    if not phone or not tx_id:
        return jsonify({"success": False, "message": "እባክዎን መረጃዎችን በትክክል ይሙሉ!"}), 400

    # ለአድሚን የሚላክ መልእክት እና አዝራር
    keyboard = [
        [InlineKeyboardButton("✅ ክፍያው ደርሷል (Balance ጫን)", callback_data=f"approve_{user_id}_{amount}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg_text = (
        f"<b>🎁 አዲስ የዲፖዚት ጥያቄ</b>\n"
        f"👤 ዩዘር ID: <code>{user_id}</code>\n"
        f"👤 ስም: {user_name}\n"
        f"📱 ስልክ: <code>{phone}</code>\n"
        f"💳 Trans ID: <code>{tx_id}</code>\n"
        f"💰 የተጠየቀው መጠን: <b>{amount} ብር</b>"
    )

    try:
        # ቦቱ በኩል ለአድሚን መላክ
        bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg_text, reply_markup=reply_markup, parse_mode="HTML")
        return jsonify({"success": True, "message": "ጥያቄዎ ተልኳል!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
