from py_vollib.black_scholes.greeks.analytical import delta, theta

# ================= PCR =================
def calculate_pcr(df):
    put_oi = df[df["type"] == "PE"]["oi"].sum()
    call_oi = df[df["type"] == "CE"]["oi"].sum()

    if call_oi == 0:
        return None

    return round(put_oi / call_oi, 2)


# ================= SUPPORT & RESISTANCE =================
def support_resistance(df):
    pe = df[df["type"] == "PE"]
    ce = df[df["type"] == "CE"]

    support = pe.loc[pe["oi"].idxmax(), "strike"]
    resistance = ce.loc[ce["oi"].idxmax(), "strike"]

    return support, resistance


# ================= MAX PAIN =================
def calculate_max_pain(df):
    strikes = sorted(df["strike"].unique())

    ce = df[df["type"] == "CE"]
    pe = df[df["type"] == "PE"]

    pain_by_strike = {}

    for strike in strikes:
        call_pain = ((ce["strike"] - strike).clip(lower=0) * ce["oi"]).sum()
        put_pain = ((strike - pe["strike"]).clip(lower=0) * pe["oi"]).sum()
        pain_by_strike[strike] = call_pain + put_pain

    return min(pain_by_strike, key=pain_by_strike.get)


# ================= GREEKS (DELTA & THETA) =================
def calculate_greeks(
    row,
    spot,
    rate=0.06,          # Risk-free rate (India ~6%)
    days_to_expiry=7,   # Weekly expiry assumption
    iv=0.20             # Assumed implied volatility
):
    try:
        flag = "c" if row["type"] == "CE" else "p"
        T = days_to_expiry / 365

        d = delta(flag, spot, row["strike"], T, rate, iv)
        t = theta(flag, spot, row["strike"], T, rate, iv)

        return round(d, 3), round(t, 3)

    except Exception:
        return None, None
