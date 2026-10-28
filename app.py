from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# የቴሌግራም ቦት ማዋቀሪያ ከ Environment Variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')

HTML_PAGE = """
<!DOCTYPE html>
<html lang="am">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telebirr Spin Game & Wallet</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f4; text-align: center; padding: 10px; margin: 0; }
        .container { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); max-width: 400px; margin: auto; }
        input, select, button { width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
        button { background: #2481cc; color: white; border: none; font-size: 16px; cursor: pointer; }
        canvas { background: #fff; margin-top: 10px; border-radius: 50%; box-shadow: 0 0 5px rgba(0,0,0,0.2); }
        .balance-box { background: #eef2f3; padding: 10px; border-radius: 5px; margin-bottom: 10px; font-weight: bold; color: #333; }
        .section-box { background: #fff9e6; border: 1px solid #ffeeba; padding: 10px; border-radius: 5px; margin-top: 15px; }
        .withdraw-box { background: #e8f8f5; border: 1px solid #a3e4d7; padding: 10px; border-radius: 5px; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Hbዱር bet - Spin & Wallet</h2>
        
        <!-- የባላንስ ማሳያ -->
        <div class="balance-box">
            የቀሪ ሂሳብዎ (Balance): <span id="userBalance" style="color: #27ae60;">200 ብር</span>
        </div>

        <!-- የስፒን ጨዋታ ክፍል -->
        <div id="gameSection">
            <canvas id="wheel" width="220" height="220"></canvas>
            <button onclick="spinWheel()">እጣ አሽክርክር (Spin - 20 ብር)</button>
            <p id="resultText" style="font-weight: bold; color: #333; margin-top: 5px;"></p>
        </div>

        <!-- ዲፖዚት ጥያቄ ክፍል -->
        <div class="section-box">
            <h4 style="color: #d9534f; margin: 5px 0;">📥 ዲፖዚት ማድረጊያ</h4>
            <input type="number" id="depAmount" placeholder="ሊያስገቡት የሚፈልጉት መጠን (ብር)">
            <input type="text" id="depTxId" placeholder="የ Telebirr Transaction ID">
            <input type="text" id="depPhone" placeholder="ስልክ ቁጥር (09...)">
            <button onclick="sendDepositRequest()" style="background: #27ae60;">የዲፖዚት ትእዛዝ ላክ</button>
        </div>

        <!-- ዊድድሮው (Withdraw) የገንዘብ ማውጫ ክፍል -->
        <div class="withdraw-box">
            <h4 style="color: #16a085; margin: 5px 0;">📤 ገንዘብ ማውጫ (Withdraw)</h4>
            <input type="number" id="withdrawAmount" placeholder="ሊያወጡት የሚፈልጉት መጠን (ብር)">
            <input type="text" id="withdrawPhone" placeholder="የሚቀበሉበት ስልክ ቁጥር (Telebirr)">
            <button onclick="sendWithdrawRequest()" style="background: #16a085;">የገንዘብ ማውጫ ጥያቄ ላክ</button>
        </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();

        let currentBalance = 200; // መነሻ ባላንስ

        const canvas = document.getElementById("wheel");
        const ctx = canvas.getContext("2d");
        const sectors = [
            { color: "#f1c40f", text: "50 ብር" },
            { color: "#2ecc71", text: "100 ብር" },
            { color: "#e74c3c", text: "0 ብር" },
            { color: "#3498db", text: "200 ብር" },
            { color: "#9b59b6", text: "500 ብር" }
        ];
        const arc = Math.PI / (sectors.length / 2);
        let ang = 0;
        let spinning = false;

        function drawSector(sector, i) {
            const angs = arc * i;
            ctx.save();
            ctx.beginPath();
            ctx.fillStyle = sector.color;
            ctx.moveTo(110, 110);
            ctx.arc(110, 110, 110, angs, angs + arc, false);
            ctx.lineTo(110, 110);
            ctx.fill();
            ctx.restore();

            ctx.save();
            ctx.translate(110, 110);
            ctx.rotate(angs + arc / 2);
            ctx.textAlign = "right";
            ctx.fillStyle = "#fff";
            ctx.font = "bold 13px sans-serif";
            ctx.fillText(sector.text, 95, 8);
            ctx.restore();
        }

        function drawWheel() {
            ctx.clearRect(0, 0, 220, 220);
            ctx.save();
            ctx.translate(110, 110);
            ctx.rotate(ang);
            ctx.translate(-110, -110);
            sectors.forEach(drawSector);
            ctx.restore();
        }

        function spinWheel() {
            if (currentBalance < 20) {
                alert("ባላንስዎ አልቋል! እባክዎ መጀመሪያ ዲፖዚት ያድርጉ።");
                return;
            }

            if (spinning) return;
            spinning = true;
            currentBalance -= 20; // ለስፒን 20 ብር ይቀንሳል
            document.getElementById("userBalance").innerText = currentBalance + " ብር";

            let randomAngle = Math.random() * 1000 + 2000;
            let currentRotation = 0;
            let speed = 50;

            let spinInterval = setInterval(() => {
                currentRotation += speed;
                ang = currentRotation * Math.PI / 180;
                drawWheel();
                speed *= 0.98;

                if (speed < 0.5) {
                    clearInterval(spinInterval);
                    spinning = false;
                    document.getElementById("resultText").innerText = "ስፒኑ ተጠናቋል!";
                }
            }, 30);
        }

        drawWheel();

        // ዲፖዚት ጥያቄ መላኪያ
        function sendDepositRequest() {
            let amount = document.getElementById("depAmount").value.trim();
            let txid = document.getElementById("depTxId").value.trim();
            let phone = document.getElementById("depPhone").value.trim();

            if (!amount || !txid || !phone) {
                alert("እባክዎ የዲፖዚት መረጃዎችንሙሉ በሙሉ ይሙሉ!");
                return;
            }

            let user = tg.initDataUnsafe && tg.initDataUnsafe.user ? tg.initDataUnsafe.user : { id: 12345, first_name: "Guest", username: "unknown" };

            fetch('/api/deposit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: user.id, user_name: user.first_name, username: user.username || "없음", phone: phone, tx_id: txid, amount: amount })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) alert("የዲፖዚት ትእዛዝዎ ተልኳል!");
            });
        }

        // ዊድድሮው (ገንዘብ ማውጫ) ጥያቄ መላኪያ
        function sendWithdrawRequest() {
            let amount = Number(document.getElementById("withdrawAmount").value.trim());
            let phone = document.getElementById("withdrawPhone").value.trim();

            if (!amount || !phone) {
                alert("እባክዎ የማውጫውን መጠን እና ስልክ ቁጥር ያስገቡ!");
                return;
            }

            if (amount > currentBalance) {
                alert("ባላንስዎ ከጠየቁት ገንዘብ ያነሰ ነው! ማውጣት የሚችሉት ከቀሪ ሂሳብዎ መጠን ጋር ነው።");
                return;
            }

            // ከሂሳብ ላይ መቀነስ
            currentBalance -= amount;
            document.getElementById("userBalance").innerText = currentBalance + " ብር";

            let user = tg.initDataUnsafe && tg.initDataUnsafe.user ? tg.initDataUnsafe.user : { id: 12345, first_name: "Guest", username: "unknown" };

            fetch('/api/withdraw', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: user.id, user_name: user.first_name, username: user.username || "없음", phone: phone, amount: amount })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert("የገንዘብ ማውጫ (Withdraw) ጥያቄዎ ተልኳል! አድሚኑ ሲያረጋግጠው ይለቀቅልዎታል።");
                }
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
    if BOT_TOKEN and ADMIN_CHAT_ID:
        msg = f"🔔 **አዲስ የዲፖዚት ጥያቄ**\n\n👤 ስም: {data.get('user_name')}\n📞 ስልክ: {data.get('phone')}\n💰 መጠን: {data.get('amount')} ብር\n🔖 TX ID: `{data.get('tx_id')}`"
        keyboard = {"inline_keyboard": [[{"text": f"✅ {data.get('amount')} ብር ዲፖዚት አረጋግጥ", "callback_data": f"approve_dep_{data.get('user_id')}_{data.get('amount')}"}]]}
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": ADMIN_CHAT_ID, "text": msg, "parse_mode": "Markdown", "reply_markup": keyboard})
    return jsonify({"success": True})

@app.route('/api/withdraw', methods=['POST'])
def withdraw():
    data = request.json
    if BOT_TOKEN and ADMIN_CHAT_ID:
        msg = f"📤 **አዲስ የገንዘብ ማውጫ (Withdraw) ጥያቄ**\n\n👤 ስም: {data.get('user_name')}\n📞 ስልክ: {data.get('phone')}\n💰 የሚወጣው መጠን: {data.get('amount')} ብር"
        keyboard = {"inline_keyboard": [[{"text": f"✅ {data.get('amount')} ብር ዊድድሮው አረጋግጥ", "callback_data": f"approve_with_{data.get('user_id')}_{data.get('amount')}"}]]}
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": ADMIN_CHAT_ID, "text": msg, "parse_mode": "Markdown", "reply_markup": keyboard})
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
