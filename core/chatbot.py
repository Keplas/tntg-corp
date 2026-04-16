import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import urllib.request
import urllib.error
import os

SYSTEM_PROMPT = """You are TARA (T&TG Automated Response Assistant), the official AI assistant for T&TG Trade Corporation — a global financial services and e-commerce company founded by Tom Ssembiito, headquartered in Toronto, Canada.

You help users with:

COMPANY INFO:
- Full name: Tom & The Group Trade Corporation (T&TG Trade Corp)
- Headquarters: M1G 1L8, Toronto, ON, Canada
- Phone: +1 (416) 832 3512
- Email: tom.grouptradecorp.ca
- Founded: October 14, 2026
- Operates in: Canada, Uganda, Netherlands, USA, Kenya and Japan
- Founder: Tom Ssembiito | Software Engineer: Edgar Kitayimbwa | Shareholder: Musana Francis

SERVICES:
[A] Insurance — Health, Trade, Cargo, Business, Life insurance. Pay premiums with Avon Points.
[B] Online Shopping Platform — Local & International marketplace for buying/selling goods.
[C] T&TG Brokerage — Forex, Stocks, Commodities and Crypto trading.
Also: Forex Exchange bureau, Coffee Roasting Company (organic Arabica), Training Programs, TV Programs.

MARKETPLACE:
- Local Market: open to individuals and companies in any of the 6 countries
- International Market: requires registered company status + T&TG Certificate of completion
- Products: Electronics (Apple, Dell, HP, Canon), Coffee (green & roasted Arabica), Pharmaceuticals, Agriculture, Textiles, Machinery
- Order types: Express (fast, higher cost) or Ordinary (standard, lower cost)
- Users earn Avon Points on every purchase

AVON POINTS LOYALTY PROGRAM:
- Earn 5.5% of purchase price as a consumer/end user
- Earn 8.5% of purchase price if you referred the buyer
- Formula (consumer): Price × Quantity ÷ 5.5 = Avon Points
- Formula (referral): Price × Quantity ÷ 8.5 = Avon Points
- Sell orders: minimum 3-month lock period, placed by quarter (Q1/Q2/Q3/Q4)
- Redeem for: insurance premiums, bill payments, real estate investment, currency conversion, withdrawal
- 1 Avon Point ≈ $1 USD

REGISTRATION STEPS:
1. Choose Local or International market
2. Select country of residence
3. Upload National ID (front & back) + selfie for KYC
4. Sign and upload declaration
5. Create profile with business description

INTERNATIONAL MARKET ELIGIBILITY:
- Must be a registered company
- Must partner with T&TG
- Must hold a T&TG Certificate of Completion ($500–$5,000 fee)

TRAINING PROGRAMS (free enrollment, paid certificate):
- Modern & Tech Farming (12.5h, cert $500)
- Advanced Coffee Cultivation & Roasting (8h, cert $500)
- Aquaponics & Greenhouse Systems (10h, cert $500)
- Corporate Mid-Market Enterprise Strategy (20h, cert $2,000)
- Import & Export Operations (8h, cert $500)
- E-Commerce Business Setup & Management (6h, cert $500)
- Financial Services & Investment Essentials (15h, cert $1,500)
- Forex Trading & Currency Management (12h, cert $1,500)
- Insurance & Risk Management (6h, cert $500)
- Investment Portfolio & Real Estate (10h, cert $2,000)
Certificate benefits: Priority employment, international market access, share eligibility, partnership opportunities.

COFFEE PROJECTIONS (Arabica $35–$55/kg):
- Level 1: 25kg/week → $10,500–$16,500/year
- Level 2: 50kg/week → $21,000–$33,000/year
- Level 3: 75kg/week → $31,500–$49,500/year
- Level 4: 100kg/week → $168,000–$264,000/year

TV PROGRAMS: T&TG Global Trade Report (Mon), Farming Tech Weekly (Wed), Investment Masterclass Live (Fri), Coffee Culture & Trade (Sat), T&TG Partner Spotlight (monthly), Forex & Currency Live (weekdays 7am UTC).

USER ACCOUNTS (demo):
- Admin: username=admin, password=admin123
- All other users: password=pass1234
- User IDs follow format: TG00001, TG00002, etc.

PAGES ON WEBSITE:
- Home: / 
- Marketplace: /marketplace/
- Products: /marketplace/products/
- Financial Services: /services/
- Insurance: /services/insurance/
- Brokerage: /services/brokerage/
- Forex: /services/forex/
- Coffee: /coffee/
- Training: /training/
- TV Programs: /training/tv/
- Avon Points: /avon-points/
- About: /about/
- Contact: /contact/
- Register: /accounts/register/
- Login: /accounts/login/
- Dashboard: /accounts/dashboard/

Be helpful, professional, and friendly. Keep answers concise but complete. Use emojis sparingly for warmth. If asked something outside T&TG scope, politely redirect to what you can help with. Never make up information not listed above."""


