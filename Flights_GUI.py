import tkinter as tk
from tkinter import messagebox
from datetime import date, datetime, timedelta
import calendar
import math
import copy


# ── Palette ───────────────────────────────────────────────────────────────────
BG         = "#F7F8FA"
WHITE      = "#FFFFFF"
RED        = "#C8102E"
RED_DARK   = "#A00D24"
RED_LIGHT  = "#FFF1F3"
DARK       = "#1A1A2E"
GREY       = "#75787b"
LIGHT_GREY = "#E5E7EB"
BORDER     = "#D1D5DB"
SECTION_BG = "#F3F4F6"
GOLD       = "#B8860B"
MAROON     = "#861F41"
ORANGE     = "#E5751F"

_SANS  = "Segoe UI"
_SERIF = "Georgia"

FONT_TITLE   = (_SERIF, 26, "bold")
FONT_LABEL   = (_SANS,  9)
FONT_CODE    = (_SANS,  32, "bold")
FONT_CITY    = (_SANS,  10)
FONT_BTN     = (_SANS,  12, "bold")
FONT_SMALL   = (_SANS,  9)
FONT_CTRL    = (_SANS,  11)
FONT_TIME    = (_SERIF, 22, "bold")
FONT_AMPM    = (_SERIF, 12, "bold")
FONT_PRICE   = (_SERIF, 20, "bold")
FONT_ROUTE   = (_SANS,  10, "bold")
FONT_DETAIL  = (_SANS,  9)
FONT_TAG     = (_SANS,  8,  "bold")

# -----------------------------
# AIRPORT DATABASE
# -----------------------------

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

AIRCRAFT = ["E.C.H.O."]

# -----------------------------
# ROUTE DATABASE
# Time is block time, not pure cruise time
# -----------------------------

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

    # Additional connector routes
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
    ("CRW", "ATL"): [0, 1, 2, 3, 4, 5, 6],  # daily
    ("CRW", "CLT"): [0, 1, 2, 3, 4, 5, 6],

    ("CRW", "ROA"): [0, 2, 4],       # Mon/Wed/Fri
    ("CRW", "TRI"): [1, 3, 5],       # Tue/Thu/Sat
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

def get_route(dep, arr):
    """
    Finds a route in either direction.
    This lets CRW -> ATL and ATL -> CRW both work.
    """
    if (dep, arr) in ROUTES:
        return ROUTES[(dep, arr)]

    if (arr, dep) in ROUTES:
        return ROUTES[(arr, dep)]

    return None

def find_connection(dep, arr, date):
    """
    Finds the best 1-stop route: dep → mid → arr.
    Chooses the shortest total travel time.
    """
    valid_connections = []

    for mid, city in AIRPORTS:
        if mid == dep or mid == arr:
            continue

        first_route = get_route(dep, mid)
        second_route = get_route(mid, arr)

        if not first_route or not second_route:
            continue

        if not route_operates_on_date(dep, mid, date):
            continue

        if not route_operates_on_date(mid, arr, date):
            continue

        layover_minutes = 45

        total_minutes = (
            first_route["dur_h"] * 60 + first_route["dur_m"] +
            layover_minutes +
            second_route["dur_h"] * 60 + second_route["dur_m"]
        )

        price1 = flight_price(first_route["dur_h"], first_route["dur_m"], "seat")
        price2 = flight_price(second_route["dur_h"], second_route["dur_m"], "seat")
        total_price = price1 + price2

        valid_connections.append({
            "mid": mid,
            "first_route": first_route,
            "second_route": second_route,
            "total_minutes": total_minutes,
            "total_price": total_price,
        })

    if not valid_connections:
        return None

    # Best = shortest total travel time
    best = min(valid_connections, key=lambda x: x["total_minutes"])

    return best["mid"], best["first_route"], best["second_route"]

def route_operates_on_date(dep, arr, date):
    """
    Checks whether a route operates on the selected calendar date.
    Monday = 0, Sunday = 6.
    """

    if (dep, arr) in ROUTE_DAYS:
        operating_days = ROUTE_DAYS[(dep, arr)]
    elif (arr, dep) in ROUTE_DAYS:
        operating_days = ROUTE_DAYS[(arr, dep)]
    else:
        return False

    return date.weekday() in operating_days

