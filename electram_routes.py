# Routes overhaul for more route frequency

from datetime import datetime
import copy
import math

# Day index used by Python datetime.weekday():
# Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4, Saturday=5, Sunday=6
EVERY_DAY = [0, 1, 2, 3, 4, 5, 6]

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
AIRPORT_ORDER = [code for code, _ in AIRPORTS]

BIG_AIRPORTS = {"CRW", "ATL", "CLT"}
SMALL_AIRPORTS = set(AIRPORT_ORDER) - BIG_AIRPORTS

# These route groups drive the demo schedule frequency.
# Big airports: 4-5 flights/day
# Big-small routes: 2-3 flights/day
# Small-small routes: 2 flights/day
BIG_BIG_ROUTES = {
    ("CRW", "ATL"),
    ("CRW", "CLT"),
    ("ATL", "CLT"),
}

# Charleston is the main WV feeder and directly serves every small airport.
CRW_FEEDER_ROUTES = {
    ("CRW", "ROA"),
    ("CRW", "TRI"),
    ("CRW", "LEX"),
    ("CRW", "CKB"),
    ("CRW", "MGW"),
    ("CRW", "BNA"),
    ("CRW", "IND"),
    ("CRW", "SDF"),
    ("CRW", "HTS"),
    ("CRW", "SHD"),
}

# Atlanta handles Indiana, Kentucky, and Tennessee-heavy service.
ATL_FEEDER_ROUTES = {
    ("ATL", "IND"),
    ("ATL", "LEX"),
    ("ATL", "SDF"),
    ("ATL", "BNA"),
    ("ATL", "TRI"),
}

# Charlotte handles Tennessee, Virginia, and Huntington service.
CLT_FEEDER_ROUTES = {
    ("CLT", "TRI"),
    ("CLT", "BNA"),
    ("CLT", "ROA"),
    ("CLT", "SHD"),
    ("CLT", "HTS"),
}

# Small-small "closest useful neighbor" demo links.
# These give small airports at least one nearby direct option.
SMALL_SMALL_ROUTES = {
    ("CKB", "MGW"),
    ("HTS", "LEX"),
    ("LEX", "SDF"),
    ("SDF", "BNA"),
    ("BNA", "TRI"),
    ("ROA", "SHD"),
    ("ROA", "TRI"),
    ("IND", "SDF"),
}

# Durations are demo gate-to-gate style estimates in hours/minutes.
# Where current real service exists, these are based around published scheduled
# elapsed times. Where no current direct service exists, these are planning
# estimates for a small commuter aircraft demo.
ROUTES_BASE = {
    # Big ↔ big
    ("CRW", "ATL"): {"dur_h": 1, "dur_m": 35},
    ("CRW", "CLT"): {"dur_h": 1, "dur_m": 15},
    ("ATL", "CLT"): {"dur_h": 1, "dur_m": 20},

    # CRW feeder routes
    ("CRW", "ROA"): {"dur_h": 0, "dur_m": 55},
    ("CRW", "TRI"): {"dur_h": 1, "dur_m": 5},
    ("CRW", "LEX"): {"dur_h": 0, "dur_m": 55},
    ("CRW", "CKB"): {"dur_h": 0, "dur_m": 35},
    ("CRW", "MGW"): {"dur_h": 0, "dur_m": 45},
    ("CRW", "BNA"): {"dur_h": 1, "dur_m": 25},
    ("CRW", "IND"): {"dur_h": 1, "dur_m": 30},
    ("CRW", "SDF"): {"dur_h": 1, "dur_m": 10},
    ("CRW", "HTS"): {"dur_h": 0, "dur_m": 30},
    ("CRW", "SHD"): {"dur_h": 1, "dur_m": 5},

    # ATL feeder routes
    ("ATL", "IND"): {"dur_h": 1, "dur_m": 35},
    ("ATL", "LEX"): {"dur_h": 1, "dur_m": 20},
    ("ATL", "SDF"): {"dur_h": 1, "dur_m": 25},
    ("ATL", "BNA"): {"dur_h": 1, "dur_m": 10},
    ("ATL", "TRI"): {"dur_h": 1, "dur_m": 15},

    # CLT feeder routes
    ("CLT", "TRI"): {"dur_h": 1, "dur_m": 5},
    ("CLT", "BNA"): {"dur_h": 1, "dur_m": 25},
    ("CLT", "ROA"): {"dur_h": 1, "dur_m": 5},
    ("CLT", "SHD"): {"dur_h": 1, "dur_m": 15},
    ("CLT", "HTS"): {"dur_h": 1, "dur_m": 10},

    # Small ↔ small closest-neighbor links
    ("CKB", "MGW"): {"dur_h": 0, "dur_m": 25},
    ("HTS", "LEX"): {"dur_h": 0, "dur_m": 45},
    ("LEX", "SDF"): {"dur_h": 0, "dur_m": 40},
    ("SDF", "BNA"): {"dur_h": 0, "dur_m": 55},
    ("BNA", "TRI"): {"dur_h": 1, "dur_m": 10},
    ("ROA", "SHD"): {"dur_h": 0, "dur_m": 40},
    ("ROA", "TRI"): {"dur_h": 0, "dur_m": 55},
    ("IND", "SDF"): {"dur_h": 0, "dur_m": 55},
}

