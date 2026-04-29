import streamlit as st
from datetime import date, datetime, timedelta
import math
import copy

# Copy and paste the following line into your terminal to run the app:
# Save to update new code thats been added/changed
# streamlit run ElectRAM_Flights_Web.py

# This is the version of the code prior to most of the UI rendering logic being 
# converted for phone use

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ElectRAM – Flight Search",
    page_icon="✈",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  :root { --bg:#F7F8FA; --white:#FFFFFF; --dark:#1A1A2E; --grey:#75787b; --light-grey:#E5E7EB; --border:#D1D5DB; --section-bg:#F3F4F6; --gold:#B8860B; --maroon:#861F41; --orange:#E5751F; --red-light:#FFF1F3; }
  html, body, .stApp, [data-testid="stAppViewContainer"] { background: var(--bg) !important; color: var(--dark) !important; font-family: "Segoe UI", Arial, sans-serif !important; }
  [data-testid="stHeader"] { background: transparent !important; }
  .block-container { max-width: 480px !important; padding-top:0 !important; padding-left:.75rem !important; padding-right:.75rem !important; }
  #MainMenu, footer, header { visibility:hidden; }

  /* ── Banner ── */
  .banner { background:var(--maroon); color:white; padding:16px 16px 12px 16px; margin:0 -.75rem 1rem -.75rem; text-align:center; border-bottom:1px solid #74203A; }
  .banner h1 { font-family:Georgia,serif; font-size:1.65rem; font-weight:700; margin:0; line-height:1.1; letter-spacing:.2px; }
  .banner p { font-size:.76rem; color:#AAB0B8; margin:5px 0 0 0; }

  /* ── Search card ── */
  .search-card-marker { display:none; }
  .search-card-marker + div { background:white; border:1px solid var(--border); padding:14px 14px; margin:0 0 1rem 0; border-radius:4px !important; box-shadow:none; }

  /* ── Inputs ── */
  label, .stCaption, [data-testid="stCaptionContainer"] { color:var(--grey) !important; font-size:.76rem !important; }
  div[data-testid="stRadio"] label p { color:var(--dark) !important; font-size:.88rem !important; }
  div[data-testid="stSelectbox"] div, div[data-testid="stDateInput"] div { color:var(--dark) !important; }
  div[data-testid="stSelectbox"] > div, div[data-testid="stDateInput"] > div { background:white !important; border:1px solid var(--border) !important; border-radius:2px !important; }
  div[data-testid="stDateInput"] input { background:white !important; color:var(--dark) !important; font-size:.85rem !important; }
  div[data-testid="stSelectbox"] [data-baseweb="select"] { background:white !important; }
  div[data-testid="stSelectbox"] [data-baseweb="select"] > div { background:white !important; color:var(--dark) !important; font-size:.85rem !important; }
  div[data-testid="stSelectbox"] [data-baseweb="select"] * { background-color:white !important; color:var(--dark) !important; }
  div[data-testid="stSelectbox"] [data-baseweb="select"] svg { fill:var(--dark) !important; }

  /* ── Buttons ── */
  div[data-testid="stButton"] > button { background:var(--orange) !important; color:white !important; border:none !important; border-radius:2px !important; font-weight:700 !important; min-height:42px; font-size:.88rem !important; box-shadow:none !important; }
  div[data-testid="stButton"] > button:hover { background:var(--maroon) !important; color:white !important; }
  div[data-testid="stButton"] > button { display:flex !important; align-items:center !important; justify-content:center !important; }
  div[data-testid="stAlert"] { color:var(--dark) !important; }
  div[data-testid="stAlert"] * { color:var(--dark) !important; }

  /* ── Results header ── */
  .results-header { display:flex; flex-direction:column; gap:4px; margin:4px 0 8px 0; }
  .results-title { font-size:1.1rem; font-weight:800; color:var(--dark); }
  .results-sub { font-size:.76rem; color:var(--grey); }
  .section-header { background:var(--section-bg); border:1px solid var(--border); color:var(--grey); font-size:.7rem; font-weight:800; padding:7px 12px; letter-spacing:.4px; margin-bottom:0; text-transform:uppercase; white-space:normal; word-break:break-word; }

  /* ── Flight card – stacked mobile layout ── */
  .flight-card { background:var(--white); border:1px solid var(--border); margin:0 0 12px 0; overflow:hidden; }
  .flight-card-popular-banner { background:var(--section-bg); color:var(--gold); font-weight:800; font-size:.7rem; text-align:right; padding:5px 12px; border-bottom:1px solid var(--border); }
  .flight-card-body { display:flex; flex-direction:column; padding:12px 14px 10px 14px; gap:10px; }

  /* Times row */
  .flight-times { display:flex; align-items:baseline; gap:6px; justify-content:center; white-space:nowrap; }
  .time-big { font-family:Georgia,serif; font-size:1.7rem; font-weight:800; color:var(--dark); line-height:1; }
  .time-ampm { font-family:Georgia,serif; font-size:.82rem; font-weight:800; color:var(--grey); }
  .flight-arrow { color:var(--grey); font-size:.9rem; padding:0 6px; }

  /* Mid: duration + codes */
  .flight-mid { display:flex; flex-direction:column; align-items:stretch; gap:3px; }
  .flight-dur { text-align:center; font-weight:800; font-size:.88rem; margin-bottom:4px; }
  .dur-nonstop { color:var(--grey); } .dur-stop { color:var(--orange); }
  .flight-divider { height:2px; background:var(--grey); margin:4px 0 6px 0; }
  .flight-codes { display:flex; justify-content:center; align-items:center; gap:6px; color:var(--grey); font-size:.78rem; flex-wrap:wrap; }
  .flight-code-bold { font-weight:900; color:var(--dark); }

  /* Price panel – full-width strip at bottom of card on mobile */
  .price-panel { background:var(--section-bg); border:1px solid var(--border); border-left:none; border-right:none; border-bottom:none; padding:10px 14px 8px 14px; text-align:center; display:flex; flex-direction:row; justify-content:center; align-items:center; gap:14px; margin-top:4px; }
  .price-big { font-family:Georgia,serif; color:var(--dark); font-size:1.55rem; font-weight:800; line-height:1.1; }
  .seats-left { color:var(--orange); font-size:.76rem; }
  .connection-note { color:var(--grey); font-size:.76rem; padding:0 14px 8px 14px; }
  .time-advantage-box { background:var(--red-light); border:1px solid var(--border); margin:0 12px 10px 12px; padding:8px 12px; font-size:.78rem; }
  .ta-label { color:var(--maroon); font-weight:800; font-size:.7rem; margin-bottom:2px; }
  .ta-detail { color:var(--dark); }

  /* Round trip card */
  .rt-section-label { background:var(--section-bg); color:var(--grey); font-size:.7rem; font-weight:800; padding:6px 14px; border-bottom:1px solid var(--border); text-transform:uppercase; }
  .rt-divider { height:1px; background:var(--dark); margin:0; }
  .rt-price-row { background:var(--section-bg); border-top:1px solid var(--border); padding:10px 14px 14px 14px; display:flex; flex-direction:column; align-items:flex-start; gap:4px; }
  .rt-price-text { font-family:Georgia,serif; font-size:1.35rem; font-weight:800; color:var(--dark); }
  .savings-note { color:var(--grey); font-weight:800; font-size:.76rem; }

  /* Flight days table – horizontal scroll */
  .fdays-scroll { overflow-x:auto; -webkit-overflow-scrolling:touch; }
  .fdays-table { width:100%; border-collapse:collapse; background:white; min-width:340px; }
  .fdays-table th { font-size:.72rem; color:var(--dark); padding:5px 5px; text-align:center; }
  .fdays-table th:first-child { text-align:left; }
  .fdays-table td { padding:2px 2px; }
  .fdays-route { font-size:.75rem; font-weight:800; color:var(--dark); }
  .fdays-city { font-size:.65rem; color:var(--grey); }
  .day-cell-on { background:#63F542; height:20px; border-radius:2px; }
  .day-cell-off { background:#EF2B2B; height:20px; border-radius:2px; }
    /* ── Force compact mobile layout instead of Streamlit stacking ── */
  @media (max-width: 640px) {
    .block-container {
      max-width: 480px !important;
      padding-left: 13px !important;
      padding-right: 13px !important;
    }

    div[data-testid="stHorizontalBlock"] {
      display: flex !important;
      flex-direction: row !important;
      flex-wrap: nowrap !important;
      gap: 8px !important;
      align-items: end !important;
    }

    div[data-testid="stHorizontalBlock"] > div {
      width: auto !important;
      flex: 1 1 0 !important;
      min-width: 0 !important;
    }

    div[data-testid="stHorizontalBlock"] > div:has(#swap_btn) {
      flex: 0 0 42px !important;
      max-width: 42px !important;
    }

    div[data-testid="stHorizontalBlock"] > div:has(#pax_minus),
    div[data-testid="stHorizontalBlock"] > div:has(#pax_plus) {
      flex: 0 0 64px !important;
      max-width: 64px !important;
    }

    div[data-testid="stButton"] > button {
      min-height: 42px !important;
      padding: 0 8px !important;
      font-size: 0.9rem !important;
    }

    div[data-testid="stRadio"] {
      margin-bottom: 0 !important;
    }

    div[data-testid="stRadio"] > div {
      flex-direction: row !important;
      gap: 12px !important;
      flex-wrap: nowrap !important;
    }

    div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
    div[data-testid="stDateInput"] input {
      min-height: 42px !important;
      font-size: 0.8rem !important;
    }
  }
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────

AIRPORTS = [
    ("CRW", "Charleston, WV"),
    ("ATL", "Atlanta, GA"),
    ("CLT", "Charlotte, NC"),
    ("ROA", "Roanoke, VA"),
    ("TRI", "Tri-Cities, TN"),
    ("LEX", "Lexington, KY"),
    ("CKB", "Clarksburg/Bridgeport, WV"),
    ("MGW", "Morgantown, WV"),
    ("BNA", "Nashville, TN"),
    ("IND", "Indianapolis, IN"),
    ("SDF", "Louisville, KY"),
    ("HTS", "Huntington, WV"),
    ("SHD", "Shenandoah Valley, VA"),
]

AIRPORT_CODES = {code: city for code, city in AIRPORTS}

ROUTES = {
    ("CRW", "ATL"): {"dur_h": 1, "dur_m": 20},
    ("CRW", "CLT"): {"dur_h": 1, "dur_m": 0},
    ("CRW", "ROA"): {"dur_h": 0, "dur_m": 35},
    ("CRW", "TRI"): {"dur_h": 0, "dur_m": 50},
    ("CRW", "LEX"): {"dur_h": 0, "dur_m": 45},
    ("CRW", "CKB"): {"dur_h": 0, "dur_m": 25},
    ("CRW", "MGW"): {"dur_h": 0, "dur_m": 30},
    ("CRW", "BNA"): {"dur_h": 1, "dur_m": 15},
    ("CRW", "IND"): {"dur_h": 1, "dur_m": 20},
    ("CRW", "SDF"): {"dur_h": 1, "dur_m": 0},
    ("CRW", "HTS"): {"dur_h": 0, "dur_m": 25},
    ("CRW", "SHD"): {"dur_h": 0, "dur_m": 45},
    ("ROA", "CLT"): {"dur_h": 0, "dur_m": 50},
    ("CLT", "ATL"): {"dur_h": 1, "dur_m": 5},
    ("ATL", "CLT"): {"dur_h": 1, "dur_m": 5},
    ("TRI", "ATL"): {"dur_h": 1, "dur_m": 10},
    ("LEX", "IND"): {"dur_h": 0, "dur_m": 50},
    ("HTS", "CLT"): {"dur_h": 1, "dur_m": 10},
    ("SHD", "CLT"): {"dur_h": 1, "dur_m": 15},
    ("ROA", "CRW"): {"dur_h": 0, "dur_m": 35},
    ("CLT", "CRW"): {"dur_h": 1, "dur_m": 0},
    ("ATL", "CRW"): {"dur_h": 1, "dur_m": 20},
    ("TRI", "CLT"): {"dur_h": 1, "dur_m": 0},
    ("CLT", "TRI"): {"dur_h": 1, "dur_m": 0},
    ("LEX", "CLT"): {"dur_h": 1, "dur_m": 10},
    ("CLT", "LEX"): {"dur_h": 1, "dur_m": 10},
    ("SDF", "CLT"): {"dur_h": 1, "dur_m": 15},
    ("CLT", "SDF"): {"dur_h": 1, "dur_m": 15},
    ("BNA", "ATL"): {"dur_h": 1, "dur_m": 5},
    ("ATL", "BNA"): {"dur_h": 1, "dur_m": 5},
    ("BNA", "CLT"): {"dur_h": 1, "dur_m": 20},
    ("CLT", "BNA"): {"dur_h": 1, "dur_m": 20},
    ("IND", "CLT"): {"dur_h": 1, "dur_m": 25},
    ("CLT", "IND"): {"dur_h": 1, "dur_m": 25},
    ("MGW", "CRW"): {"dur_h": 0, "dur_m": 30},
    ("CKB", "CRW"): {"dur_h": 0, "dur_m": 25},
    ("HTS", "CRW"): {"dur_h": 0, "dur_m": 25},
    ("SHD", "CRW"): {"dur_h": 0, "dur_m": 45},
}

ROUTE_DAYS = {
    ("CRW", "ATL"): [0, 1, 2, 3, 4, 5, 6],
    ("CRW", "CLT"): [0, 1, 2, 3, 4, 5, 6],
    ("CRW", "ROA"): [0, 2, 4],
    ("CRW", "TRI"): [1, 3, 5],
    ("CRW", "LEX"): [0, 3, 6],
    ("CRW", "CKB"): [0, 1, 2, 3, 4],
    ("CRW", "MGW"): [0, 1, 2, 3, 4],
    ("CRW", "BNA"): [1, 4, 6],
    ("CRW", "IND"): [0, 2, 5],
    ("CRW", "SDF"): [1, 3, 6],
    ("CRW", "HTS"): [0, 1, 2, 3, 4],
    ("CRW", "SHD"): [2, 5],
    ("ROA", "CLT"): [0, 1, 2, 3, 4, 5, 6],
    ("CLT", "ATL"): [0, 1, 2, 3, 4, 5, 6],
    ("ATL", "CLT"): [0, 1, 2, 3, 4, 5, 6],
    ("TRI", "ATL"): [0, 2, 4],
    ("LEX", "IND"): [1, 3, 5],
    ("HTS", "CLT"): [0, 2, 4],
    ("SHD", "CLT"): [1, 4],
    ("ROA", "CRW"): [0, 2, 4],
    ("CLT", "CRW"): [0, 1, 2, 3, 4, 5, 6],
    ("ATL", "CRW"): [0, 1, 2, 3, 4, 5, 6],
    ("TRI", "CLT"): [1, 3, 5],
    ("CLT", "TRI"): [1, 3, 5],
    ("LEX", "CLT"): [0, 3, 6],
    ("CLT", "LEX"): [0, 3, 6],
    ("SDF", "CLT"): [1, 3, 6],
    ("CLT", "SDF"): [1, 3, 6],
    ("BNA", "ATL"): [1, 4, 6],
    ("ATL", "BNA"): [1, 4, 6],
    ("BNA", "CLT"): [1, 4, 6],
    ("CLT", "BNA"): [1, 4, 6],
    ("IND", "CLT"): [0, 2, 5],
    ("CLT", "IND"): [0, 2, 5],
    ("MGW", "CRW"): [0, 1, 2, 3, 4],
    ("CKB", "CRW"): [0, 1, 2, 3, 4],
    ("HTS", "CRW"): [0, 1, 2, 3, 4],
    ("SHD", "CRW"): [2, 5],
}

DRIVE_TIMES = {
    ("CRW", "ATL"): {"h": 7, "m": 0},
    ("CRW", "CLT"): {"h": 4, "m": 15},
    ("CRW", "ROA"): {"h": 2, "m": 45},
    ("CRW", "TRI"): {"h": 3, "m": 25},
    ("CRW", "LEX"): {"h": 2, "m": 50},
    ("CRW", "CKB"): {"h": 2, "m": 5},
    ("CRW", "MGW"): {"h": 2, "m": 35},
    ("CRW", "BNA"): {"h": 6, "m": 15},
    ("CRW", "IND"): {"h": 5, "m": 45},
    ("CRW", "SDF"): {"h": 4, "m": 0},
    ("CRW", "HTS"): {"h": 1, "m": 0},
    ("CRW", "SHD"): {"h": 4, "m": 0},
    ("ROA", "CLT"): {"h": 3, "m": 0},
    ("CLT", "ATL"): {"h": 4, "m": 15},
    ("ATL", "CLT"): {"h": 4, "m": 15},
    ("TRI", "ATL"): {"h": 4, "m": 45},
    ("LEX", "IND"): {"h": 3, "m": 0},
    ("HTS", "CLT"): {"h": 4, "m": 30},
    ("SHD", "CLT"): {"h": 4, "m": 45},
}

# ── Logic ─────────────────────────────────────────────────────────────────────

def get_route(dep, arr):
    if (dep, arr) in ROUTES:
        return ROUTES[(dep, arr)]
    if (arr, dep) in ROUTES:
        return ROUTES[(arr, dep)]
    return None

def get_route_days(dep, arr):
    if (dep, arr) in ROUTE_DAYS:
        return ROUTE_DAYS[(dep, arr)]
    if (arr, dep) in ROUTE_DAYS:
        return ROUTE_DAYS[(arr, dep)]
    return None

def route_operates_on_date(dep, arr, d):
    operating_days = get_route_days(dep, arr)
    if operating_days is None:
        return False
    return d.weekday() in operating_days

def operating_days_text(dep, arr):
    days = get_route_days(dep, arr)

    if days is None:
        return None

    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return ", ".join(day_names[d] for d in days)

def find_connection(dep, arr, d):
    valid_connections = []
    for mid, city in AIRPORTS:
        if mid == dep or mid == arr:
            continue
        first_route = get_route(dep, mid)
        second_route = get_route(mid, arr)
        if not first_route or not second_route:
            continue
        if not route_operates_on_date(dep, mid, d):
            continue
        if not route_operates_on_date(mid, arr, d):
            continue
        layover_minutes = 45
        total_minutes = (
            first_route["dur_h"] * 60 + first_route["dur_m"] +
            layover_minutes +
            second_route["dur_h"] * 60 + second_route["dur_m"]
        )
        valid_connections.append({
            "mid": mid,
            "first_route": first_route,
            "second_route": second_route,
            "total_minutes": total_minutes,
        })
    if not valid_connections:
        return None
    best = min(valid_connections, key=lambda x: x["total_minutes"])
    return best["mid"], best["first_route"], best["second_route"]

def add_minutes(hour, minute, duration_h, duration_m):
    total_minutes = hour * 60 + minute + duration_h * 60 + duration_m
    return (total_minutes // 60) % 24, total_minutes % 60

def flight_price(h, m, booking_mode="seat"):
    fh = h + m / 60
    cost_fh = 1209
    fluff = 200
    cost_seat_hour = (cost_fh + fluff) / 19
    desired_profit = 40
    rate_seat_whole = fh * cost_seat_hour + desired_profit
    rate_ac_whole = (cost_fh + fluff) * fh + desired_profit
    rate_seat = math.ceil(rate_seat_whole / 10) * 10 - 1
    rate_ac = math.ceil(rate_ac_whole / 10) * 10 - 1
    if booking_mode == "charter":
        rate_ac += 500
        return rate_ac
    return rate_seat

def generate_flights(dep, arr, d, count=5):
    route = get_route(dep, arr)
    if route is None:
        return []
    if not route_operates_on_date(dep, arr, d):
        return []
    departure_times = [(9,0),(11,0),(13,0),(15,0),(17,0)]
    flights = []
    for i, (dep_h, dep_m) in enumerate(departure_times[:count]):
        arr_h, arr_m = add_minutes(dep_h, dep_m, route["dur_h"], route["dur_m"])
        seat_price = flight_price(route["dur_h"], route["dur_m"], "seat")
        aircraft_price = flight_price(route["dur_h"], route["dur_m"], "charter")
        if i == 0:
            seat_price += 20
        elif i == 2:
            seat_price -= 10
        flights.append({
            "dep_h": dep_h, "dep_m": dep_m, "arr_h": arr_h, "arr_m": arr_m,
            "dur_h": route["dur_h"], "dur_m": route["dur_m"],
            "stops": "Nonstop", "aircraft": "E.C.H.O.",
            "price": seat_price, "aircraft_price": aircraft_price,
            "seats_left": 2 if i == 0 else None,
            "popular": True if i == 1 else False,
            "dep_code": dep, "arr_code": arr,
            "dep_city": AIRPORT_CODES.get(dep, dep),
            "arr_city": AIRPORT_CODES.get(arr, arr),
        })
    return flights

def generate_multileg_flights(dep, arr, d, count=5):
    direct = generate_flights(dep, arr, d, count)
    if direct:
        return direct, "direct"
    connection = find_connection(dep, arr, d)
    if connection is None:
        return [], "none"
    mid, first_route, second_route = connection
    departure_times = [(8,0),(11,0),(14,0)]
    itineraries = []
    for i, (dep_h, dep_m) in enumerate(departure_times[:count]):
        mid_arr_h, mid_arr_m = add_minutes(dep_h, dep_m, first_route["dur_h"], first_route["dur_m"])
        second_dep_h, second_dep_m = add_minutes(mid_arr_h, mid_arr_m, 0, 45)
        final_arr_h, final_arr_m = add_minutes(second_dep_h, second_dep_m, second_route["dur_h"], second_route["dur_m"])
        price1 = flight_price(first_route["dur_h"], first_route["dur_m"], "seat")
        aircraft_price1 = flight_price(first_route["dur_h"], first_route["dur_m"], "charter")
        price2 = flight_price(second_route["dur_h"], second_route["dur_m"], "seat")
        aircraft_price2 = flight_price(second_route["dur_h"], second_route["dur_m"], "charter")
        itineraries.append({
            "multi_leg": True, "connection": mid,
            "leg1": {
                "dep_h": dep_h, "dep_m": dep_m, "arr_h": mid_arr_h, "arr_m": mid_arr_m,
                "dur_h": first_route["dur_h"], "dur_m": first_route["dur_m"],
                "stops": "Nonstop", "aircraft": "E.C.H.O.",
                "price": price1, "aircraft_price": aircraft_price1,
                "seats_left": 2 if i == 0 else None, "popular": True if i == 1 else False,
                "dep_code": dep, "arr_code": mid,
                "dep_city": AIRPORT_CODES.get(dep, dep), "arr_city": AIRPORT_CODES.get(mid, mid),
            },
            "leg2": {
                "dep_h": second_dep_h, "dep_m": second_dep_m, "arr_h": final_arr_h, "arr_m": final_arr_m,
                "dur_h": second_route["dur_h"], "dur_m": second_route["dur_m"],
                "stops": "Nonstop", "aircraft": "E.C.H.O.",
                "price": price2, "aircraft_price": aircraft_price2,
                "seats_left": 2 if i == 0 else None, "popular": True if i == 1 else False,
                "dep_code": mid, "arr_code": arr,
                "dep_city": AIRPORT_CODES.get(mid, mid), "arr_city": AIRPORT_CODES.get(arr, arr),
            },
            "price": price1 + price2,
        })
    return itineraries, "connection"

def random_flights(dep, arr, d, count=5):
    flights, _ = generate_multileg_flights(dep, arr, d, count)
    return flights

def fmt_time(h, m):
    ampm = "AM" if h < 12 else "PM"
    return f"{h % 12 or 12}:{m:02d}", ampm

def get_drive_time(dep, arr):
    if (dep, arr) in DRIVE_TIMES:
        return DRIVE_TIMES[(dep, arr)]
    if (arr, dep) in DRIVE_TIMES:
        return DRIVE_TIMES[(arr, dep)]
    return None

def time_to_minutes(t):
    return t["h"] * 60 + t["m"]

def minutes_to_str(minutes):
    h = minutes // 60
    m = minutes % 60
    if h == 0:
        return f"{m} min"
    if m == 0:
        return f"{h}h"
    return f"{h}h {m}m"

def flight_duration_minutes(f):
    if f.get("multi_leg"):
        return (f["leg1"]["dur_h"]*60 + f["leg1"]["dur_m"] + 45 +
                f["leg2"]["dur_h"]*60 + f["leg2"]["dur_m"])
    return f["dur_h"]*60 + f["dur_m"]

def route_drive_minutes(f):
    if f.get("multi_leg"):
        leg1_drive = get_drive_time(f["leg1"]["dep_code"], f["leg1"]["arr_code"])
        leg2_drive = get_drive_time(f["leg2"]["dep_code"], f["leg2"]["arr_code"])
        if not leg1_drive or not leg2_drive:
            return None
        return time_to_minutes(leg1_drive) + time_to_minutes(leg2_drive)
    drive = get_drive_time(f.get("dep_code",""), f.get("arr_code",""))
    return time_to_minutes(drive) if drive else None

def apply_booking_mode(flights, booking_mode):
    processed = []
    for f in flights:
        f_copy = copy.deepcopy(f)
        if f_copy.get("multi_leg"):
            if booking_mode == "charter":
                f_copy["display_price"] = (f_copy["leg1"]["aircraft_price"] +
                                           f_copy["leg2"]["aircraft_price"])
            else:
                f_copy["display_price"] = f_copy["price"]
        else:
            if booking_mode == "charter":
                f_copy["display_price"] = f_copy["aircraft_price"]
            else:
                f_copy["display_price"] = f_copy["price"]
        processed.append(f_copy)
    return processed

# ── UI Helpers ────────────────────────────────────────────────────────────────

def erj_savings_html(display_price):
    erj_cost_fh = 7450
    echo_cost_fh = 2009
    savings_pct = (1 - (echo_cost_fh / erj_cost_fh)) * 100
    return f'<span class="savings-note">E.C.H.O. est. ~{savings_pct:.0f}% lower cost than ERJ</span>'

def render_time_advantage(f):
    drive_min = route_drive_minutes(f)
    if drive_min is None:
        return ""
    fly_min = flight_duration_minutes(f)
    saved = drive_min - fly_min
    if saved <= 0:
        return ""
    return f"""
    <div class="time-advantage-box">
      <div class="ta-label">Time Advantage</div>
      <div class="ta-detail">
        Drive: {minutes_to_str(drive_min)} &nbsp;·&nbsp;
        Flight: {minutes_to_str(fly_min)} &nbsp;·&nbsp;
        Time saved: {minutes_to_str(saved)}
      </div>
    </div>"""

def render_flight_card(f, key, booking_mode, passengers, context="outbound"):
    dep_t, dep_ap = fmt_time(f["dep_h"], f["dep_m"])
    arr_t, arr_ap = fmt_time(f["arr_h"], f["arr_m"])
    dur_str = f"{f['dur_h']}h {f['dur_m']}m" if f['dur_m'] else f"{f['dur_h']}h"
    stops_cls = "dur-stop" if f["stops"] != "Nonstop" else "dur-nonstop"
    display_price = f.get("display_price", f["price"])
    savings_html = ""
    if booking_mode == "charter":
        savings_html = erj_savings_html(display_price)

    popular_banner = ""
    if f.get("popular"):
        popular_banner = '<div class="flight-card-popular-banner">★ MOST POPULAR</div>'

    seats_html = ""
    if f.get("seats_left"):
        seats_html = f'<div class="seats-left">{f["seats_left"]} seat{"s" if f["seats_left"]>1 else ""} left</div>'

    ta_html = render_time_advantage(f)

    html = f"""
    <div class="flight-card">
      {popular_banner}
      <div class="flight-card-body">
        <div class="flight-times">
          <span class="time-big">{dep_t}</span><span class="time-ampm">{dep_ap}</span>
          <span class="flight-arrow">&nbsp;──✈──&nbsp;</span>
          <span class="time-big">{arr_t}</span><span class="time-ampm">{arr_ap}</span>
        </div>
        <div class="flight-mid">
          <div class="flight-dur {stops_cls}">{dur_str} &nbsp;·&nbsp; {f['stops']}</div>
          <div class="flight-divider"></div>
          <div class="flight-codes">
            <span class="flight-code-bold">{f['dep_code']}</span>
            <span>{f['dep_city']}</span>
            <span>&nbsp;✈ {f['aircraft']}&nbsp;</span>
            <span class="flight-code-bold">{f['arr_code']}</span>
            <span>{f['arr_city']}</span>
          </div>
        </div>
        <div class="price-panel">
          <div class="price-big">${display_price}</div>
          {savings_html}
          {seats_html}
          <div id="btn-{key}"></div>
        </div>
      </div>
      {ta_html}
    </div>"""

    st.html(html)
    selected = st.button("SELECT", key=key, use_container_width=True)

    if selected:
        if booking_mode == "charter":
            price_label = "Aircraft charter price"
            passenger_line = "Aircraft charter includes up to 19 seats"
            total = display_price
        else:
            price_label = "Price per person"
            passenger_line = f"Passengers: {passengers}"
            total = display_price * passengers

        st.success("Flight Selected ✔")

        st.markdown(f"""
        <div style="
            background: var(--section-bg);
            border: 1px solid var(--border);
            padding: 14px 18px;
            margin-top: 8px;
            border-radius: 4px;
        ">
          <div style="font-size: 0.95rem; color: var(--dark);">
            <b>{f['dep_code']} → {f['arr_code']}</b> &nbsp;&nbsp;
            {dep_t}{dep_ap} – {arr_t}{arr_ap} &nbsp;·&nbsp; {dur_str} &nbsp;·&nbsp; {f['stops']}
          </div>
          <div style="margin-top: 6px; font-size: 0.9rem;">
            <b>{price_label}:</b> ${display_price} &nbsp;&nbsp;|&nbsp;&nbsp;
            {passenger_line} &nbsp;&nbsp;|&nbsp;&nbsp;
            <b>Total:</b> ${total}
          </div>
          <div style="margin-top: 6px; font-size: 0.8rem; color: var(--grey);">
            Proceeding to checkout…
          </div>
        </div>
        """, unsafe_allow_html=True)

def render_multileg_card(itin, key, booking_mode, passengers):
    leg1 = itin["leg1"]
    leg2 = itin["leg2"]
    combined = {
        "dep_h": leg1["dep_h"], "dep_m": leg1["dep_m"],
        "arr_h": leg2["arr_h"], "arr_m": leg2["arr_m"],
        "dur_h": flight_duration_minutes(itin) // 60,
        "dur_m": flight_duration_minutes(itin) % 60,
        "stops": "1 Stop", "aircraft": "E.C.H.O.",
        "price": itin.get("display_price", itin["price"]),
        "display_price": itin.get("display_price", itin["price"]),
        "seats_left": None,
        "popular": leg1.get("popular", False) or leg2.get("popular", False),
        "dep_code": leg1["dep_code"], "arr_code": leg2["arr_code"],
        "dep_city": leg1["dep_city"], "arr_city": leg2["arr_city"],
    }
    dep_t, dep_ap = fmt_time(combined["dep_h"], combined["dep_m"])
    arr_t, arr_ap = fmt_time(combined["arr_h"], combined["arr_m"])
    dur_str = f"{combined['dur_h']}h {combined['dur_m']}m" if combined['dur_m'] else f"{combined['dur_h']}h"
    display_price = combined["display_price"]
    savings_html = ""
    if booking_mode == "charter":
        savings_html = erj_savings_html(display_price)

    popular_banner = ""
    if combined.get("popular"):
        popular_banner = '<div class="flight-card-popular-banner">★ MOST POPULAR</div>'

    ta_html = render_time_advantage(itin)

    html = f"""
    <div class="flight-card">
      {popular_banner}
      <div class="flight-card-body">
        <div class="flight-times">
          <span class="time-big">{dep_t}</span><span class="time-ampm">{dep_ap}</span>
          <span class="flight-arrow">&nbsp;──✈──&nbsp;</span>
          <span class="time-big">{arr_t}</span><span class="time-ampm">{arr_ap}</span>
        </div>
        <div class="flight-mid">
          <div class="flight-dur dur-stop">{dur_str} &nbsp;·&nbsp; 1 Stop</div>
          <div class="flight-divider"></div>
          <div class="flight-codes">
            <span class="flight-code-bold">{combined['dep_code']}</span>
            <span>{combined['dep_city']}</span>
            <span>&nbsp;✈ E.C.H.O.&nbsp;</span>
            <span class="flight-code-bold">{combined['arr_code']}</span>
            <span>{combined['arr_city']}</span>
          </div>
        </div>
        <div class="price-panel">
          <div class="price-big">${display_price}</div>
          {savings_html}
          <div id="btn-{key}"></div>
        </div>
      </div>
      <div class="connection-note">Connection: {leg1['arr_code']} · 45 min layover</div>
      {ta_html}
    </div>"""

    st.html(html)
    selected = st.button("SELECT", key=key, use_container_width=True)

    if selected:
        l1_dep_t, l1_dep_ap = fmt_time(leg1["dep_h"], leg1["dep_m"])
        l1_arr_t, l1_arr_ap = fmt_time(leg1["arr_h"], leg1["arr_m"])
        l2_dep_t, l2_dep_ap = fmt_time(leg2["dep_h"], leg2["dep_m"])
        l2_arr_t, l2_arr_ap = fmt_time(leg2["arr_h"], leg2["arr_m"])
        if booking_mode == "charter":
            price_label = "Aircraft charter price"
            passenger_line = "Aircraft charter includes up to 19 seats"
            total = display_price
        else:
            price_label = "Price per person"
            passenger_line = f"Passengers: {passengers}"
            total = display_price * passengers

        st.success("Connecting Flight Selected ✔")

        st.markdown(f"""
        <div style="
            background: var(--section-bg);
            border: 1px solid var(--border);
            padding: 14px 18px;
            margin-top: 8px;
            border-radius: 4px;
        ">
          <div style="font-size: 0.95rem; color: var(--dark);">
            <b>LEG 1:</b> {leg1['dep_code']} → {leg1['arr_code']} &nbsp;
            {l1_dep_t}{l1_dep_ap} – {l1_arr_t}{l1_arr_ap}
          </div>

          <div style="margin-top: 4px; font-size: 0.85rem; color: var(--grey);">
            Layover: 45 min in {itin['connection']}
          </div>

          <div style="margin-top: 6px; font-size: 0.95rem; color: var(--dark);">
            <b>LEG 2:</b> {leg2['dep_code']} → {leg2['arr_code']} &nbsp;
            {l2_dep_t}{l2_dep_ap} – {l2_arr_t}{l2_arr_ap}
          </div>

          <div style="margin-top: 8px; font-size: 0.9rem;">
            <b>{price_label}:</b> ${display_price} &nbsp;&nbsp;|&nbsp;&nbsp;
            {passenger_line} &nbsp;&nbsp;|&nbsp;&nbsp;
            <b>Total:</b> ${total}
          </div>

          <div style="margin-top: 6px; font-size: 0.8rem; color: var(--grey);">
            Proceeding to checkout…
          </div>
        </div>
        """, unsafe_allow_html=True)

def render_round_trip_card(out_f, ret_f, key, booking_mode, passengers):
    out_price = out_f.get("display_price", out_f.get("price", 0))
    ret_price = ret_f.get("display_price", ret_f.get("price", 0))
    total_price = out_price + ret_price

    def flight_mini_html(f, label):
        if f.get("multi_leg"):
            leg1, leg2 = f["leg1"], f["leg2"]
            dep_t, dep_ap = fmt_time(leg1["dep_h"], leg1["dep_m"])
            arr_t, arr_ap = fmt_time(leg2["arr_h"], leg2["arr_m"])
            dur_min = flight_duration_minutes(f)
            dur_str = f"{dur_min//60}h {dur_min%60}m" if dur_min%60 else f"{dur_min//60}h"
            stops = "1 Stop"
            connection_note = f"via {leg1['arr_code']} · 45 min layover"
            dep_code = leg1["dep_code"]; arr_code = leg2["arr_code"]
        else:
            dep_t, dep_ap = fmt_time(f["dep_h"], f["dep_m"])
            arr_t, arr_ap = fmt_time(f["arr_h"], f["arr_m"])
            dur_str = f"{f['dur_h']}h {f['dur_m']}m" if f['dur_m'] else f"{f['dur_h']}h"
            stops = f["stops"]
            connection_note = ""
            dep_code = f["dep_code"]; arr_code = f["arr_code"]
        layover_html = ""
        if f.get("multi_leg"):
            layover_html = f"""
            <div class="connection-note">
              Connection: {f['connection']} · 45 min layover
            </div>
            """
        stops_cls = "dur-stop" if stops != "Nonstop" else "dur-nonstop"
        return f"""
        <div class="rt-section-label">{label}</div>
        <div class="flight-card-body">
          <div class="flight-times">
            <span class="time-big">{dep_t}</span><span class="time-ampm">{dep_ap}</span>
            <span class="flight-arrow">&nbsp;──✈──&nbsp;</span>
            <span class="time-big">{arr_t}</span><span class="time-ampm">{arr_ap}</span>
          </div>
          <div class="flight-mid">
            <div class="flight-dur {stops_cls}">{dur_str} &nbsp;·&nbsp; {stops}</div>
            <div class="flight-divider"></div>
            <div class="flight-codes">
              <span class="flight-code-bold">{dep_code}</span>
              <span>{AIRPORT_CODES.get(dep_code, dep_code)}</span>
              <span>&nbsp;✈ E.C.H.O.&nbsp;</span>
              <span>{connection_note}</span>
              <span class="flight-code-bold">{arr_code}</span>
              <span>{AIRPORT_CODES.get(arr_code, arr_code)}</span>
            </div>
          </div>
        </div>
        {layover_html}
        """

    # Check popular
    out_popular = out_f.get("popular", False)
    ret_popular = ret_f.get("popular", False)
    if out_f.get("multi_leg"):
        out_popular = out_f["leg1"].get("popular", False) or out_f["leg2"].get("popular", False)
    if ret_f.get("multi_leg"):
        ret_popular = ret_f["leg1"].get("popular", False) or ret_f["leg2"].get("popular", False)

    popular_banner = ""
    if out_popular or ret_popular:
        popular_banner = '<div class="flight-card-popular-banner">★ MOST POPULAR</div>'

    savings_html = ""
    if total_price > 1000:
        erj_cost_fh = 7450
        echo_cost_fh = 2009
        savings_pct = (1 - (echo_cost_fh / erj_cost_fh)) * 100
        savings_html = f'<span class="savings-note">E.C.H.O. est. ~{savings_pct:.0f}% lower cost than ERJ</span>'

    out_ta_html = render_time_advantage(out_f)
    ret_ta_html = render_time_advantage(ret_f)

    html = f"""
    <div class="flight-card">
      {popular_banner}
      {flight_mini_html(out_f, 'OUTBOUND')}
      {out_ta_html}
      <div class="rt-divider"></div>
      {flight_mini_html(ret_f, 'RETURN')}
      {ret_ta_html}
      <div class="rt-price-row">
        <div>
          <span class="rt-price-text">Round Trip Total: ${total_price}</span>
          &nbsp;&nbsp;{savings_html}
        </div>
      </div>
    </div>"""

    st.html(html)
    selected = st.button("SELECT", key=key, use_container_width=True)

    if selected:
        if booking_mode == "charter":
            price_label = "Aircraft charter price"
            passenger_line = "Aircraft charter includes up to 19 seats"
            final_total = total_price
        else:
            price_label = "Price per person"
            passenger_line = f"Passengers: {passengers}"
            final_total = total_price * passengers

        st.success("Round Trip Selected ✔")

        st.markdown(f"""
        <div style="
            background:#F3F4F6;
            border:1px solid #D1D5DB;
            padding:14px 18px;
            margin-top:8px;
            border-radius:4px;
        ">
          <div style="font-size:0.95rem; color:#1A1A2E;">
            <b>Price per person:</b> ${total_price} &nbsp;&nbsp;|&nbsp;&nbsp;
            <b>Passengers:</b> {passengers} &nbsp;&nbsp;|&nbsp;&nbsp;
            <b>Total:</b> ${final_total}
          </div>
          <div style="margin-top:6px; font-size:0.85rem; color:#75787b;">
            Proceeding to checkout…
          </div>
        </div>
        """, unsafe_allow_html=True)

def render_flight_days_table():
    st.markdown("""
    <div style="margin-bottom:12px">
      <span style="font-size:0.82rem;color:#75787b">
        🟢 = route operates that day &nbsp;&nbsp; 🔴 = no scheduled service
      </span>
    </div>""", unsafe_allow_html=True)

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    header = '<div class="fdays-scroll"><table class="fdays-table"><thead><tr><th>Route</th>'
    for d in days:
        header += f'<th>{d}</th>'
    header += '</tr></thead><tbody>'

    rows = ""
    for (dep, arr), operating_days in ROUTE_DAYS.items():
        dep_city = AIRPORT_CODES.get(dep, "")
        arr_city = AIRPORT_CODES.get(arr, "")
        rows += f'<tr><td><div class="fdays-route">{dep} → {arr}</div><div class="fdays-city">{dep_city} → {arr_city}</div></td>'
        for day_index in range(7):
            cls = "day-cell-on" if day_index in operating_days else "day-cell-off"
            rows += f'<td><div class="{cls}"></div></td>'
        rows += '</tr>'

    st.markdown(header + rows + '</tbody></table></div>', unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "trip_type": "Round Trip",
        "booking_mode": "Seat Booking",
        "depart_code": "CRW",
        "arrive_code": "ATL",
        "passengers": 1,
        "depart_date": date.today() + timedelta(days=10),
        "return_date": date.today() + timedelta(days=13),
        "results": None,
        "show_flight_days": False,
        "search_dep": None,
        "search_arr": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Banner ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="banner">
  <h1>✈&nbsp; ElectRAM Air</h1>
  <p>Search and book commuter charter flights across the East Coast</p>
</div>
""", unsafe_allow_html=True)

# ── Demo Disclaimer ────────────────────────────────────────────────────────────

if "show_demo_notice" not in st.session_state:
    st.session_state.show_demo_notice = True

if st.session_state.show_demo_notice:
    st.warning(
        "⚠️ **Demo Project Notice**\n\n"
        "This is a student design/demo application. ElectRAM Air is not a real airline or booking service. "
        "No flights are actually being booked or operated."
    )

    if st.button("Close notice", key="close_notice"):
        st.session_state.show_demo_notice = False
        st.rerun()

# ── Search Card ───────────────────────────────────────────────────────────────

def update_depart_code():
    st.session_state.depart_code = st.session_state.dep_select.split(" – ")[0]

def update_arrive_code():
    st.session_state.arrive_code = st.session_state.arr_select.split(" – ")[0]

def swap_airports():
    st.session_state.depart_code, st.session_state.arrive_code = (
        st.session_state.arrive_code,
        st.session_state.depart_code,
    )
    st.session_state.dep_select = airport_options[code_to_index(st.session_state.depart_code)]
    st.session_state.arr_select = airport_options[code_to_index(st.session_state.arrive_code)]

with st.container():
    st.markdown('<div class="search-card-marker"></div>', unsafe_allow_html=True)

    # Row 1a: Trip type + Passengers side by side
    r1a_cols = st.columns([1.25, 1.0])

    with r1a_cols[0]:
        st.caption("Trip Type")
        trip_type = st.radio(
            "trip_type_radio",
            ["Round Trip", "One Way"],
            index=0 if st.session_state.trip_type == "Round Trip" else 1,
            horizontal=True,
            label_visibility="collapsed",
        )
        st.session_state.trip_type = trip_type

    with r1a_cols[1]:
        st.caption("👤 Passengers")
        p_col1, p_col2, p_col3 = st.columns([1, 0.7, 1])
        with p_col1:
            if st.button("−", key="pax_minus", use_container_width=True):
                st.session_state.passengers = max(1, st.session_state.passengers - 1)
        with p_col2:
            st.markdown(
                f"<div style='text-align:center;font-size:1.1rem;font-weight:bold;padding-top:10px'>{st.session_state.passengers}</div>",
                unsafe_allow_html=True
            )
        with p_col3:
            if st.button("＋", key="pax_plus", use_container_width=True):
                st.session_state.passengers = min(9, st.session_state.passengers + 1)

    # Row 1b: Booking type + Flight Days button
    r1b_cols = st.columns([1.25, 1.0])

    with r1b_cols[0]:
        st.caption("Booking Type")
        booking_mode = st.radio(
            "booking_mode_radio",
            ["Seat Booking", "Charter Aircraft"],
            index=0 if st.session_state.booking_mode == "Seat Booking" else 1,
            horizontal=True,
            label_visibility="collapsed",
        )
        st.session_state.booking_mode = booking_mode

    with r1b_cols[1]:
        st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
        if st.button("📅 Flight Days", use_container_width=True):
            st.session_state.show_flight_days = not st.session_state.show_flight_days
            st.rerun()

    # Row 2: Airports and dates
    airport_options = [f"{code} – {city}" for code, city in AIRPORTS]
    airport_codes_list = [code for code, _ in AIRPORTS]

    def code_to_index(code):
        return airport_codes_list.index(code) if code in airport_codes_list else 0

    r2_cols = st.columns([2.4, 0.4, 2.4])

    with r2_cols[0]:
        st.caption("Departing")
        dep_sel = st.selectbox(
            "dep_sel", airport_options,
            index=code_to_index(st.session_state.depart_code),
            label_visibility="collapsed",
            key="dep_select",
            on_change=update_depart_code
        )

    with r2_cols[1]:
        st.caption("&nbsp;")
        st.button(
            "⇄",
            key="swap_btn",
            use_container_width=True,
            on_click=swap_airports
        )

    with r2_cols[2]:
        st.caption("Arriving")
        arr_sel = st.selectbox(
            "arr_sel", airport_options,
            index=code_to_index(st.session_state.arrive_code),
            label_visibility="collapsed",
            key="arr_select",
            on_change=update_arrive_code
        )

    is_round = st.session_state.trip_type == "Round Trip"
    date_cols = st.columns(2)

    with date_cols[0]:
        st.caption("Departure Date")
        depart_date = st.date_input(
            "depart_date_input",
            value=st.session_state.depart_date,
            min_value=date.today(),
            label_visibility="collapsed",
            key="dep_date_input"
        )
        st.session_state.depart_date = depart_date

    with date_cols[1]:
        st.caption("Return Date" if is_round else "Return Date (N/A)")
        return_date = st.date_input(
            "return_date_input",
            value=st.session_state.return_date,
            min_value=depart_date,
            label_visibility="collapsed",
            key="ret_date_input",
            disabled=not is_round
        )
        if is_round:
            st.session_state.return_date = return_date

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    find_clicked = st.button("✈  FIND FLIGHTS", use_container_width=True, key="find_flights_btn")

    st.markdown('</div>', unsafe_allow_html=True)

# ── Flight Days Panel ─────────────────────────────────────────────────────────
if st.session_state.get("show_flight_days", False):
    st.markdown("""
    <div style="background:#861F41;color:white;padding:14px 24px;margin-bottom:1rem;border-radius:6px">
      <span style="font-family:Georgia,serif;font-size:1.4rem;font-weight:bold">✈&nbsp; Flight Days</span>
    </div>""", unsafe_allow_html=True)
    render_flight_days_table()
    st.divider()

# ── Search & Results ──────────────────────────────────────────────────────────
if find_clicked:
    dep = st.session_state.depart_code
    arr = st.session_state.arrive_code
    if dep == arr:
        st.warning("⚠️ Departure and arrival airports cannot be the same.")
    elif st.session_state.passengers < 1:
        st.warning("⚠️ Please add at least 1 passenger.")
    else:
        st.session_state.search_dep = dep
        st.session_state.search_arr = arr
        st.session_state.results = True

if st.session_state.results and st.session_state.search_dep:
    dep = st.session_state.search_dep
    arr = st.session_state.search_arr
    dep_city = AIRPORT_CODES.get(dep, dep)
    arr_city = AIRPORT_CODES.get(arr, arr)
    booking_mode_key = "seat" if st.session_state.booking_mode == "Seat Booking" else "charter"
    passengers = st.session_state.passengers
    is_round = st.session_state.trip_type == "Round Trip"
    dep_dt = datetime.combine(st.session_state.depart_date, datetime.min.time())
    ret_dt = datetime.combine(st.session_state.return_date, datetime.min.time())
    def fmt_display_date(d):
        return d.strftime("%a, %b ") + str(d.day)

    dep_str = fmt_display_date(st.session_state.depart_date)
    ret_str = fmt_display_date(st.session_state.return_date)

    outbound_flights = random_flights(dep, arr, dep_dt, 5)
    outbound_flights = apply_booking_mode(outbound_flights, booking_mode_key)

    if is_round:
        return_flights = random_flights(arr, dep, ret_dt, 5)
        return_flights = apply_booking_mode(return_flights, booking_mode_key)

        # Header
        st.markdown(f"""
        <div class="results-header">
          <span class="results-title">{dep} &nbsp;✈&nbsp; {arr} &nbsp;✈&nbsp; {dep}</span>
          <span class="results-sub">Round Trip &nbsp;·&nbsp; {dep_str} – {ret_str} &nbsp;·&nbsp; {passengers} passenger{"s" if passengers>1 else ""}</span>
        </div>""", unsafe_allow_html=True)

        st.markdown(f'<div class="section-header">ROUND TRIP &nbsp;·&nbsp; {dep} → {arr} &nbsp;·&nbsp; {dep_str} &nbsp;&nbsp;|&nbsp;&nbsp; {arr} → {dep} &nbsp;·&nbsp; {ret_str}</div>', unsafe_allow_html=True)

        if not outbound_flights or not return_flights:
            out_days = operating_days_text(dep, arr)
            ret_days = operating_days_text(arr, dep)

            message = f"No round trip flights are available for the selected dates.\n\n"

            if not outbound_flights and out_days:
                message += f"Outbound {dep} → {arr} operates on: **{out_days}**.\n\n"

            if not return_flights and ret_days:
                message += f"Return {arr} → {dep} operates on: **{ret_days}**."

            st.warning(message)
        else:
            for i, (out_f, ret_f) in enumerate(zip(outbound_flights, return_flights)):
                render_round_trip_card(out_f, ret_f, f"rt_select_{i}", booking_mode_key, passengers)

    else:
        # One way header
        st.markdown(f"""
        <div class="results-header">
          <span class="results-title">{dep} &nbsp;✈&nbsp; {arr}</span>
          <span class="results-sub">{dep_city} → {arr_city} &nbsp;·&nbsp; {dep_str} &nbsp;·&nbsp; {passengers} passenger{"s" if passengers>1 else ""}</span>
        </div>""", unsafe_allow_html=True)

        st.markdown(f'<div class="section-header">OUTBOUND &nbsp;·&nbsp; {dep} → {arr} &nbsp;·&nbsp; {dep_str}</div>', unsafe_allow_html=True)

        if not outbound_flights:
            days_text = operating_days_text(dep, arr)

            if days_text:
                st.warning(
                    f"No flights operate for {dep} → {arr} on {dep_str}.\n\n"
                    f"Available flight days: **{days_text}**."
                )
            else:
                st.info(f"No flights currently available for {dep} → {arr}.")
        else:
            for i, f in enumerate(outbound_flights):
                if f.get("multi_leg"):
                    render_multileg_card(f, f"ml_select_{i}", booking_mode_key, passengers)
                else:
                    render_flight_card(f, f"ow_select_{i}", booking_mode_key, passengers)