def add_minutes(hour, minute, duration_h, duration_m):
    """
    Adds duration to departure time and returns arrival hour/minute.
    """
    total_minutes = hour * 60 + minute + duration_h * 60 + duration_m
    arr_hour = (total_minutes // 60) % 24
    arr_min = total_minutes % 60
    return arr_hour, arr_min

def flight_price(h, m, booking_mode="seat"):
    '''
    Calculates flight price based on duration (h hours and m minutes) and other factors.
    Do not remove, adjust this to fit the flight code for when its not hardcoded.
    Multipy the results by 2 if the trip type is round trip (not implemented in the hardcoded
    version, but should be in the random version).

    Parameters:
        h (int): Flight duration hours
        m (int): Flight duration minutes

    returns:
        rate_seat (float): Price per seat
        rate_ac (float): Price for whole aircraft
    '''
    # Sample price function based $/FH (flight hour) with some extra costs
    fh = h + m/60
    cost_fh = 1209 # Cost for flight hour
    fluff = 300
    cost_seat_hour = (cost_fh + fluff)/19 # Cost per seat (based on 19-seat E.C.H.O. aircraft)
    
    # Adjust based on route popularity, demand, and other competitors
    desired_profit = 50
    
    # Whole rates
    rate_seat_whole = fh * cost_seat_hour + desired_profit # Price per seat
    rate_ac_whole = (cost_fh + fluff) * fh + desired_profit # Price for whole aircraft

    # Round to the nearest XX9 dollars
    rate_seat = math.ceil(rate_seat_whole / 10) * 10 - 1
    rate_ac = math.ceil(rate_ac_whole / 10) * 10 - 1
    
    if booking_mode == "charter":
        rate_ac += 500 # Additional fee for charter booking
        return rate_ac

    return rate_seat

def generate_flights(dep, arr, date, count=3):
    """
    Generates flight listings from the route database
    and prices them using flight_price().
    """
    route = get_route(dep, arr)

    if route is None:
        return []

    if not route_operates_on_date(dep, arr, date):
        return []

    departure_times = [
        (9, 0),
        (11, 0),
        (13, 0),
        (15, 0),
        (17, 0),
    ]

    flights = []

    for i, (dep_h, dep_m) in enumerate(departure_times[:count]):
        arr_h, arr_m = add_minutes(
            dep_h,
            dep_m,
            route["dur_h"],
            route["dur_m"]
        )

        # Use your $/FH price model
        seat_price = flight_price(route["dur_h"], route["dur_m"], "seat")
        aircraft_price = flight_price(route["dur_h"], route["dur_m"], "charter")

        # Optional demo variation
        if i == 0:
            seat_price += 20
        elif i == 2:
            seat_price -= 10

        flights.append({
            "dep_h": dep_h,
            "dep_m": dep_m,
            "arr_h": arr_h,
            "arr_m": arr_m,
            "dur_h": route["dur_h"],
            "dur_m": route["dur_m"],
            "stops": "Nonstop",
            "aircraft": "E.C.H.O.",
            "price": seat_price,
            "aircraft_price": aircraft_price,
            "seats_left": 2 if i == 0 else None,
            "popular": True if i == 1 else False,
            "dep_code": dep,
            "arr_code": arr,
            "dep_city": AIRPORT_CODES.get(dep, dep),
            "arr_city": AIRPORT_CODES.get(arr, arr),
        })

    return flights

def generate_multileg_flights(dep, arr, date, count=3):
    """
    Returns direct flights if available.
    If not, tries to create 1-stop connecting itineraries.
    """
    direct = generate_flights(dep, arr, date, count)

    if direct:
        return direct, "direct"

    connection = find_connection(dep, arr, date)

    if connection is None:
        return [], "none"

    mid, first_route, second_route = connection

    departure_times = [
        (8, 0),
        (11, 0),
        (14, 0),
    ]

    itineraries = []

    for i, (dep_h, dep_m) in enumerate(departure_times[:count]):
        # First leg
        mid_arr_h, mid_arr_m = add_minutes(
            dep_h,
            dep_m,
            first_route["dur_h"],
            first_route["dur_m"]
        )

        # Layover, 45 minutes
        second_dep_h, second_dep_m = add_minutes(
            mid_arr_h,
            mid_arr_m,
            0,
            45
        )

        # Second leg
        final_arr_h, final_arr_m = add_minutes(
            second_dep_h,
            second_dep_m,
            second_route["dur_h"],
            second_route["dur_m"]
        )

        price1 = flight_price(first_route["dur_h"], first_route["dur_m"], "seat")
        aircraft_price1 = flight_price(first_route["dur_h"], first_route["dur_m"], "charter")

        price2 = flight_price(second_route["dur_h"], second_route["dur_m"], "seat")
        aircraft_price2 = flight_price(second_route["dur_h"], second_route["dur_m"], "charter")

        itineraries.append({
            "multi_leg": True,
            "connection": mid,

            "leg1": {
                "dep_h": dep_h,
                "dep_m": dep_m,
                "arr_h": mid_arr_h,
                "arr_m": mid_arr_m,
                "dur_h": first_route["dur_h"],
                "dur_m": first_route["dur_m"],
                "stops": "Nonstop",
                "aircraft": "E.C.H.O.",
                "price": price1,
                "aircraft_price": aircraft_price1,
                "seats_left": 2 if i == 0 else None,
                "popular": True if i == 1 else False,
                "dep_code": dep,
                "arr_code": mid,
                "dep_city": AIRPORT_CODES.get(dep, dep),
                "arr_city": AIRPORT_CODES.get(mid, mid),
            },

            "leg2": {
                "dep_h": second_dep_h,
                "dep_m": second_dep_m,
                "arr_h": final_arr_h,
                "arr_m": final_arr_m,
                "dur_h": second_route["dur_h"],
                "dur_m": second_route["dur_m"],
                "stops": "Nonstop",
                "aircraft": "E.C.H.O.",
                "price": price2,
                "aircraft_price": aircraft_price2,
                "seats_left": 2 if i == 0 else None,
                "popular": True if i == 1 else False,
                "dep_code": mid,
                "arr_code": arr,
                "dep_city": AIRPORT_CODES.get(mid, mid),
                "arr_city": AIRPORT_CODES.get(arr, arr),
            },

            "price": price1 + price2,
        })

    return itineraries, "connection"

def random_flights(dep, arr, date, count=5):
    flights, route_type = generate_multileg_flights(dep, arr, date, count)
    return flights

def fmt_time(h, m):
    ampm = "AM" if h < 12 else "PM"
    return f"{h % 12 or 12}:{m:02d}", ampm

def format_route_days(days):
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    if days == [0, 1, 2, 3, 4, 5, 6]:
        return "Daily"

    return ", ".join(day_names[d] for d in days)

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
        return (
            f["leg1"]["dur_h"] * 60 + f["leg1"]["dur_m"] +
            45 +
            f["leg2"]["dur_h"] * 60 + f["leg2"]["dur_m"]
        )

    return f["dur_h"] * 60 + f["dur_m"]


def route_drive_minutes(f):
    if f.get("multi_leg"):
        leg1_drive = get_drive_time(f["leg1"]["dep_code"], f["leg1"]["arr_code"])
        leg2_drive = get_drive_time(f["leg2"]["dep_code"], f["leg2"]["arr_code"])

        if not leg1_drive or not leg2_drive:
            return None

        return time_to_minutes(leg1_drive) + time_to_minutes(leg2_drive)

    drive = get_drive_time(f["dep_code"], f["arr_code"])

    if not drive:
        return None

    return time_to_minutes(drive)


# ── Reusable Widgets ──────────────────────────────────────────────────────────

class HoverButton(tk.Button):
    def __init__(self, master, bg, fg, hover_bg, hover_fg, **kw):
        super().__init__(master, bg=bg, fg=fg, activebackground=hover_bg,
                         activeforeground=hover_fg, relief="flat", cursor="hand2", **kw)
        self._bg, self._fg = bg, fg
        self._hbg, self._hfg = hover_bg, hover_fg
        self.bind("<Enter>", lambda e: self.config(bg=self._hbg, fg=self._hfg))
        self.bind("<Leave>", lambda e: self.config(bg=self._bg,  fg=self._fg))


class CalendarPicker(tk.Toplevel):
    def __init__(self, parent, initial_date, callback):
        super().__init__(parent)
        self.callback  = callback
        self._selected = initial_date
        self._viewing  = datetime(initial_date.year, initial_date.month, 1)
        self.overrideredirect(True)
        self.configure(bg=WHITE)
        self.resizable(False, False)
        self._build()
        x = parent.winfo_rootx()
        y = parent.winfo_rooty() + parent.winfo_height() + 4
        self.geometry(f"+{x}+{y}")
        self.grab_set()

    def _build(self):
        for w in self.winfo_children(): w.destroy()
        outer = tk.Frame(self, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        outer.pack()
        hdr = tk.Frame(outer, bg=RED, pady=8); hdr.pack(fill="x")
        tk.Button(hdr, text="◀", bg=RED, fg=WHITE, relief="flat",
                  font=(_SANS, 12), command=self._prev,
                  cursor="hand2", activebackground=RED_DARK, activeforeground=WHITE
                  ).pack(side="left", padx=8)
        tk.Label(hdr, text=self._viewing.strftime("%B  %Y"),
                 bg=RED, fg=WHITE, font=(_SANS, 11, "bold")).pack(side="left", expand=True)
        tk.Button(hdr, text="▶", bg=RED, fg=WHITE, relief="flat",
                  font=(_SANS, 12), command=self._next,
                  cursor="hand2", activebackground=RED_DARK, activeforeground=WHITE
                  ).pack(side="right", padx=8)
        days_f = tk.Frame(outer, bg=WHITE, pady=4); days_f.pack(fill="x", padx=8)
        for i, d in enumerate(["Su","Mo","Tu","We","Th","Fr","Sa"]):
            tk.Label(days_f, text=d, width=3, bg=WHITE, fg=GREY, font=FONT_SMALL
                     ).grid(row=0, column=i, padx=2)
        grid_f = tk.Frame(outer, bg=WHITE, padx=8, pady=4); grid_f.pack()
        today = datetime.today().date()
        for r, week in enumerate(calendar.monthcalendar(self._viewing.year, self._viewing.month)):
            for c, day in enumerate(week):
                if day == 0:
                    tk.Label(grid_f, text="", width=3, bg=WHITE).grid(row=r, column=c, padx=2, pady=1)
                    continue
                d       = datetime(self._viewing.year, self._viewing.month, day)
                is_sel  = d.date() == self._selected.date()
                is_past = d.date() < today
                tk.Button(grid_f, text=str(day), width=3,
                          bg=ORANGE if is_sel else WHITE,
                          fg=WHITE if is_sel else (LIGHT_GREY if is_past else DARK),
                          relief="flat", font=FONT_SMALL,
                          cursor="hand2" if not is_past else "arrow",
                          activebackground=RED_LIGHT, activeforeground=RED,
                          command=(lambda dt=d: self._pick(dt)) if not is_past else None
                          ).grid(row=r, column=c, padx=2, pady=1)
        tk.Button(outer, text="Close", bg=BG, fg=GREY, relief="flat",
                  font=FONT_SMALL, cursor="hand2", command=self.destroy).pack(pady=6)

    def _prev(self):
        m, y = self._viewing.month - 1, self._viewing.year
        if m == 0: m, y = 12, y - 1
        self._viewing = datetime(y, m, 1); self._build()

    def _next(self):
        m, y = self._viewing.month + 1, self._viewing.year
        if m == 13: m, y = 1, y + 1
        self._viewing = datetime(y, m, 1); self._build()

    def _pick(self, dt):
        self.callback(dt); self.destroy()


class AirportDropdown(tk.Toplevel):
    def __init__(self, parent, current_code, callback):
        super().__init__(parent)
        self.callback = callback
        self.overrideredirect(True)
        self.configure(bg=WHITE)
        self.resizable(False, False)
        x = parent.winfo_rootx()
        y = parent.winfo_rooty() + parent.winfo_height()
        self.geometry(f"280x320+{x}+{y}")
        outer = tk.Frame(self, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        outer.pack(fill="both", expand=True)
        sv = tk.StringVar()
        sv.trace_add("write", lambda *_: self._filter(sv.get()))
        tk.Entry(outer, textvariable=sv, font=FONT_CTRL, relief="flat",
                 bg=BG, fg=DARK, insertbackground=RED).pack(fill="x", padx=8, pady=8, ipady=6)
        self._list_frame = tk.Frame(outer, bg=WHITE)
        self._list_frame.pack(fill="both", expand=True, padx=4)
        self._render(AIRPORTS)
        self.grab_set()

    def _filter(self, text):
        t = text.lower()
        self._render([(c, ct) for c, ct in AIRPORTS if t in c.lower() or t in ct.lower()])

    def _render(self, items):
        for w in self._list_frame.winfo_children(): w.destroy()
        canvas = tk.Canvas(self._list_frame, bg=WHITE, highlightthickness=0)
        sb = tk.Scrollbar(self._list_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y"); canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=WHITE)
        canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        for code, city in items:
            row = tk.Frame(inner, bg=WHITE, cursor="hand2"); row.pack(fill="x", pady=1)
            tk.Label(row, text=code, font=(_SANS, 11, "bold"),
                     bg=WHITE, fg=RED, width=5, anchor="w").pack(side="left", padx=6)
            tk.Label(row, text=city, font=FONT_CITY, bg=WHITE, fg=DARK, anchor="w").pack(side="left")
            for w in [row] + list(row.winfo_children()):
                w.bind("<Enter>",    lambda e, r=row: r.config(bg=RED_LIGHT))
                w.bind("<Leave>",    lambda e, r=row: r.config(bg=WHITE))
                w.bind("<Button-1>", lambda e, c=code: (self.callback(c), self.destroy()))


# ── Flight Result Row ─────────────────────────────────────────────────────────

def build_flight_row(parent, f, on_book, show_price=True, show_popular=True, show_time=True):
    dep_t, dep_ap = fmt_time(f["dep_h"], f["dep_m"])
    arr_t, arr_ap = fmt_time(f["arr_h"], f["arr_m"])

    outer = tk.Frame(parent, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
    outer.pack(fill="x", pady=(0, 18))

    # "MOST POPULAR" banner
    if f["popular"] and show_popular:
        banner = tk.Frame(outer, bg=SECTION_BG); banner.pack(fill="x")
        tk.Label(banner, text="★ MOST POPULAR", font=FONT_TAG,
                 bg=SECTION_BG, fg=GOLD, anchor="e", padx=12, pady=4).pack(side="right")

    row = tk.Frame(outer, bg=WHITE, pady=14); row.pack(fill="x")

    # Times
    times_f = tk.Frame(row, bg=WHITE, width=280);  times_f.pack(side="left", padx=(18, 0))
    times_f.pack_propagate(True)

    def time_block(par, t, ap):
        b = tk.Frame(par, bg=WHITE); b.pack(side="left")
        tk.Label(b, text=t,  font=FONT_TIME, bg=WHITE, fg=DARK).pack(side="left", anchor="s")
        tk.Label(b, text=ap, font=FONT_AMPM, bg=WHITE, fg=GREY).pack(side="left", anchor="s", pady=(0, 3))

    time_block(times_f, dep_t, dep_ap)
    tk.Label(times_f, text="  ──✈──  ", font=(_SANS, 10),
              bg=WHITE, fg=GREY).pack(side="left", pady=(8, 0))
    time_block(times_f, arr_t, arr_ap)

    # Route details
    mid = tk.Frame(row, bg=WHITE, width=200); mid.pack(side="left", padx=18, fill="x")
    mid.pack_propagate(True)
    dur_str   = f"{f['dur_h']}h {f['dur_m']}m" if f['dur_m'] else f"{f['dur_h']}h"
    stops_col = ORANGE if f["stops"] != "Nonstop" else GREY
    tk.Label(
        mid,
        text=f"                               {dur_str}  ·  {f['stops']}",
        font=(_SANS, 10, "bold"),
        bg=WHITE,
        fg=stops_col
    ).pack(anchor="w")

    if "subline" in f:
        tk.Label(
            mid,
            text=f"                               {f['subline']}",
            font=FONT_DETAIL,
            bg=WHITE,
            fg=GREY
        ).pack(anchor="w", pady=(2, 0))
    tk.Frame(mid, bg=LIGHT_GREY, height=2).pack(fill="x", pady=4)
    codes_f = tk.Frame(mid, bg=WHITE); codes_f.pack(fill="x")
    tk.Label(codes_f, text=f["dep_code"], font=FONT_ROUTE, bg=WHITE, fg=DARK).pack(side="left")
    tk.Label(codes_f, text=f["dep_city"], font=FONT_DETAIL, bg=WHITE, fg=GREY).pack(side="left", padx=(3,0))
    tk.Label(codes_f, text=f"       ✈ {f['aircraft']}       ", font=FONT_DETAIL, bg=WHITE, fg=GREY).pack(side="left", expand=True)
    arr_f = tk.Frame(mid, bg=WHITE); arr_f.pack(fill="x")
    tk.Label(codes_f, text=f["arr_code"], font=FONT_ROUTE, bg=WHITE, fg=DARK).pack(side="right")
    tk.Label(codes_f, text=f["arr_city"], font=FONT_DETAIL, bg=WHITE, fg=GREY).pack(side="left", padx=(3,0))

    if show_time:
        build_time_advantage(outer, f)

    # Price panel
    if show_price:
        price_panel = tk.Frame(row, bg=SECTION_BG, padx=18, pady=10,
                               highlightbackground=BORDER, highlightthickness=1)
        price_panel.pack(side="right", padx=18, fill="y")

        price_row = tk.Frame(price_panel, bg=SECTION_BG)
        price_row.pack(anchor="e")

        display_price = f.get("display_price", f["price"])

        tk.Label(price_row, text=f"${display_price}", font=FONT_PRICE,
                 bg=SECTION_BG, fg=DARK).pack(side="left")

        tk.Label(price_row, text=" ▶", font=(_SANS, 10),
                 bg=SECTION_BG, fg=ORANGE).pack(side="left", pady=(4,0))

        if f["seats_left"]:
            tk.Label(price_panel,
                     text=f"{f['seats_left']} seat{'s' if f['seats_left']>1 else ''} left",
                     font=FONT_DETAIL, bg=SECTION_BG, fg=ORANGE).pack(anchor="e", pady=(2, 6))
        else:
            tk.Label(price_panel, text=" ", font=FONT_DETAIL,
                     bg=SECTION_BG).pack(pady=(2, 6))

        HoverButton(price_panel, bg=ORANGE, fg=WHITE,
                    hover_bg=MAROON, hover_fg=WHITE,
                    text="SELECT", font=(_SANS, 9, "bold"),
                    command=lambda: on_book(f), padx=14, pady=5).pack(anchor="e")

def build_round_trip_row(parent, outbound, ret, on_book):
    outer = tk.Frame(parent, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
    outer.pack(fill="x", pady=(0, 18))

    # Shared MOST POPULAR banner
    outbound_popular = outbound.get("popular", False)
    ret_popular = ret.get("popular", False)

    if outbound.get("multi_leg"):
        outbound_popular = outbound["leg1"].get("popular", False) or outbound["leg2"].get("popular", False)

    if ret.get("multi_leg"):
        ret_popular = ret["leg1"].get("popular", False) or ret["leg2"].get("popular", False)

    if outbound_popular or ret_popular:
        banner = tk.Frame(outer, bg=SECTION_BG)
        banner.pack(fill="x")

        tk.Label(
            banner,
            text="★  MOST POPULAR",
            font=FONT_TAG,
            bg=SECTION_BG,
            fg=GOLD,
            anchor="e",
            padx=12,
            pady=4
        ).pack(side="right")

    # Outbound section
    tk.Label(
        outer,
        text="OUTBOUND",
        font=FONT_TAG,
        bg=SECTION_BG,
        fg=GREY,
        anchor="w",
        padx=18,
        pady=6
    ).pack(fill="x")

    if outbound.get("multi_leg"):
        build_multileg_row(outer, outbound, lambda f: None, show_price=False)
    else:
        build_flight_row(
            outer,
            outbound,
            lambda f: None,
            show_price=False,
            show_popular=False
        )

    # Divider
    tk.Frame(outer, bg=DARK, height=1).pack(fill="x", pady=2)

    # Return section
    tk.Label(
        outer,
        text="RETURN",
        font=FONT_TAG,
        bg=SECTION_BG,
        fg=GREY,
        anchor="w",
        padx=18,
        pady=6
    ).pack(fill="x")

    if ret.get("multi_leg"):
        build_multileg_row(outer, ret, lambda f: None, show_price=False)
    else:
        build_flight_row(
            outer,
            ret,
            lambda f: None,
            show_price=False,
            show_popular=False
        )

    # Total price
    outbound_price = outbound.get("display_price", outbound["price"])
    ret_price = ret.get("display_price", ret["price"])
    total_price = outbound_price + ret_price

    price_panel = tk.Frame(
        outer,
        bg=SECTION_BG,
        padx=18,
        pady=10,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    price_panel.pack(fill="x", padx=18, pady=10)

    tk.Label(
        price_panel,
        text=f"Round Trip Total: ${total_price}",
        font=FONT_PRICE,
        bg=SECTION_BG,
        fg=DARK
    ).pack(side="left")

    if total_price > 1000:  # rough way to only show during charter pricing
        erj_cost_fh = 7450
        echo_cost_fh = 2009

        savings_pct = (1 - (echo_cost_fh / erj_cost_fh)) * 100

        tk.Label(
            price_panel,
            text=f"E.C.H.O. estimated operating cost is ~{savings_pct:.0f}% lower than an ERJ on this route.",
            font=FONT_ROUTE,
            bg=SECTION_BG,
            fg=GREY
        ).pack(side="left", padx=(20, 0))

    HoverButton(
        price_panel,
        bg=ORANGE,
        fg=WHITE,
        hover_bg=MAROON,
        hover_fg=WHITE,
        text="SELECT ROUND TRIP",
        font=(_SANS, 9, "bold"),
        command=lambda: on_book(outbound, ret),
        padx=14,
        pady=5
    ).pack(side="right")

def build_multileg_row(parent, itinerary, on_book, show_price=True):
    leg1 = itinerary["leg1"]
    leg2 = itinerary["leg2"]

    combined = {
        "dep_h": leg1["dep_h"],
        "dep_m": leg1["dep_m"],
        "arr_h": leg2["arr_h"],
        "arr_m": leg2["arr_m"],
        "dur_h": flight_duration_minutes(itinerary) // 60,
        "dur_m": flight_duration_minutes(itinerary) % 60,
        "stops": "1 Stop",
        # "subline": f"Connection: {leg1['arr_code']} · 45 min layover · Saves {minutes_to_str(route_drive_minutes(itinerary) - flight_duration_minutes(itinerary))}",
        "aircraft": "E.C.H.O.",
        "price": itinerary.get("display_price", itinerary["price"]),
        "display_price": itinerary.get("display_price", itinerary["price"]),
        "seats_left": None,
        "popular": leg1.get("popular", False) or leg2.get("popular", False),
        "dep_code": leg1["dep_code"],
        "arr_code": leg2["arr_code"],
        "dep_city": leg1["dep_city"],
        "arr_city": leg2["arr_city"],
    }

    build_flight_row(
        parent,
        combined,
        lambda f: on_book(itinerary),
        show_price=show_price,
        show_popular=True,
        show_time=False
    )

    outer = tk.Frame(parent, bg=WHITE)
    outer.pack(fill="x", pady=(0, 18))

    tk.Label(
        outer,
        text=f"Connection: {leg1['arr_code']} · 45 min layover",
        font=FONT_DETAIL,
        bg=WHITE,
        fg=GREY,
        anchor="w",
        padx=24,
        pady=2
    ).pack(fill="x")

    build_time_advantage(outer, itinerary)

def build_time_advantage(parent, flight):
    drive_minutes = route_drive_minutes(flight)

    if drive_minutes is None:
        return

    fly_minutes = flight_duration_minutes(flight)
    saved_minutes = drive_minutes - fly_minutes

    if saved_minutes <= 0:
        return

    box = tk.Frame(
        parent,
        bg=RED_LIGHT,
        padx=16,
        pady=8,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    box.pack(fill="x", padx=18, pady=(4, 10))

    tk.Label(
        box,
        text="Time Advantage",
        font=FONT_TAG,
        bg=RED_LIGHT,
        fg=MAROON
    ).pack(anchor="w")

    tk.Label(
        box,
        text=f"Drive: {minutes_to_str(drive_minutes)}   ·   Flight: {minutes_to_str(fly_minutes)}   ·   Time saved: {minutes_to_str(saved_minutes)}",
        font=FONT_DETAIL,
        bg=RED_LIGHT,
        fg=DARK
    ).pack(anchor="w")

# ── Main Application ──────────────────────────────────────────────────────────

class FlightBookingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        # Window Title Bar
        self.title("ElectRAM – Flight Search")
        self.configure(bg=BG)
        self.resizable(True, True)

        self.trip_type   = tk.StringVar(value="round")
        # Defualt window airport codes.
        self.depart_code = tk.StringVar(value="CRW")
        self.arrive_code = tk.StringVar(value="ATL")
        # Default passenger and pet counts (pets not implemented)
        self.passengers  = tk.IntVar(value=1)
        # self.pets        = tk.IntVar(value=0)
        self.booking_mode = tk.StringVar(value="seat")  # "seat" or "charter"
        # Default dates (10 days from today for departure, 13 days for return)
        self.depart_date = datetime.today() + timedelta(days=10)
        self.return_date = datetime.today() + timedelta(days=13)

        self._build_ui()
        self.update_idletasks()
        self.geometry("960x560")

    def _build_ui(self):
        # Banner
        banner = tk.Frame(self, bg=MAROON, pady=18); banner.pack(fill="x")
        # Banner headline and subtitle text
        tk.Label(banner, text="✈  ElectRAM Air", font=FONT_TITLE, bg=MAROON, fg=WHITE).pack()
        tk.Label(banner, text="Search and book commuter charter flights across the East Coast",
                 font=FONT_SMALL, bg=MAROON, fg=GREY).pack(pady=(2,0))

        # Scrollable container
        outer = tk.Frame(self, bg=BG); outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        vsb    = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y"); canvas.pack(side="left", fill="both", expand=True)

        self._canvas = canvas
        self._inner  = tk.Frame(canvas, bg=BG)
        self._cwin   = canvas.create_window((0,0), window=self._inner, anchor="nw")
        self._inner.bind("<Configure>",
                         lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(self._cwin, width=e.width))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Search card
        card = tk.Frame(self._inner, bg=WHITE, padx=28, pady=22,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", padx=30, pady=20)

        top = tk.Frame(card, bg=WHITE); top.pack(fill="x", pady=(0,16))
        right_controls = tk.Frame(top, bg=WHITE); right_controls.pack(side="right")
        self._trip_buttons(top)
        tk.Frame(top, bg=LIGHT_GREY, width=1).pack(side="left", fill="y", padx=16)
        self._pax_control(top, "👤 Passengers", self.passengers, 9)
        # self._pax_control(top, "🐾 Pets",       self.pets,       4)
        self._booking_mode_buttons(top)

        tk.Frame(card, bg=LIGHT_GREY, height=1).pack(fill="x", pady=(0,16))

        main = tk.Frame(card, bg=WHITE); main.pack(fill="x")
        self._airport_selector(main, "Departing", self.depart_code)
        self._swap_button(main)
        self._airport_selector(main, "Arriving",  self.arrive_code)
        tk.Frame(main, bg=LIGHT_GREY, width=1).pack(side="left", fill="y", padx=16)
        self._date_picker_btn(main, "Departure Date", "depart_date")
        self._date_picker_btn(main, "Return Date",    "return_date")
        HoverButton(card, bg=ORANGE, fg=WHITE, hover_bg=MAROON, hover_fg=WHITE,
                    text="FIND FLIGHTS", font=FONT_BTN,
                    command=self._find_flights, padx=28, pady=11
                    ).pack(pady=(18,0), side="right")

        HoverButton(
            right_controls,
            bg=WHITE,
            fg=ORANGE,
            hover_bg=WHITE,
            hover_fg=MAROON,
            text="View Flight Days",
            font=FONT_BTN,
            command=self._open_flight_days_popup,
            padx=20,
            pady=10
        ).pack(anchor="w", padx=30, pady=(0, 20))

        # Results area
        self._results = tk.Frame(self._inner, bg=BG)
        self._results.pack(fill="x", padx=30, pady=(0,30))

    # ── Sub-builders ──────────────────────────────────────────────────────────

    def _trip_buttons(self, parent):
        frame = tk.Frame(parent, bg=WHITE); frame.pack(side="left")
        tk.Label(frame, text="Trip Type", font=FONT_LABEL, bg=WHITE, fg=GREY).pack(anchor="w")
        bf = tk.Frame(frame, bg=WHITE, pady=4); bf.pack()
        for val, txt in [("round","✈  Round Trip"), ("one","→  One Way")]:
            rb = tk.Radiobutton(bf, text=txt, variable=self.trip_type, value=val,
                                font=FONT_CTRL, bg=WHITE, fg=DARK, selectcolor=WHITE,
                                activebackground=WHITE, cursor="hand2",
                                indicatoron=False, relief="flat", padx=12, pady=6,
                                command=self._on_trip_type)
            rb.pack(side="left", padx=4)
            rb.config(selectcolor=ORANGE,
                      fg=WHITE if val==self.trip_type.get() else DARK,
                      bg=ORANGE  if val==self.trip_type.get() else WHITE)
        self._rb_refs = bf

    def _on_trip_type(self):
        for rb in self._rb_refs.winfo_children():
            sel = rb["value"] == self.trip_type.get()
            rb.config(bg=ORANGE if sel else WHITE, fg=WHITE if sel else DARK,
                      selectcolor=ORANGE if sel else WHITE)

    def _pax_control(self, parent, label, var, max_val):
        frame = tk.Frame(parent, bg=WHITE, padx=10); frame.pack(side="left")
        tk.Label(frame, text=label, font=FONT_LABEL, bg=WHITE, fg=GREY).pack(anchor="w")
        ctrl = tk.Frame(frame, bg=WHITE); ctrl.pack(pady=4)
        HoverButton(ctrl, bg=BG, fg=DARK, hover_bg=LIGHT_GREY, hover_fg=RED,
                    text="−", font=(_SANS, 14), width=2,
                    command=lambda: var.set(max(0, var.get()-1))).pack(side="left")
        tk.Label(ctrl, textvariable=var, font=(_SANS, 13, "bold"),
                 bg=WHITE, fg=DARK, width=2).pack(side="left", padx=6)
        HoverButton(ctrl, bg=BG, fg=DARK, hover_bg=LIGHT_GREY, hover_fg=RED,
                    text="+", font=(_SANS, 14), width=2,
                    command=lambda: var.set(min(max_val, var.get()+1))).pack(side="left")

    def _airport_selector(self, parent, title, code_var):
        frame = tk.Frame(parent, bg=WHITE, cursor="hand2")
        frame.pack(side="left", padx=(0,8))
        tk.Label(frame, text=title, font=FONT_LABEL, bg=WHITE, fg=GREY).pack(anchor="w")
        code_lbl = tk.Label(frame, textvariable=code_var, font=FONT_CODE, bg=WHITE, fg=DARK)
        code_lbl.pack(anchor="w")
        city_var = tk.StringVar()
        code_var.trace_add("write", lambda *_: city_var.set(AIRPORT_CODES.get(code_var.get(),"")))
        city_var.set(AIRPORT_CODES.get(code_var.get(),""))
        city_lbl = tk.Label(frame, textvariable=city_var, font=FONT_CITY, bg=WHITE, fg=RED)
        city_lbl.pack(anchor="w")
        tk.Frame(frame, bg=DARK, height=2).pack(fill="x", pady=(4,0))
        def open_picker(): AirportDropdown(frame, code_var.get(), code_var.set)
        for w in (frame, code_lbl, city_lbl):
            w.bind("<Button-1>", lambda e: open_picker())

    def _swap_button(self, parent):
        frame = tk.Frame(parent, bg=WHITE); frame.pack(side="left", padx=8)
        def swap():
            a, b = self.depart_code.get(), self.arrive_code.get()
            self.depart_code.set(b); self.arrive_code.set(a)
        HoverButton(frame, bg=LIGHT_GREY, fg=DARK, hover_bg=DARK, hover_fg=WHITE,
                    text="⇄", font=(_SANS, 14),
                    command=swap, padx=6, pady=6).pack(pady=14)

    def _date_picker_btn(self, parent, title, attr):
        frame = tk.Frame(parent, bg=WHITE, cursor="hand2", padx=6)
        frame.pack(side="left")
        tk.Label(frame, text=title, font=FONT_LABEL, bg=WHITE, fg=GREY).pack(anchor="w")
        date_var = tk.StringVar()
        def refresh():
            dt = getattr(self, attr)
            date_var.set(dt.strftime("%a, %b ") + str(dt.day))
        refresh()
        lbl = tk.Label(frame, textvariable=date_var,
                       font=(_SANS, 16, "bold"), bg=WHITE, fg=DARK)
        lbl.pack(anchor="w")
        tk.Frame(frame, bg=BORDER, height=1).pack(fill="x", pady=(4,0))
        def open_cal():
            CalendarPicker(frame, getattr(self, attr),
                           lambda d: (setattr(self, attr, d), refresh()))
        for w in (frame, lbl):
            w.bind("<Button-1>", lambda e: open_cal())

    def _booking_mode_buttons(self, parent):
        frame = tk.Frame(parent, bg=WHITE, padx=10)
        frame.pack(side="left")

        tk.Label(frame, text="Booking Type", font=FONT_LABEL, bg=WHITE, fg=GREY).pack(anchor="w")

        bf = tk.Frame(frame, bg=WHITE, pady=4)
        bf.pack()

        for val, txt in [("seat", "Seat Booking"), ("charter", "Charter Aircraft")]:
            rb = tk.Radiobutton(
                bf,
                text=txt,
                variable=self.booking_mode,
                value=val,
                font=FONT_CTRL,
                bg=WHITE,
                fg=DARK,
                selectcolor=WHITE,
                activebackground=WHITE,
                cursor="hand2",
                indicatoron=False,
                relief="flat",
                padx=12,
                pady=6
            )
            rb.pack(side="left", padx=4)

    def _build_flight_days_panel(self, parent):
        panel = tk.Frame(
            parent,
            bg=WHITE,
            padx=24,
            pady=16,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        panel.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        tk.Label(
            panel,
            text="Flight Days",
            font=(_SANS, 14, "bold"),
            bg=WHITE,
            fg=DARK
        ).pack(anchor="w")

        tk.Label(
            panel,
            text="Green = route operates that day   |   Red = no scheduled service",
            font=FONT_SMALL,
            bg=WHITE,
            fg=GREY
        ).pack(anchor="w", pady=(2, 14))

        # Scrollable container
        container = tk.Frame(panel, bg=WHITE)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=WHITE, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        scrollable_frame = tk.Frame(canvas, bg=WHITE)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        table = scrollable_frame

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        OPERATES = "#63F542"      # bright green
        NO_SERVICE = "#EF2B2B"    # red

        # Header row
        tk.Label(
            table,
            text="Route",
            font=FONT_ROUTE,
            bg=WHITE,
            fg=DARK,
            anchor="w",
            width=22,
            padx=8,
            pady=6
        ).grid(row=0, column=0, sticky="nsew")

        for col, day in enumerate(days, start=1):
            tk.Label(
                table,
                text=day,
                font=FONT_ROUTE,
                bg=WHITE,
                fg=DARK,
                anchor="center",
                padx=8,
                pady=6
            ).grid(row=0, column=col, sticky="nsew")

        # Route rows
        for row, ((dep, arr), operating_days) in enumerate(ROUTE_DAYS.items(), start=1):
            dep_city = AIRPORT_CODES.get(dep, "")
            arr_city = AIRPORT_CODES.get(arr, "")

            route_cell = tk.Frame(table, bg=WHITE, padx=8, pady=6)
            route_cell.grid(row=row, column=0, sticky="nsew")

            tk.Label(
                route_cell,
                text=f"{dep} → {arr}",
                font=FONT_ROUTE,
                bg=WHITE,
                fg=DARK,
                anchor="w"
            ).pack(anchor="w")

            tk.Label(
                route_cell,
                text=f"{dep_city} → {arr_city}",
                font=FONT_DETAIL,
                bg=WHITE,
                fg=GREY,
                anchor="w"
            ).pack(anchor="w")

            for day_index in range(7):
                color = OPERATES if day_index in operating_days else NO_SERVICE

                tk.Frame(
                    table,
                    bg=color,
                    highlightbackground=WHITE,
                    highlightthickness=1,
                    height=34
                ).grid(row=row, column=day_index + 1, sticky="nsew", padx=1, pady=1)

        # Let columns stretch evenly
        table.columnconfigure(0, weight=2)

        for col in range(1, 8):
            table.columnconfigure(col, weight=1)

    def _open_flight_days_popup(self):
        popup = tk.Toplevel(self)
        popup.title("ElectRAM Air – Flight Days")
        popup.configure(bg=BG)
        popup.geometry("850x600")
        popup.resizable(True, True)

        header = tk.Frame(popup, bg=MAROON, pady=14)
        header.pack(fill="x")

        tk.Label(
            header,
            text="✈  Flight Days",
            font=(_SERIF, 22, "bold"),
            bg=MAROON,
            fg=WHITE
        ).pack()

        body = tk.Frame(popup, bg=BG)
        body.pack(fill="both", expand=True, padx=18, pady=18)

        self._build_flight_days_panel(body)

    # ── Search & Results ──────────────────────────────────────────────────────

    def _find_flights(self):
        dep = self.depart_code.get()
        arr = self.arrive_code.get()
        if dep == arr:
            messagebox.showwarning("Invalid Route",
                                   "Departure and arrival airports cannot be the same.")
            return
        if self.passengers.get() == 0:
            messagebox.showwarning("No Passengers", "Please add at least 1 passenger.")
            return
        self._show_results(dep, arr)

    def _apply_booking_mode(self, flights):
        processed = []

        for f in flights:
            f_copy = copy.deepcopy(f)  # avoid mutating original data

            if f_copy.get("multi_leg"):
                if self.booking_mode.get() == "charter":
                    f_copy["display_price"] = (
                        f_copy["leg1"]["aircraft_price"] +
                        f_copy["leg2"]["aircraft_price"]
                    )
                else:
                    f_copy["display_price"] = f_copy["price"]

            else:
                if self.booking_mode.get() == "charter":
                    f_copy["display_price"] = f_copy["aircraft_price"]
                else:
                    f_copy["display_price"] = f_copy["price"]

            processed.append(f_copy)

        return processed

    def _show_results(self, dep, arr):
        for w in self._results.winfo_children():
            w.destroy()

        dep_city = AIRPORT_CODES.get(dep, dep)
        arr_city = AIRPORT_CODES.get(arr, arr)
        dep_str = self.depart_date.strftime("%a, %b ") + str(self.depart_date.day)
        ret_str = self.return_date.strftime("%a, %b ") + str(self.return_date.day)
        is_round = self.trip_type.get() == "round"

        outbound_flights = random_flights(dep, arr, self.depart_date, 5)
        outbound_flights = self._apply_booking_mode(outbound_flights)

        if is_round:
            return_flights = random_flights(arr, dep, self.return_date, 5)
            return_flights = self._apply_booking_mode(return_flights)

            hdr = tk.Frame(self._results, bg=BG, pady=4)
            hdr.pack(fill="x")

            tk.Label(
                hdr,
                text=f"{dep}  ✈  {arr}  ✈  {dep}",
                font=(_SANS, 16, "bold"),
                bg=BG,
                fg=DARK
            ).pack(side="left")

            tk.Label(
                hdr,
                text=f"   Round Trip   ·   {dep_str} – {ret_str}"
                     f"   ·   {self.passengers.get()} passenger{'s' if self.passengers.get()>1 else ''}",
                font=FONT_SMALL,
                bg=BG,
                fg=GREY
            ).pack(side="left", pady=(5, 0))

            self._section_header(
                f"ROUND TRIP  ·  {dep} → {arr}  ·  {dep_str}     |     {arr} → {dep}  ·  {ret_str}"
            )

            if not outbound_flights or not return_flights:
                tk.Label(
                    self._results,
                    text=f"No round trip flights currently available for {dep} → {arr} → {dep}.",
                    font=FONT_BTN,
                    bg=BG,
                    fg=GREY,
                    pady=30
                ).pack()
            else:
                for out_flight, ret_flight in zip(outbound_flights, return_flights):
                    build_round_trip_row(
                        self._results,
                        out_flight,
                        ret_flight,
                        self._on_round_trip_book
                    )

        else:
            hdr = tk.Frame(self._results, bg=BG, pady=4)
            hdr.pack(fill="x")

            tk.Label(
                hdr,
                text=f"{dep}  ✈  {arr}",
                font=(_SANS, 16, "bold"),
                bg=BG,
                fg=DARK
            ).pack(side="left")

            tk.Label(
                hdr,
                text=(f"   {dep_city}  →  {arr_city}   ·   {dep_str}"
                      f"   ·   {self.passengers.get()} passenger{'s' if self.passengers.get()>1 else ''}"),
                font=FONT_SMALL,
                bg=BG,
                fg=GREY
            ).pack(side="left", pady=(5, 0))

            self._section_header(f"OUTBOUND  ·  {dep} → {arr}  ·  {dep_str}")

            if not outbound_flights:
                tk.Label(
                    self._results,
                    text=f"No flights currently available for {dep} → {arr}.",
                    font=FONT_BTN,
                    bg=BG,
                    fg=GREY,
                    pady=30
                ).pack()
            else:
                for f in outbound_flights:
                    if f.get("multi_leg"):
                        build_multileg_row(self._results, f, self._on_multileg_book)
                    else:
                        build_flight_row(self._results, f, lambda fl: self._on_book(fl, "Outbound"))

        self.after(120, lambda: self._canvas.yview_moveto(0.22))

    def _section_header(self, text):
        f = tk.Frame(self._results, bg=SECTION_BG,
                     highlightbackground=BORDER, highlightthickness=1)
        f.pack(fill="x")
        tk.Label(f, text=f"  {text}", font=FONT_TAG,
                 bg=SECTION_BG, fg=GREY, anchor="w", pady=7).pack(fill="x", padx=8)

    def _on_round_trip_book(self, outbound, ret):
        def describe_trip(f):
            if f.get("multi_leg"):
                leg1 = f["leg1"]
                leg2 = f["leg2"]

                l1_dep_t, l1_dep_ap = fmt_time(leg1["dep_h"], leg1["dep_m"])
                l1_arr_t, l1_arr_ap = fmt_time(leg1["arr_h"], leg1["arr_m"])
                l2_dep_t, l2_dep_ap = fmt_time(leg2["dep_h"], leg2["dep_m"])
                l2_arr_t, l2_arr_ap = fmt_time(leg2["arr_h"], leg2["arr_m"])

                return (
                    f"  {leg1['dep_code']} → {leg1['arr_code']}\n"
                    f"  {l1_dep_t}{l1_dep_ap} – {l1_arr_t}{l1_arr_ap}\n"
                    f"  45 min layover in {f['connection']}\n"
                    f"  {leg2['dep_code']} → {leg2['arr_code']}\n"
                    f"  {l2_dep_t}{l2_dep_ap} – {l2_arr_t}{l2_arr_ap}"
                )

            dep_t, dep_ap = fmt_time(f["dep_h"], f["dep_m"])
            arr_t, arr_ap = fmt_time(f["arr_h"], f["arr_m"])

            return (
                f"  {f['dep_code']} → {f['arr_code']}\n"
                f"  {dep_t}{dep_ap} – {arr_t}{arr_ap}"
            )

        total_price = (
            outbound.get("display_price", outbound["price"]) +
            ret.get("display_price", ret["price"])
        )

        if self.booking_mode.get() == "charter":
            price_label = "Aircraft charter price"
            passenger_line = "Aircraft charter includes up to 19 seats"
            final_total = total_price
        else:
            price_label = "Price per person"
            passenger_line = f"Passengers: {self.passengers.get()}"
            final_total = total_price * self.passengers.get()

        messagebox.showinfo(
            "Round Trip Selected ✔",
            f"ROUND TRIP SELECTED\n\n"
            f"OUTBOUND\n"
            f"{describe_trip(outbound)}\n\n"
            f"RETURN\n"
            f"{describe_trip(ret)}\n\n"
            f"{price_label}: ${total_price}\n"
            f"{passenger_line}\n"
            f"Total: ${final_total}\n\n"
            f"Proceeding to checkout…"
        )

    def _on_multileg_book(self, itinerary):
        leg1 = itinerary["leg1"]
        leg2 = itinerary["leg2"]

        l1_dep_t, l1_dep_ap = fmt_time(leg1["dep_h"], leg1["dep_m"])
        l1_arr_t, l1_arr_ap = fmt_time(leg1["arr_h"], leg1["arr_m"])

        l2_dep_t, l2_dep_ap = fmt_time(leg2["dep_h"], leg2["dep_m"])
        l2_arr_t, l2_arr_ap = fmt_time(leg2["arr_h"], leg2["arr_m"])

        selected_price = itinerary.get("display_price", itinerary["price"])

        if self.booking_mode.get() == "charter":
            price_label = "Aircraft charter price"
            passenger_line = "Aircraft charter includes up to 19 seats"
            total = selected_price
        else:
            price_label = "Price per person"
            passenger_line = f"Passengers: {self.passengers.get()}"
            total = selected_price * self.passengers.get()

        messagebox.showinfo(
            "Connecting Flight Selected ✔",
            f"CONNECTING FLIGHT SELECTED\n\n"
            f"LEG 1\n"
            f"  {leg1['dep_code']} → {leg1['arr_code']}\n"
            f"  {l1_dep_t}{l1_dep_ap} – {l1_arr_t}{l1_arr_ap}\n\n"
            f"LAYOVER\n"
            f"  45 min in {itinerary['connection']}\n\n"
            f"LEG 2\n"
            f"  {leg2['dep_code']} → {leg2['arr_code']}\n"
            f"  {l2_dep_t}{l2_dep_ap} – {l2_arr_t}{l2_arr_ap}\n\n"
            f"{price_label}: ${selected_price}\n"
            f"{passenger_line}\n"
            f"Total: ${total}\n\n"
            f"Proceeding to checkout…"
        )


if __name__ == "__main__":
    FlightBookingApp().mainloop()