DIRECT_ROUTE_SET_BASE = set(ROUTES_BASE.keys())


def _mirror_pairs(base_dict):
    """Return a copy of a pair-keyed dict with reverse-direction entries added."""
    mirrored = {}
    for (dep, arr), value in base_dict.items():
        mirrored[(dep, arr)] = copy.deepcopy(value)
        mirrored[(arr, dep)] = copy.deepcopy(value)
    return mirrored


ROUTES = _mirror_pairs(ROUTES_BASE)

# All scheduled demo routes operate every day so users can get anywhere every day.
ROUTE_DAYS = {pair: EVERY_DAY[:] for pair in ROUTES}

# Demo drive times between directly displayed / computed route pairs.
# These are practical planning estimates, not live traffic estimates.
DRIVE_TIMES_BASE = {
    # Big ↔ big
    ("CRW", "ATL"): {"h": 7, "m": 0},
    ("CRW", "CLT"): {"h": 4, "m": 15},
    ("ATL", "CLT"): {"h": 4, "m": 15},

    # CRW feeder routes
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

    # ATL feeder routes
    ("ATL", "IND"): {"h": 8, "m": 0},
    ("ATL", "LEX"): {"h": 5, "m": 45},
    ("ATL", "SDF"): {"h": 6, "m": 20},
    ("ATL", "BNA"): {"h": 4, "m": 15},
    ("ATL", "TRI"): {"h": 4, "m": 45},

    # CLT feeder routes
    ("CLT", "TRI"): {"h": 3, "m": 0},
    ("CLT", "BNA"): {"h": 6, "m": 30},
    ("CLT", "ROA"): {"h": 3, "m": 0},
    ("CLT", "SHD"): {"h": 4, "m": 45},
    ("CLT", "HTS"): {"h": 4, "m": 30},

    # Small ↔ small closest-neighbor links
    ("CKB", "MGW"): {"h": 0, "m": 45},
    ("HTS", "LEX"): {"h": 2, "m": 5},
    ("LEX", "SDF"): {"h": 1, "m": 25},
    ("SDF", "BNA"): {"h": 2, "m": 45},
    ("BNA", "TRI"): {"h": 4, "m": 45},
    ("ROA", "SHD"): {"h": 2, "m": 0},
    ("ROA", "TRI"): {"h": 2, "m": 25},
    ("IND", "SDF"): {"h": 1, "m": 55},
}

DRIVE_TIMES = _mirror_pairs(DRIVE_TIMES_BASE)


def _normalized_pair(dep, arr):
    """Return pair in base-direction form where possible."""
    if (dep, arr) in DIRECT_ROUTE_SET_BASE:
        return (dep, arr)
    if (arr, dep) in DIRECT_ROUTE_SET_BASE:
        return (arr, dep)
    return (dep, arr)


def route_type(dep, arr):
    pair = _normalized_pair(dep, arr)
    if pair in BIG_BIG_ROUTES:
        return "big_big"
    if pair in SMALL_SMALL_ROUTES:
        return "small_small"
    if dep in BIG_AIRPORTS and arr in SMALL_AIRPORTS:
        return "big_small"
    if arr in BIG_AIRPORTS and dep in SMALL_AIRPORTS:
        return "big_small"
    return "connection"


def default_departure_times(dep, arr, direct=True):
    """Return demo departure times by route type."""
    rtype = route_type(dep, arr)

    if not direct:
        if rtype == "small_small":
            return [(13, 0)]
        return [(8, 0), (11, 0), (14, 0)]


    if rtype == "big_big":
        return [(8, 0), (10, 30), (13, 0), (15, 30), (18, 0)]

    if rtype == "big_small":
        # Slightly shorter feeder routes get 3 flights; longer feeder routes get 2.
        route = get_route(dep, arr)
        duration_min = route["dur_h"] * 60 + route["dur_m"] if route else 90
        if duration_min <= 80:
            return [(8, 30), (13, 0), (17, 30)]
        return [(9, 0), (16, 30)]

    if rtype == "small_small":
        # Small-small demo routes should only show one direct frequency per day.
        return [(9, 30)]

    return [(9, 0), (13, 0), (17, 0)]


def get_route(dep, arr):
    return ROUTES.get((dep, arr))


