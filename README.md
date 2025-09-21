# ⚽ Fotbalové predikce s předplatným

Tato aplikace je postavena na **Streamlit** a umožňuje předplatné přes **Stripe**.

## Obsah projektu
- `fotbal_app_multi.py` – hlavní Streamlit aplikace
- `stripe_checkout.py` – platební logika (Stripe)
- `teams.json` – ukázková data týmů
- `requirements.txt` – seznam Python balíčků

## Nasazení na Render
1. Nahraj tuto složku do **GitHub** repozitáře.
2. Na [render.com](https://render.com/) vytvoř **Web Service**:
   - Start Command:
     ```
     streamlit run fotbal_app_multi.py --server.port 10000 --server.enableCORS false
     ```
3. V **Environment Variables** nastav:
   - `STRIPE_SECRET_KEY` = tvůj Stripe **sk_test_...** klíč
   - `STRIPE_PRICE_ID` = ID ceny (price_...) z tvého Stripe produktu
   - `PUBLIC_BASE_URL` = veřejná adresa aplikace (např. https://moje-app.onrender.com)

4. Klikni **Deploy**. Hotovo ✅

## Lokální spuštění
pip install -r requirements.txt
streamlit run fotbal_app_multi.py

less
Zkopírovat kód

Aplikace běží na `http://localhost:8501`
