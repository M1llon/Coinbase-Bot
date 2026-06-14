import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

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

st.progress(min(1.0, (kurs_aktuell / MAKRO_ZIEL_WELLE_3)), text=f"Fortschritt zu Welle-3-Ziel (700€): {(kurs_aktuell / MAKRO_ZIEL_WELLE_3)*100:.1f}%")

# ==============================================================================
# 5. DIE NEUE GRAFISCHE VISUALISIERUNG (AUTOMATISCHER CHART)
# ==============================================================================
st.subheader("📈 Visueller Fahrplan im Chart")

nodes_x = [0, 2, 4, 5.2, 6.0, 7.8, 8.5, 10]
nodes_y = [31, 380, 135, 330, 230, 530, 410, 700]
labels = ["31€", "380€", "~135€", "~330€", "230€", "~530€", "410€", "700€"]

plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(nodes_x, nodes_y, '-', color='#1E88E5', linewidth=3)
ax.scatter(nodes_x, nodes_y, color='#0D47A1', s=60, edgecolors='white', linewidths=1)

# Dynamischer roter Punkt für Ihren aktuellen Live-Kurs im Chart
x_pos_aktuell = 4.0 + (teilwellen_fortschritt / 100.0) * 1.2 if kurs_aktuell < 330 else (5.2 + (teilwellen_fortschritt / 100.0) * 2.6 if kurs_aktuell < 530 else 7.8 + (teilwellen_fortschritt / 100.0) * 2.2)
ax.plot(x_pos_aktuell, kurs_aktuell, 'ro', markersize=12, markeredgecolor='white', label='AKTUELLE POSITION')

for i, txt in enumerate(labels):
    offset = (0, -18) if i in [0, 2, 4, 6] else (0, 8)
    ax.annotate(txt, (nodes_x[i], nodes_y[i]), textcoords="offset points", xytext=offset, ha='center', fontsize=9, color='#E0E0E0')

ax.set_ylim(0, 800)
ax.grid(True, linestyle=':', alpha=0.2)
ax.get_xaxis().set_visible(False)
st.pyplot(fig)

# 6. DIE STRATEGISCHEN WELLEN-FORTSCHRITTSBALKEN
st.subheader("🌊 SK-System & Elliott-Wellen Radar")
st.write(f"**Makro-Welle 2 (Korrektur-Bodenbildung):**")
st.progress(aktueller_korrektur_fortschritt / 100, text=f"Fortschritt zum SK-Kaufbereich (~135€): {aktueller_korrektur_fortschritt:.1f}%")

st.write(f"**Status im Bullenmarkt-Zyklus:** {aktuelle_teilwelle}")
st.progress(teilwellen_fortschritt / 100, text=f"Fortschritt dieser Teilphase: {teilwellen_fortschritt:.1f}%")

# 7. DIE KI-ENTSCHEIDUNGS-MATRIX
st.subheader("⚙️ Strategisches Bot-Kommando")

if rsi_live > dyn_ob and bearische_divergenz and kurs_aktuell >= (MAKRO_ZIEL_WELLE_3 * 0.8):
    st.error(f"🚨 CYCLICAL TOP ERREICHT! (RSI: {rsi_live:.1f})\n\n👉 EMPFEHLUNG: 100% KOMPLETT-VERKAUF bei {kurs_aktuell:.2f}€!")
elif rsi_live < dyn_os:
    st.warning(f"🟢 COINBASE IM PREIS-CONDOWN! (RSI: {rsi_live:.1f})")
    st.markdown("### 🔄 Risiko-Check:")
    st.write(f"• Bullische Divergenz am Boden: {'✅ AKTIV' if bullische_divergenz else '❌ FEHLT'}")
    st.write(f"• Bitcoin-Trend (über SMA50): {'✅ BULLISCH' if btc_bullisch else '❌ BÄRISCH'}")
else:
    st.info(f"😴 STATUS: ABSOLUTES HALTEN (HODL)\n\nDer RSI steht stabil bei {rsi_live:.1f} (Boden-Band bei: {dyn_os:.1f} | Top-Band bei: {dyn_ob:.1f}).")