def get_route_days(dep, arr):
    return ROUTE_DAYS.get((dep, arr))


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
    """Find the fastest valid one-stop connection for any non-direct route."""
    valid_connections = []

    # Prefer the user's requested hub structure before falling back to any shortest connection.
    preferred_mids = ["CRW", "ATL", "CLT"] + AIRPORT_ORDER

    for mid in preferred_mids:
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

        # Small bonus to choose big-airport connections when durations are close.
        hub_preference = 0 if mid in BIG_AIRPORTS else 20

        valid_connections.append({
            "mid": mid,
            "first_route": first_route,
            "second_route": second_route,
            "total_minutes": total_minutes + hub_preference,
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


def multileg_price(price1, price2, booking_mode="seat"):
    # Multileg discount: adjust this value to change the connection discount.
    multi_discount = 30

    total = price1 + price2 - multi_discount

    # Keeps demo pricing from going negative if you test very short routes later.
    return max(total, 0)


def generate_flights(dep, arr, d, count=5):
    route = get_route(dep, arr)

    if route is None:
        return []

    if not route_operates_on_date(dep, arr, d):
        return []

    departure_times = default_departure_times(dep, arr, direct=True)
    flights = []

    for i, (dep_h, dep_m) in enumerate(departure_times[:count]):
        arr_h, arr_m = add_minutes(dep_h, dep_m, route["dur_h"], route["dur_m"])

        seat_price = flight_price(route["dur_h"], route["dur_m"], "seat")
        aircraft_price = flight_price(route["dur_h"], route["dur_m"], "charter")

        # Small demo fare variation so the cards do not all look identical.
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


def build_connection_itineraries(dep, arr, d, count=5):
    """Build one-stop itineraries without first checking for a direct flight.

    This is separated out so small-to-small routes can show BOTH:
      1. the closest small-airport nonstop option, when one exists
      2. a hub-connection option through CRW/ATL/CLT
    """
    connection = find_connection(dep, arr, d)

    if connection is None:
        return []

    mid, first_route, second_route = connection
    departure_times = default_departure_times(dep, arr, direct=False)
    itineraries = []

    for i, (dep_h, dep_m) in enumerate(departure_times[:count]):
        mid_arr_h, mid_arr_m = add_minutes(dep_h, dep_m, first_route["dur_h"], first_route["dur_m"])
        second_dep_h, second_dep_m = add_minutes(mid_arr_h, mid_arr_m, 0, 45)
        final_arr_h, final_arr_m = add_minutes(second_dep_h, second_dep_m, second_route["dur_h"], second_route["dur_m"])

        price1 = flight_price(first_route["dur_h"], first_route["dur_m"], "seat")
        aircraft_price1 = flight_price(first_route["dur_h"], first_route["dur_m"], "charter")
        price2 = flight_price(second_route["dur_h"], second_route["dur_m"], "seat")
        aircraft_price2 = flight_price(second_route["dur_h"], second_route["dur_m"], "charter")

        total_seat_price = multileg_price(price1, price2, "seat")
        total_aircraft_price = multileg_price(aircraft_price1, aircraft_price2, "charter")

        itineraries.append({
            "multi_leg": True,
            "connection": mid,
            "price": total_seat_price,
            "aircraft_price": total_aircraft_price,
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
                "popular": False,
                "dep_code": mid,
                "arr_code": arr,
                "dep_city": AIRPORT_CODES.get(mid, mid),
                "arr_city": AIRPORT_CODES.get(arr, arr),
            },
        })

    return itineraries


def generate_multileg_flights(dep, arr, d, count=5):
    direct = generate_flights(dep, arr, d, count)

    # Small → small searches should show limited demo frequency:
    #   1 direct closest-small-airport option, when that direct route exists
    #   1 multileg hub-connected option, when a valid connection exists
    if dep in SMALL_AIRPORTS and arr in SMALL_AIRPORTS:
        direct = direct[:1]
        connection_options = build_connection_itineraries(dep, arr, d, 1)[:1]

        if direct and connection_options:
            return direct + connection_options, "small_small_mixed"

        if direct:
            return direct, "direct"

        if connection_options:
            return connection_options, "connection"

        return [], "none"

    if direct:
        return direct, "direct"

    connection_options = build_connection_itineraries(dep, arr, d, count)

    if not connection_options:
        return [], "none"

    return connection_options, "connection"


def random_flights(dep, arr, d, count=5):
    flights, _ = generate_multileg_flights(dep, arr, d, count)
    return flights


def fmt_time(h, m):
    ampm = "AM" if h < 12 else "PM"
    return f"{h % 12 or 12}:{m:02d}", ampm


def get_drive_time(dep, arr):
    return DRIVE_TIMES.get((dep, arr))


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

    drive = get_drive_time(f.get("dep_code", ""), f.get("arr_code", ""))
    return time_to_minutes(drive) if drive else None


def apply_booking_mode(flights, booking_mode):
    processed = []

    for f in flights:
        f_copy = copy.deepcopy(f)

        if f_copy.get("multi_leg"):
            if booking_mode == "charter":
                f_copy["display_price"] = f_copy["aircraft_price"]
            else:
                f_copy["display_price"] = f_copy["price"]
        else:
            if booking_mode == "charter":
                f_copy["display_price"] = f_copy["aircraft_price"]
            else:
                f_copy["display_price"] = f_copy["price"]

        processed.append(f_copy)

    return processed
