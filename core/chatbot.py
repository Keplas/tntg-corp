import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import urllib.request
import urllib.error
import os

SYSTEM_PROMPT = """You are TARA (T&TG Automated Response Assistant), the official AI assistant for T&TG Trade Corporation — a Trade & e-Commerce corporation founded by Tom Ssembiito, headquartered in Toronto, Canada.

COMPANY INFO:
- Full name: Tom & The Group Trade Corporation (T&TG Trade Corp)
- Headquarters: 9 Summerbridge Road, Scarborough, M1G 1L8, Toronto, Ontario, Canada
- Phone: +1 (416) 832 3512
- Email: tom.grouptrade@gmail.com
- Founded: October 14, 2026
- Operates in: Canada 🇨🇦, Uganda 🇺🇬 and Kenya 🇰🇪
- Import & Export (RM) registered corporation
- Founder: Tom Ssembiito

ABOUT US:
Founded on October 14 2026, T&TG Trade Corporation operates a Trade & e-Commerce platform designed to facilitate seamless domestic and international commerce. Our Toronto-based corporation operates globally, providing services across Canada, Uganda and Kenya. From our headquarters in Toronto, Ontario, Canada, we coordinate international operations that support cross-border collaboration, market development and service delivery.

SERVICES:
[A] T&TG Shopping Platform — Premium coffee marketplace. T&TG Arabica Green Coffee ($35/kg) and T&TG Robusta Green Coffee ($28/kg), sourced from Uganda. Available to Canadians and Global Clients.
[B] T&TG Trade Loyalty Platform — Earn loyalty points on every purchase and refer friends to earn more.
[C] Live Exchange Rates — CAD/UGX, CAD/KES, UGX/KES — the currencies of our trade routes.
[D] Training Programs — Trade, farming and enterprise programs with certificates.
[E] TV Programs — Trade, farming and commerce content.

MARKETPLACE (Online Shopping Platform):
- Local Market: open to individuals and companies in Canada, Uganda or Kenya
- International Market: requires registered company + T&TG Certificate of completion
- Product Categories: Clothing (Suits, Shirts, T-Shirts, Trousers), Shoes, Hand Watches, Coffee (Robusta Green Coffee, Arabica Green Coffee)
- Target audiences: Men, Women
- Order types: Express (fast, higher cost) or Ordinary (standard, lower cost)
- Buyers earn T&TG Loyalty Points on every purchase

T&TG TRADE LOYALTY PLATFORM:
(A) Points — Earn T&TG Loyalty Points on every purchase
    - Consumer/end-user rate: 1% of purchase price
    - Referral rate: 2.5% of purchase price (when you refer a buyer)
    - Rates are calculated on net price after expenses and taxes
(B) Promotions — Seasonal and partner promotions (coming soon)
(C) Referral — Refer friends and earn 2.5% loyalty points on their purchases
(D) Reward / Withdrawal — Withdraw your loyalty points as funds
    - Payment is processed on the 45th day after the purchase date
    - Minimum points required to withdraw apply

LIVE EXCHANGE RATES (Trade Routes):
- CAD/UGX — Canadian Dollar to Ugandan Shilling
- CAD/KES — Canadian Dollar to Kenyan Shilling
- UGX/KES — Ugandan Shilling to Kenyan Shilling
Visit /services/forex/ for live rates.

REGISTRATION STEPS:
1. Choose Local or International market
2. Select country of residence (Canada, Uganda or Kenya)
3. Upload National ID (front & back) + selfie for KYC
4. Sign and upload declaration
5. Create profile with business description

INTERNATIONAL MARKET ELIGIBILITY:
- Must be a registered company
- Must partner with T&TG Trade Corp
- Must hold a T&TG Certificate of Completion ($500–$5,000 fee)

TRAINING PROGRAMS (free enrollment, paid certificate):
- Modern & Tech Farming (12.5h, cert $500)
- Trade & E-Commerce Business Setup (6h, cert $500)
- Import & Export Operations (8h, cert $500)
Certificate benefits: Priority employment, international market access, partnership opportunities.

TV PROGRAMS: T&TG Global Trade Report (Mon), Farming Tech Weekly (Wed), Coffee & Trade (Sat), T&TG Partner Spotlight (monthly).

USER ACCOUNTS:
- Admin: username=admin, password=admin123
- All other users: password=pass1234
- User IDs follow format: TG00001, TG00002, etc.

PAGES ON WEBSITE:
- Home: /
- Marketplace: /marketplace/
- Products: /marketplace/products/
- All Coffee: /marketplace/products/?category=coffee
- Arabica Green Coffee: /marketplace/products/?category=coffee&name=arabica
- Robusta Green Coffee: /marketplace/products/?category=coffee&name=robusta
- Artisanal Coffee Goods: /marketplace/products/?category=coffee&name=artisanal
- Forex / Exchange Rates: /services/forex/
- Trade & E-Commerce: /services/
- T&TG Loyalty Platform: /loyalty/
- My Loyalty Dashboard: /accounts/loyalty/
- Training: /training/
- TV Programs: /training/tv/
- About: /about/
- Contact: /contact/
- Register: /accounts/register/
- Login: /accounts/login/
- Dashboard: /accounts/dashboard/

Be helpful, professional and friendly. Keep answers concise but complete. Use emojis sparingly. If asked something outside T&TG scope, politely redirect. Never make up information not listed above."""


