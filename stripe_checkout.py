# stripe_checkout.py
# ------------------
import os
import stripe
import streamlit as st

# ====== Nastavení klíčů z ENV ======
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "").strip()
STRIPE_PRICE_ID   = os.getenv("STRIPE_PRICE_ID", "").strip()
PUBLIC_URL        = os.getenv("PUBLIC_URL", "").strip()  # např. https://fotbal-predikce-3.onrender.com

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

def _require_stripe_ready() -> bool:
    if not STRIPE_SECRET_KEY or not STRIPE_PRICE_ID:
        st.error("Stripe není nakonfigurován. Na Renderu nastav **STRIPE_SECRET_KEY** a **STRIPE_PRICE_ID** v Environment Variables.")
        return False
    return True

def has_active_subscription(email: str) -> bool:
    """Zkontroluje aktivní/trial předplatné podle e-mailu (sandbox i live)."""
    if not _require_stripe_ready() or not email:
        return False
    try:
        customers = stripe.Customer.list(email=email, limit=3).data
        for cust in customers:
            subs = stripe.Subscription.list(customer=cust.id, status="all", limit=5).data
            for s in subs:
                if s.status in ("active", "trialing"):
                    return True
        return False
    except stripe.error.AuthenticationError:
        st.error("Chybný Stripe API key (použij **test** klíč sk_test_... v Sandboxu).")
        return False
    except Exception as e:
        st.warning(f"Stripe kontrola selhala: {e}")
        return False

def paywall_ui(render_protected):
    """Jednoduchý paywall: pokud není aktivní předplatné, nabídne Checkout."""
    st.markdown("### 🔒 Předplatné")
    st.caption("Pro plný přístup je potřeba aktivní předplatné (399 Kč / měsíc).")

    # e-mail – použijeme ho pro přiřazení předplatného
    email = st.text_input("Váš e-mail", placeholder="např. jan.novak@email.cz")

    # když se vrátíme ze Stripe Checkout (success=1), zobraz obsah
    qp = st.query_params
    just_success = qp.get("success", ["0"])[0] == "1"

    subscribed = has_active_subscription(email) if email else False
    if subscribed:
        st.success("✅ Máte aktivní předplatné. Děkujeme!")
        render_protected()
        return

    if just_success and email:
        # po návratu ze Stripe chvilku trvá, než Stripe oznámí subskripci → zkusíme najít
        if has_active_subscription(email):
            st.success("✅ Platba potvrzena. Předplatné je aktivní.")
            render_protected()
            return
        st.info("Platba proběhla, aktivace může trvat pár sekund. Zkuste to za chvíli znovu.")

    st.warning("Nemáte aktivní předplatné.")

    # tlačítko do Stripe Checkout
    if st.button("💳 Přejít na platbu (Stripe)"):
        if not _require_stripe_ready():
            st.stop()
        if not email:
            st.error("Zadejte prosím e-mail.")
            st.stop()

        success_url = (PUBLIC_URL or "https://example.com") + "?success=1"
        cancel_url  = (PUBLIC_URL or "https://example.com") + "?canceled=1"

        try:
            session = stripe.checkout.Session.create(
                mode="subscription",
                payment_method_types=["card"],
                line_items=[{"price": STRIPE_PRICE_ID, "quantity": 1}],
                customer_email=email,
                success_url=success_url,
                cancel_url=cancel_url,
                allow_promotion_codes=True,
            )
            st.link_button("🔗 Otevřít Stripe Checkout", session.url, use_container_width=True, type="primary")
            st.caption("Pokud se odkaz neotevře automaticky, klepněte na tlačítko výše.")
        except Exception as e:
            st.error(f"Vytvoření Checkout session selhalo: {e}")