@csrf_exempt
@require_POST
def chatbot_api(request):
    try:
        data = json.loads(request.body)
        messages = data.get('messages', [])
        if not messages:
            return JsonResponse({'error': 'No messages provided'}, status=400)

        # Cap history to last 20 messages to control context
        messages = messages[-20:]

        payload = json.dumps({
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 600,
            "system": SYSTEM_PROMPT,
            "messages": messages,
        }).encode('utf-8')

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            },
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            reply = result.get('content', [{}])[0].get('text', 'Sorry, I could not generate a response.')
            return JsonResponse({'reply': reply})

    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore')
        # If no API key, return a helpful offline response
        if e.code == 401:
            return JsonResponse({'reply': get_offline_reply(data.get('messages', []))})
        return JsonResponse({'reply': 'I am having trouble connecting right now. Please try again shortly or contact us at tom.grouptradecorp.ca.'})
    except Exception as e:
        return JsonResponse({'reply': get_offline_reply(data.get('messages', []))})


def get_offline_reply(messages):
    """Rule-based fallback when API is unavailable."""
    if not messages:
        return "Hello! I'm TARA, T&TG's assistant. How can I help you today?"
    last = messages[-1].get('content', '').lower()
    if any(w in last for w in ['avon', 'point', 'earn', 'loyalty']):
        return "💰 **Avon Points** — Earn 5.5% as a consumer or 8.5% via referral on every purchase. Redeem for insurance, bills, real estate or cash withdrawal. Sell orders have a 3-month minimum lock period (Q1–Q4)."
    if any(w in last for w in ['register', 'sign up', 'join', 'account']):
        return "👤 To register, go to **/accounts/register/**. You'll need: National ID (front & back), a selfie, and a signed declaration. Choose Local or International market and fill in your business description."
    if any(w in last for w in ['insurance']):
        return "🛡️ We offer Health, Trade, Cargo, Business and Life insurance. You can pay premiums using Avon Points. Visit **/services/insurance/** or contact us at +1 (416) 832 3512."
    if any(w in last for w in ['coffee']):
        return "☕ T&TG manages a premium organic Arabica coffee roasting company. Green beans and roasted coffee available on the marketplace. Projections range from $10,500 to $264,000/year depending on volume. Visit **/coffee/**."
    if any(w in last for w in ['train', 'course', 'certificate', 'learn']):
        return "🎓 We offer 10 training programs in Farming, Enterprise and Financial Services. Enrollment is free — certificates cost $500–$2,000. Certified users get priority employment and international market access. Visit **/training/**."
    if any(w in last for w in ['forex', 'exchange', 'currency', 'rate']):
        return "💱 T&TG operates a Forex Bureau supporting USD, CAD, UGX, EUR, GBP, KES and JPY. Visit **/services/forex/** for live rates and our currency converter."
    if any(w in last for w in ['market', 'buy', 'sell', 'product', 'order']):
        return "🛒 Our marketplace has Local and International markets. Browse products at **/marketplace/**. Choose Express (⚡ faster) or Ordinary (🚢 cheaper) delivery. You earn Avon Points on every order."
    if any(w in last for w in ['contact', 'phone', 'email', 'address']):
        return "📞 **T&TG Trade Corp** — +1 (416) 832 3512 | tom.grouptradecorp.ca | M1G 1L8, Toronto, ON, Canada. Or visit **/contact/** to send a message."
    if any(w in last for w in ['hello', 'hi', 'hey', 'help', 'start']):
        return "👋 Hello! I'm **TARA**, T&TG's AI assistant. I can help you with:\n• 🛒 Marketplace & Orders\n• 💰 Avon Points\n• 🛡️ Insurance & Services\n• 📈 Brokerage & Forex\n• ☕ Coffee Company\n• 🎓 Training Programs\n\nWhat would you like to know?"
    return "I'm here to help with T&TG Trade Corp services. You can ask me about our marketplace, Avon Points, insurance, forex, training programs, or how to register. What would you like to know?"