@csrf_exempt
@require_POST
def chatbot_api(request):
    try:
        data     = json.loads(request.body)
        messages = data.get('messages', [])
        if not messages:
            return JsonResponse({'error': 'No messages provided'}, status=400)

        messages = messages[-20:]

        payload = json.dumps({
            "model":      "claude-haiku-4-5-20251001",
            "max_tokens": 600,
            "system":     SYSTEM_PROMPT,
            "messages":   messages,
        }).encode('utf-8')

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type":      "application/json",
                "anthropic-version": "2023-06-01",
            },
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            reply  = result.get('content', [{}])[0].get('text', 'Sorry, I could not generate a response.')
            return JsonResponse({'reply': reply})

    except urllib.error.HTTPError as e:
        if e.code == 401:
            return JsonResponse({'reply': get_offline_reply(data.get('messages', []))})
        return JsonResponse({'reply': 'I am having trouble connecting right now. Please call us at +1 (416) 832 3512.'})
    except Exception:
        return JsonResponse({'reply': get_offline_reply(data.get('messages', []))})


def get_offline_reply(messages):
    if not messages:
        return "Hello! I'm TARA, T&TG's assistant. How can I help you today?"
    last = messages[-1].get('content', '').lower()
    if any(w in last for w in ['point', 'loyalty', 'earn', 'reward']):
        return ("💰 **T&TG Trade Loyalty Platform** — Earn 1% of your purchase as T&TG Loyalty Points "
                "(or 2.5% when you're referred by someone). "
                "Withdraw your funds on Day 45 after purchase. Visit **/loyalty/** for details.")
    if any(w in last for w in ['referral', 'refer', 'friend']):
        return ("🤝 **Referral Programme** — When you refer a buyer, you earn 2.5% of their purchase "
                "as T&TG Loyalty Points. Share your referral code and start earning. Visit **/loyalty/**.")
    if any(w in last for w in ['withdraw', 'cash', 'payment', 'fund']):
        return ("💸 **Withdraw Your Funds** — Submit a withdrawal request from your Loyalty Dashboard. "
                "Payments are processed on Day 45 after the qualifying purchase. Visit **/accounts/loyalty/**.")
    if any(w in last for w in ['register', 'sign up', 'join', 'account']):
        return ("👤 To register, visit **/accounts/register/**. You'll need: National ID (front & back), "
                "a selfie, and a signed declaration. Choose Local or International market.")
    if any(w in last for w in ['coffee', 'robusta', 'arabica']):
        return ("☕ We sell **Robusta Green Coffee** and **Arabica Green Coffee** on our marketplace. "
                "Browse at **/marketplace/products/?category=coffee**.")
    if any(w in last for w in ['cloth', 'suit', 'shirt', 'trouser', 'shoe', 'watch', 'textile']):
        return ("👔 Our marketplace carries Suits, Shirts, T-Shirts, Trousers, Shoes and Hand Watches "
                "for men and women. Browse at **/marketplace/products/**.")
    if any(w in last for w in ['forex', 'exchange', 'currency', 'rate', 'cad', 'ugx', 'kes']):
        return ("💱 **Live Exchange Rates** — We track CAD/UGX, CAD/KES and UGX/KES — the currencies "
                "of our trade routes across Canada, Uganda and Kenya. Visit **/services/forex/**.")
    if any(w in last for w in ['train', 'course', 'certificate', 'learn']):
        return ("🎓 Training Programs in Farming, Trade & E-Commerce, and Import/Export. "
                "Enrollment is free — certificates cost from $500. Visit **/training/**.")
    if any(w in last for w in ['market', 'buy', 'sell', 'product', 'order', 'shop']):
        return ("🛒 Our marketplace has Local and International markets. "
                "Browse T&TG Arabica and Robusta green coffee at **/marketplace/**. "
                "Choose Express ⚡ or Ordinary 🚢 delivery. Earn T&TG Loyalty Points on every order.")
    if any(w in last for w in ['contact', 'phone', 'email', 'address']):
        return ("📞 **T&TG Trade Corp** — +1 (416) 832 3512 | tom.grouptrade@gmail.com | "
                "9 Summerbridge Road, Scarborough, M1G 1L8, Toronto, ON, Canada. "
                "Or visit **/contact/**.")
    if any(w in last for w in ['hello', 'hi', 'hey', 'help', 'start']):
        return ("👋 Hello! I'm **TARA**, T&TG's AI assistant. I can help you with:\n"
                "• 🛒 Marketplace & Orders\n"
                "• 💰 T&TG Loyalty Platform\n"
                "• 💱 Live Exchange Rates (CAD/UGX, CAD/KES, UGX/KES)\n"
                "• 🎓 Training Programs\n"
                "• 🇨🇦 🇺🇬 🇰🇪 Canada · Uganda · Kenya\n\n"
                "What would you like to know?")
    return ("I'm here to help with T&TG Trade Corp services. Ask me about our marketplace, "
            "T&TG Loyalty Platform, forex rates, training programs, or how to register.")
