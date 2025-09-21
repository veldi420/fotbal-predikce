import os
import streamlit as st
import stripe

# Stripe konfigurace z Environment variables
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
PRICE_ID = os.getenv("STRIPE_PRICE_ID", "")

if not STRIPE_SECRET_KEY:
    st.error("❌ Chybí STRIPE_SECRET_KEY v nastavení Renderu.")
    st.stop()

stripe.api_key = STRIPE_SECRET_KEY

def has_active_subscription(email: str) -> bool:
    """Vrací True, pokud má uživatel aktivní předplatné."""
    try:
        customers = stripe.Customer.list(email=email, limit=1).data
        if not customers:
            return False
        customer = customers[0]
        subs = stripe.Subscription.list(customer=customer.id, status="active")
        return len(subs.data) > 0
    except Exception as e:
        st.error(f"Chyba při kontrole předplatného: {e}")
        return False

def paywall_ui(protected_content_callback):
    """Zobrazí paywall, dokud není aktivní předplatné."""
    st.title("🔒 Fotbalové predikce – předplatné")
    st.markdown("Plný přístup za **399 Kč / měsíc**")

    # email od uživatele
    email = st.text_input("E-mail pro aktivaci předplatného:")

    # Ověření předplatného
    if email and has_active_subscription(email):
        st.session_state.subscribed = True
        protected_content_callback()
        return

    # Platební tlačítko
    if email and st.button("Předplatit 399 Kč / měsíc"):
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": PRICE_ID, "quantity": 1}],
            mode="subscription",
            customer_email=email,
            success_url=st.query_params.get("PUBLIC_BASE_URL", "https://example.com"),
            cancel_url=st.query_params.get("PUBLIC_BASE_URL", "https://example.com"),
        )
        st.markdown(f"[👉 Klikněte zde pro platbu]({session.url})")

    st.stop()
