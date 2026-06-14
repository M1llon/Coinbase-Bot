import streamlit as st
import yfinance as yf
import pandas as pd

# 1. SMARTPHONE-LAYOUT & DEPOT-SETUP
st.set_page_config(page_title="Coinbase Kompass", page_icon="🤖", layout="centered")

ANZAHL_AKTIEN = 700
EINSTIEG_EUR = 57.07
STEUERSATZ = 0.26375
STEUER_FREIBETRAG = 1000.00

st.title("🤖 Coinbase Makro-Kompass")
st.write("Exklusives Dashboard für Ihr Trade Republic Depot")

# 2. BÖRSENDATEN LADEN
with st.spinner("Aktualisiere Live-Zyklen..."):
    coin = yf.download("COIN", period="2y", interval="1d", progress=False)
    btc = yf.download("BTC-USD", period="2y", interval="1d", progress=False)
    fx = yf.download("EURUSD=X", period="2y", interval="1d", progress=False)

df = pd.DataFrame({
    'USD_Close': coin['Close'].squeeze(),
    'USD_High': coin['High'].squeeze(),
    'USD_Low': coin['Low'].squeeze(),
    'BTC_USD': btc['Close'].squeeze(),
    'FX': fx['Close'].squeeze()
}).dropna()

df['Close'] = df['USD_Close'] / df['FX']
df['High'] = df['USD_High'] / df['FX']
df['Low'] = df['USD_Low'] / df['FX']

# Mathematischer Wilder's RSI (14) via EWM
delta = df['Close'].diff()
gain = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
loss = -delta.clip(upper=0).ewm(alpha=1/14, adjust=False).mean()
df['RSI'] = 100 - (100 / (1 + gain / loss))

# Volatilitäts-Bänder auf den RSI (Bollinger Bänder)
df['RSI_MA'] = df['RSI'].rolling(20).mean()
df['RSI_STD'] = df['RSI'].rolling(20).std()
df['OB'] = df['RSI_MA'] + (2 * df['RSI_STD'])
df['OS'] = df['RSI_MA'] - (2 * df['RSI_STD'])

# Live-Werte extrahieren
kurs_aktuell = df['Close'].iloc[-1]
rsi_live = df['RSI'].iloc[-1]
dyn_ob = df['OB'].iloc[-1]
dyn_os = df['OS'].iloc[-1]

# Multi-Faktor-Filter berechnen
bearische_divergenz = (df['Close'].iloc[-1] > df['Close'].iloc[-5]) and (df['RSI'].iloc[-1] < df['RSI'].iloc[-5])
bullische_divergenz = (df['Close'].iloc[-1] < df['Close'].iloc[-5]) and (df['RSI'].iloc[-1] > df['RSI'].iloc[-5])
btc_bullisch = df['BTC_USD'].iloc[-1] > df['BTC_USD'].rolling(50).mean().iloc[-1]

# ==============================================================================
# 3. ADVANCED ELLIOTT-WAVE & SK-SYSTEM MATH
# ==============================================================================
MAKRO_START_WELLE_1 = 31.00
MAKRO_TOP_WELLE_1 = 380.00
MAKRO_ZIEL_WELLE_3 = 700.00

# Berechnung Makro-Welle 2 (Korrektur-Bodenbildung zum 0.618er SK-Boden bei ~135€)
sk_boden_welle_2 = 135.00
spanne_korrektur = MAKRO_TOP_WELLE_1 - sk_boden_welle_2
aktueller_korrektur_fortschritt = max(0.0, min(100.0, ((MAKRO_TOP_WELLE_1 - kurs_aktuell) / spanne_korrektur) * 100))

# Fortschritts-Ermittlung innerhalb der inneren Wellen-Struktur der Welle 3
if kurs_aktuell < 330.00:
    aktuelle_teilwelle = "Innere Welle 1 (Erster Impuls nach oben)"
    teilwellen_fortschritt = max(0.0, min(100.0, ((kurs_aktuell - sk_boden_welle_2) / (330.00 - sk_boden_welle_2)) * 100))
elif kurs_aktuell >= 330.00 and kurs_aktuell < 530.00:
    aktuelle_teilwelle = "Innere Welle 3 (Die explosive Haupt-Welle)"
    teilwellen_fortschritt = max(0.0, min(100.0, ((kurs_aktuell - 330.00) / (530.00 - 330.00)) * 100))
else:
    aktuelle_teilwelle = "Innere Welle 5 (Das finale Makro-Top)"
    teilwellen_fortschritt = max(0.0, min(100.0, ((kurs_aktuell - 530.00) / (700.00 - 530.00)) * 100))

# Steuer-Kalkulation (Trade Republic Netto-Wert)
brutto_erloes = ANZAHL_AKTIEN * kurs_aktuell
buchgewinn = brutto_erloes - (ANZAHL_AKTIEN * EINSTIEG_EUR)
zu_versteuern = max(0, buchgewinn - STEUER_FREIBETRAG)
reale_steuer = zu_versteuern * STEUERSATZ
netto_cash = brutto_erloes - reale_steuer

