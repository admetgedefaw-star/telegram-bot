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
    <title>ቴሌብር የፊደል እና ሉሲ ስፒን ጨዋታ</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f172a, #1e1b4b);
            color: #ffffff;
            text-align: center;
            padding: 5px;
            margin: 0;
            min-height: 100vh;
        }
        .container {
            width: 100%;
            max-width: 450px;
            margin: 0 auto;
            background: rgba(30, 41, 59, 0.98);
            backdrop-filter: blur(10px);
            padding: 15px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.8);
            border: 2px solid rgba(245, 158, 11, 0.7);
            box-sizing: border-box;
        }
        h1 { font-size: 20px; margin-bottom: 5px; color: #f59e0b; }
        .subtitle { font-size: 11px; color: #cbd5e1; margin-bottom: 10px; }
        
        .balance-box {
            font-size: 16px;
            margin: 8px 0;
            background: linear-gradient(90deg, rgba(255, 215, 0, 0.2), rgba(245, 158, 11, 0.1));
            padding: 8px;
            border-radius: 10px;
            color: #ffd700;
            border: 1px solid rgba(255, 215, 0, 0.5);
            font-weight: bold;
        }

        .result-display-banner {
            background: linear-gradient(135deg, #1e293b, #0f172a);
            border: 2px solid #ffd700;
            padding: 8px 15px;
            border-radius: 12px;
            margin: 10px auto;
            width: 85%;
            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        .result-label {
            font-size: 12px;
            color: #94a3b8;
            font-weight: bold;
        }
        .result-value {
            font-size: 18px;
            font-weight: 900;
            color: #ffd700;
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.8);
        }
        
        .wheel-container {
            position: relative;
            width: 300px;
            height: 300px;
            margin: 15px auto;
            background: conic-gradient(
                #ff007f 0deg 45deg,
                #ef4444 45deg 90deg,
                #22c55e 90deg 135deg,
                #3b82f6 135deg 180deg,
                #f59e0b 180deg 225deg,
                #a855f7 225deg 270deg,
                #06b6d4 270deg 315deg,
                #ec4899 315deg 360deg
            );
            border: 10px solid #ffd700;
            border-radius: 50%;
            box-shadow: 0 0 30px rgba(251, 191, 36, 0.8), inset 0 0 20px rgba(0,0,0,0.8);
            overflow: hidden;
            transition: transform 6s cubic-bezier(0.15, 0.8, 0.15, 1);
        }

        .wheel-center-pin {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 24px;
            height: 24px;
            background: #0f172a;
            border-radius: 50%;
            z-index: 28;
            box-shadow: 0 0 10px rgba(0,0,0,0.9);
            border: 3px solid #ffd700;
        }

        .wheel-item {
            position: absolute;
            width: 28px;
            height: 28px;
            font-size: 12px;
            font-weight: 900;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            z-index: 15;
            background: #ffffff;
            color: #1e293b;
            border: 2px solid #ffd700;
            box-shadow: 0 2px 6px rgba(0,0,0,0.8);
            transform: translate(-50%, -50%);
        }

        .wheel-lucy {
            position: absolute;
            width: 32px;
            height: 32px;
            font-size: 13px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            z-index: 15;
            background: #ffffff;
            color: #ff007f;
            border: 2px solid #ffd700;
            box-shadow: 0 0 15px #ff007f;
            transform: translate(-50%, -50%);
        }

        .input-group {
            margin: 10px 0;
            text-align: left;
        }
        label {
            font-size: 12px;
            display: block;
            margin-bottom: 5px;
            color: #e2e8f0;
            font-weight: bold;
        }

        .selection-table {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 5px;
            background: rgba(15, 23, 42, 0.6);
            padding: 8px;
            border-radius: 10px;
            border: 1px solid #334155;
            margin-bottom: 8px;
        }
        .cell-btn {
            background: #1e293b;
            color: #fff;
            border: 1px solid #475569;
            padding: 8px 4px;
            text-align: center;
            font-size: 12px;
            font-weight: bold;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .cell-btn:hover { background: #334155; }
        .cell-btn.selected {
            background: #22c55e;
            color: #ffffff;
            border-color: #4ade80;
            box-shadow: 0 0 10px rgba(34, 197, 94, 0.6);
        }
        .cell-btn.lucy-cell {
            background: linear-gradient(135deg, #ff007f, #7f00ff);
            color: #ffffff;
            border: 1px solid #ffffff;
            grid-column: span 4;
        }

        input, select {
            width: 100%;
            padding: 8px;
            border-radius: 6px;
            border: 1px solid #475569;
            background: #0f172a;
            color: #fff;
            font-size: 13px;
            box-sizing: border-box;
            margin-bottom: 5px;
        }
        .message-box {
            margin: 8px 0;
            font-size: 13px;
            font-weight: bold;
            min-height: 20px;
        }
        button {
            background: linear-gradient(135deg, #22c55e, #16a34a);
            color: #ffffff;
            border: none;
            padding: 10px;
            font-size: 14px;
            border-radius: 8px;
            cursor: pointer;
            width: 100%;
            margin-top: 5px;
            font-weight: bold;
            box-shadow: 0 4px 10px rgba(34, 197, 94, 0.4);
        }
        button:disabled { background: #475569; cursor: not-allowed; }

        .card {
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(34, 197, 94, 0.4);
            padding: 10px;
            border-radius: 10px;
            margin-top: 12px;
            text-align: left;
        }
        .card-title {
            color: #22c55e;
            font-weight: bold;
            font-size: 13px;
            margin-bottom: 6px;
        }
        .bonus-banner {
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: #0f172a;
            padding: 8px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 12px;
            margin-bottom: 10px;
            text-align: center;
        }
        .copy-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #0f172a;
            padding: 6px 8px;
            border-radius: 6px;
            margin-bottom: 6px;
            font-size: 13px;
            border: 1px solid #334155;
        }
        .copy-btn {
            background: #3b82f6;
            color: #fff;
            border: none;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            width: auto;
            margin: 0;
        }
    </style>
</head>
<body>

    <div class="container">
        <h1>🎰 ቴሌብር የፊደል ስፒን ጨዋታ</h1>
        <div class="subtitle">ፊደላት (A-G) እና ሉሲ ቦነስ ጨዋታ</div>

        <div class="balance-box">
            ቀሪ ሂሳብ: <span id="balance">100</span> ብር
        </div>

        <div class="result-display-banner">
            <span class="result-label">የወጣው ውጤት:</span>
            <span id="spinDisplay" class="result-value">A</span>
        </div>

        <div style="position: relative; width: 300px; margin: 0 auto;">
            <div class="wheel-container" id="wheelContainer">
                <div class="wheel-center-pin"></div>
            </div>
            <button id="spinBtn" onclick="playSpin()">🎲 አጫውት (SPIN)</button>
        </div>

        <div class="input-group" style="margin-top: 15px;">
            <label>ፊደላትን (A-G) ወይም ሉሲን ይምረጡ:</label>
            <div class="selection-table" id="selectionTable"></div>

            <label for="betAmount">የውርርድ መጠን ለእያንዳንዱ ምርጫ (ብር):</label>
            <input type="number" id="betAmount" value="30" min="30">
        </div>

        <div class="message-box" id="infoMessage">ምርጫዎችዎን መርጠው 'አጫውት' ይጫኑ</div>

        <!-- ዴፖዚት ካርድ -->
        <div class="card">
            <div class="bonus-banner">🎁 ለመጀመሪያ ዴፖዚት (100 ብር ሲያስገቡ) እስከ 200% ቦነስ!</div>
            <div class="card-title">📥 ገንዘብ ማስገቢያ (Deposit)</div>
            <label>በዚህ ቴሌብር ቁጥር ይላኩ:</label>
            <div class="copy-row">
                <span id="telNumber">0920538962</span>
                <button class="copy-btn" onclick="copyTelebirr()">📋 ኮፒ</button>
            </div>
            
            <label>የላኩበት Transaction ID:</label>
            <input type="text" id="depTxId" placeholder="ለአብነት: TX12345678">
            
            <label>የእርስዎ ቴሌብር ስልክ ቁጥር:</label>
            <input type="tel" id="depPhone" placeholder="09........">

            <label>የቦነስ ምርጫ:</label>
            <select id="bonusChoice">
                <option value="100">100 ብር + 100% ቦነስ (አጠቃላይ 200 ብር)</option>
                <option value="200" selected>100 ብር + 200% ቦነስ (አጠቃላይ 300 ብር)</option>
            </select>

            <button style="background: linear-gradient(135deg, #22c55e, #16a34a);" onclick="submitDeposit()">ገንዘብ አስገባሁ (Submit Deposit)</button>
        </div>

        <!-- ዊዝድሮዋል ካርድ -->
        <div class="card" style="border-color: rgba(239, 68, 68, 0.4);">
            <div class="card-title" style="color: #ef4444;">📤 ገንዘብ ማውጫ (Withdraw)</div>
            
            <label>ማውጣት የሚፈልጉት መጠን (ብር):</label>
            <input type="number" id="wdAmount" placeholder="ከ 500 ብር ጀምሮ">

            <label>የሚቀበሉበት ቴሌብር ስልክ ቁጥር:</label>
            <input type="tel" id="wdPhone" placeholder="09........">

            <button style="background: linear-gradient(135deg, #ef4444, #dc2626);" onclick="submitWithdraw()">ወጪ ጠይቅ (Request Withdraw)</button>
        </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();

        let balance = 100; // መነሻ 100 ብር

        const letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G'];
        let wheelItems = ["Lucy", ...letters];
        let selectedChoices = ["A"];

        let tableContainer = document.getElementById("selectionTable");
        let allSelectableItems = [...letters, "Lucy"];

        allSelectableItems.forEach(item => {
            let btn = document.createElement("div");
            btn.className = item === "Lucy" ? "cell-btn lucy-cell" : "cell-btn";
            if(item === "A") btn.classList.add("selected");
            btn.innerText = item === "Lucy" ? "🌟 ሉሲ (Gold - x5)" : item;
            
            btn.onclick = function() {
                if (selectedChoices.includes(item)) {
                    if (selectedChoices.length > 1) {
                        selectedChoices = selectedChoices.filter(c => c !== item);
                        btn.classList.remove('selected');
                    }
                } else {
                    selectedChoices.push(item);
                    btn.classList.add('selected');
                }
            };
            tableContainer.appendChild(btn);
        });

        let wheelContainer = document.getElementById("wheelContainer");
        let centerX = 150;
        let centerY = 150;
        let radius = 85; 
        let totalItems = wheelItems.length;
        let sliceAngle = 360 / totalItems;

        wheelItems.forEach((item, index) => {
            let angle = (index * sliceAngle + sliceAngle / 2) * (Math.PI / 180) - Math.PI / 2;
            let x = centerX + radius * Math.cos(angle);
            let y = centerY + radius * Math.sin(angle);

            let div = document.createElement("div");
            div.style.left = x + "px";
            div.style.top = y + "px";

            if (item === "Lucy") {
                div.className = "wheel-lucy";
                div.innerText = "🌟";
            } else {
                div.className = "wheel-item";
                div.innerText = item;
            }
            wheelContainer.appendChild(div);
        });

        let currentRotation = 0;

        function playSpin() {
            let balanceBox = document.getElementById("balance");
            let infoBox = document.getElementById("infoMessage");
            let spinDisplay = document.getElementById("spinDisplay");
            let spinBtn = document.getElementById("spinBtn");
            let betAmountPerChoice = parseFloat(document.getElementById("betAmount").value);

            if (selectedChoices.length === 0) {
                infoBox.innerText = "እባክዎን ቢያንስ አንድ ምርጫ ይምረጡ!";
                return;
            }

            let totalBet = betAmountPerChoice * selectedChoices.length;

            if (balance < totalBet) {
                infoBox.innerText = `ሂሳብዎ በቂ አይደለም! (አጠቃላይ ውርርድ: ${totalBet} ብር)`;
                return;
            }

            spinBtn.disabled = true;
            infoBox.innerText = "ስፒን በመሽከርከር ላይ ነው...";

            balance -= totalBet;
            balanceBox.innerText = balance;

            let winningIndex = Math.floor(Math.random() * totalItems);
            let winningItem = wheelItems[winningIndex];

            let extraRotations = 360 * 6; 
            let targetRotation = currentRotation + extraRotations + (360 - (winningIndex * sliceAngle));
            
            currentRotation = targetRotation;
            wheelContainer.style.transform = `rotate(${currentRotation}deg)`;

            let tempInterval = setInterval(() => {
                let tempItem = wheelItems[Math.floor(Math.random() * totalItems)];
                spinDisplay.innerText = tempItem === "Lucy" ? "🌟 ሉሲ" : tempItem;
            }, 100);

            setTimeout(() => {
                clearInterval(tempInterval);
                let finalDisplay = winningItem === "Lucy" ? "🌟 ሉሲ" : winningItem;
                spinDisplay.innerText = finalDisplay;
                spinBtn.disabled = false;

                if (selectedChoices.includes(winningItem)) {
                    let odd = winningItem === "Lucy" ? 5.0 : 2.5;
                    let winPayout = Math.floor(betAmountPerChoice * odd);
                    balance += winPayout;
                    infoBox.innerText = `🎉 አሸነፍክ! +${winPayout} ብር አግኝተሃል!`;
                } else {
                    infoBox.innerText = `😢 አልተሳካም! -${totalBet} ብር ተቀንሷል።`;
                }

                balanceBox.innerText = balance;
            }, 6000);
        }

        function copyTelebirr() {
            let telText = document.getElementById("telNumber").innerText;
            navigator.clipboard.writeText(telText).then(() => {
                alert("የቴሌብር ቁጥር ተኮርጅዟል: " + telText);
            });
        }

        function submitDeposit() {
            let txId = document.getElementById("depTxId").value.trim();
            let phone = document.getElementById("depPhone").value.trim();
            let bonusVal = document.getElementById("bonusChoice").value;

            if (!txId || !phone) {
                alert("እባክዎን የ Transaction ID እና የስልክ ቁጥር ያስገቡ!");
                return;
            }

            let user = tg.initDataUnsafe && tg.initDataUnsafe.user ? tg.initDataUnsafe.user : { id: 12345, first_name: "Guest", username: "unknown" };
            
            fetch('/api/deposit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: user.id, user_name: user.first_name, username: user.username || "none", phone: phone, tx_id: txId, bonus: bonusVal })
            })
            .then(res => res.json())
            .then(data => {
                if(data.success) alert("የዲፖዚት ጥያቄዎ ለአድሚን ተልኳል!");
            });
        }

        function submitWithdraw() {
            let amount = parseFloat(document.getElementById("wdAmount").value);
            let phone = document.getElementById("wdPhone").value.trim();

            if (!amount || amount < 500 || amount > balance) {
                alert("ልክ ያልሆነ መጠን ወይም በቂ ሂሳብ የለዎትም (Min: 500 ETB)!");
                return;
            }

            balance -= amount;
            document.getElementById("balance").innerText = balance;

            let user = tg.initDataUnsafe && tg.initDataUnsafe.user ? tg.initDataUnsafe.user : { id: 12345, first_name: "Guest", username: "none" };

            fetch('/api/withdraw', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: user.id, user_name: user.first_name, username: user.username || "none", phone: phone, amount: amount })
            })
            .then(res => res.json())
            .then(data => {
                if(data.success) alert("የገንዘብ ማውጫ ጥያቄዎ ተልኳል!");
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
        msg = (
            f"🎁 **አዲስ የዲፖዚት እና ቦነስ ጥያቄ**\n\n"
            f"👤 ስም: {data.get('user_name')} (@{data.get('username')})\n"
            f"🆔 ID: `{data.get('user_id')}`\n"
            f"📱 ስልክ: `{data.get('phone')}`\n"
            f"💳 Trans ID: `{data.get('tx_id')}`\n"
            f"💰 የተጠየቀው ቦነስ: {data.get('bonus')} ብር"
        )
        keyboard = {
            "inline_keyboard": [
                [{"text": f"✅ ዲፖዚት አረጋግጥ (Approve)", "callback_data": f"approve_dep_{data.get('user_id')}_{data.get('bonus')}"}]
            ]
        }
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": ADMIN_CHAT_ID, "text": msg, "parse_mode": "Markdown", "reply_markup": keyboard}
        )
    return jsonify({"success": True})

@app.route('/api/withdraw', methods=['POST'])
def withdraw():
    data = request.json
    if BOT_TOKEN and ADMIN_CHAT_ID:
        msg = (
            f"📤 **አዲስ የገንዘብ ማውጫ (Withdraw) ጥያቄ**\n\n"
            f"👤 ስም: {data.get('user_name')} (@{data.get('username')})\n"
            f"🆔 ID: `{data.get('user_id')}`\n"
            f"📱 ስልክ: `{data.get('phone')}`\n"
            f"💰 የሚወጣው መጠን: **{data.get('amount')} ብር**"
        )
        keyboard = {
            "inline_keyboard": [
                [{"text": f"✅ {data.get('amount')} ብር ዊድድሮ አረጋግጥ", "callback_data": f"approve_with_{data.get('user_id')}_{data.get('amount')}"}]
            ]
        }
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": ADMIN_CHAT_ID, "text": msg, "parse_mode": "Markdown", "reply_markup": keyboard}
        )
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
