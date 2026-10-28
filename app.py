from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# የቴሌግራም ቦት ማዋቀሪያ ከ Environment Variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')

# የጨዋታው የፊት ገጽ (HTML/JavaScript) በቀጥታ እዚህ ተጻፈ
HTML_PAGE = """
<!DOCTYPE html>
<html lang="am">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telebirr Spin Game</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f4; text-align: center; padding: 20px; }
        .container { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); max-width: 400px; margin: auto; }
        input, button { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
        button { background: #2481cc; color: white; border: none; font-size: 16px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Hbዱር bet - Spin Game</h2>
        <input type="text" id="depTxId" placeholder="የ Telebirr Transaction ID ያስገቡ">
        <input type="text" id="depPhone" placeholder="የስልክ ቁጥር (09...)">
        <select id="bonusChoice">
            <option value="200">200 ብር ዲፖዚት</option>
        </select>
        <button onclick="submitDeposit()">ክፍያ አረጋግጥ (Deposit)</button>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();

        function submitDeposit() {
            let txid = document.getElementById("depTxId").value.trim();
            let phone = document.getElementById("depPhone").value.trim();
            let bonusVal = document.getElementById("bonusChoice").value;

            if (!txid || !phone) {
                alert("እ和ይት የ Transaction ID እና የስልክ ቁጥር ያስገቡ!");
                return;
            }

            let user = tg.initDataUnsafer && tg.initDataUnsafer.user ? tg.initDataUnsafer.user : { id: 12345, first_name: "Guest" };
            let depositAmount = Number(bonusVal);

            fetch('/api/deposit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    user_id: user.id, 
                    user_name: user.first_name, 
                    phone: phone, 
                    tx_id: txid, 
                    amount: depositAmount 
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("የደምብሂት እና የክፍያ ጥያቄ በአስተዳዳሪው ዘንድ ተላክቷል! ክፍያው ሲረጋገጥ አካውንትዎ ይስተካከላል።");
                } else {
                    alert("ስህተት ተፈጥሯል: " + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert("የኔትወርክ ስህተት አጋጥሟል!");
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML_PAGE

@app.route('/api/deposit', methods=['POST'])
def deposit():
    data = request.json
    user_name = data.get('user_name')
    phone = data.get('phone')
    tx_id = data.get('tx_id')
    amount = data.get('amount')

    # ወደ አድሚን ቴሌግራም ማሳወቂያ መላኪያ
    if BOT_TOKEN and ADMIN_CHAT_ID:
        message = (
            f"🔔 **አዲስ የዲፖዚት ጥያቄ መጥቷል!**\n\n"
            f"👤 ስም: {user_name}\n"
            f"📞 ስልክ: {phone}\n"
            f"💰 መጠን: {amount} ብር\n"
            f"🔖 Transaction ID: `{tx_id}`"
        )
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": ADMIN_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print(f"Telegram error: {e}")

    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