# 4. BENUTZEROBERFLÄCHE
st.subheader("📊 Ihre Echtzeit-Vermögenswerte")
c1, c2 = st.columns(2)
c1.metric("Aktueller Kurs", f"{kurs_aktuell:.2f} €")
c2.metric("Brutto-Wert (700)", f"{brutto_erloes:,.2f} €")

c3, c4 = st.columns(2)
c4.metric("Buchgewinn", f"+{buchgewinn:,.2f} €")
c3.metric("Netto-Auszahlung", f"{netto_cash:,.2f} €")

# Welle-3-Fortschrittsbalken direkt unter den Vermögenswerten (Exakt wie auf Ihrem Screenshot)
st.progress(min(1.0, (kurs_aktuell / MAKRO_ZIEL_WELLE_3)), text=f"Fortschritt zu Welle-3-Ziel (700€): {(kurs_aktuell / MAKRO_ZIEL_WELLE_3)*100:.1f}%")

# 5. DIE STRATEGISCHEN WELLEN-FORTSCHRITTSBALKEN
st.subheader("🌊 SK-System & Elliott-Wellen Radar")

# Balken 1: Fortschritt der übergeordneten Korrektur (Welle 2)
st.write(f"**Makro-Welle 2 (Korrektur-Bodenbildung):**")
st.progress(aktueller_korrektur_fortschritt / 100, text=f"Fortschritt zum SK-Kaufbereich (~135€): {aktueller_korrektur_fortschritt:.1f}%")

# Balken 2: Fortschritt der inneren Zyklus-Strukturen bis zum 700€ Top
st.write(f"**Status im Bullenmarkt-Zyklus:** {aktuelle_teilwelle}")
st.progress(teilwellen_fortschritt / 100, text=f"Fortschritt dieser Teilphase: {teilwellen_fortschritt:.1f}%")

# 6. DIE KI-ENTSCHEIDUNGS-MATRIX
st.subheader("⚙️ Strategisches Bot-Kommando")

if rsi_live > dyn_ob and bearische_divergenz and kurs_aktuell >= (MAKRO_ZIEL_WELLE_3 * 0.8):
    st.error(f"🚨 CYCLICAL TOP ERREICHT! (RSI: {rsi_live:.1f})\n\n"
             f"Die Indikatoren GLÜHEN an der Spitze der Welle.\n"
             f"👉 EMPFEHLUNG: 100% KOMPLETT-VERKAUF bei {kurs_aktuell:.2f}€!\n"
             f"Parken Sie {netto_cash:,.2f}€ auf Ihrem Verrechnungskonto.")

elif rsi_live < dyn_os:
    st.warning(f"🟢 COINBASE IM PREIS-CONDOWN! (RSI: {rsi_live:.1f})\n\n"
               f"Das mathematische Band nach unten wurde durchbrochen. Der Preis von {kurs_aktuell:.2f}€ ist statistisch extrem günstig.")
    
    st.markdown("### 🔄 Ihre 2 Optionen für das geparkte Cash:")
    st.info("**OPTION A (Aggressiver Dip-Kauf):**\n"
            "Schlagen Sie JETZT im freien Fall zu, um den potenziell tiefsten Punkt zu sichern.")
    
    st.markdown("**OPTION B (Sicherer Einstieg mit Bestätigung):**")
    if not bullische_divergenz:
        st.write("• ❌ *Keine bullische Divergenz:* Der Verkaufsdruck am Markt ist aktuell noch hoch.")
    else:
        st.write("• ✅ *Bullische Divergenz aktiv:* Die Verkäufer verlieren an Kraft!")
        
    if not btc_bullisch:
        st.write("• ❌ *Bitcoin schwächelt:* BTC steht unter dem SMA50. Gefahr von Mitreißeffekten.")
    else:
        st.write("• ✅ *Bitcoin stabilisiert sich:* Der Gesamtmarkt stützt die Aktie.")
        
    if bullische_divergenz and btc_bullisch:
        st.success("👉 *Bot-Empfehlung:* ALLE Filter sind grün! Option B ist jetzt freigegeben. Kaufen!")
    else:
        st.error("👉 *Bot-Empfehlung:* Warten Sie noch, bis beide Warnpunkte verschwinden, um nicht in ein fallendes Messer zu greifen.")

else:
    st.info(f"😴 STATUS: ABSOLUTES HALTEN (HODL)\n\n"
            f"Der Markt befindet sich im Niemandsland. Der RSI steht stabil bei {rsi_live:.1f} "
            f"(Boden-Band bei: {dyn_os:.1f} | Top-Band bei: {dyn_ob:.1f}).\n\n"
            f"👉 HANDLUNG: Füße stillhalten, keine unüberlegten Verkäufe.")
