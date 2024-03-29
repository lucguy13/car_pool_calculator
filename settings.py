# ------------------- #
# Settings            #
# ------------------- #

# Settable settings
PARTICIPANT_NAMES = ["Neerav", "Brock", "Tony", "Juan"]
TRIP_DISTANCE = 19 # Km
PETROL_PRICE = 2.1 # $/L
CAR_CONSUMPTION = 8.2 # L/100km

# Derived trip price
CAR_CONSUMPTION_PER_KM = CAR_CONSUMPTION / 100
PRICE_PER_KM = CAR_CONSUMPTION_PER_KM * PETROL_PRICE

# Toll price
TOLL_PRICE_PER_TRIP = 6.5 # $

# Total
TOTAL_PRICE_PER_TRIP = (PRICE_PER_KM * TRIP_DISTANCE) + TOLL_PRICE_PER_TRIP

# Trips
TRIP_NAMES = (  "Monday morning", "Monday arvo", \
                "Tuesday morning", "Tuesday arvo", \
                "Wednesday morning", "Wednesday arvo", \
                "Thursday morning", "Thursday arvo", \
                "Friday morning", "Friday arvo")

# Presets (to save time)
PASSENGERS_PRESETS = (
    ("dummy",), # 0
    ("Brock", "Tony"),  # 1
    ("Brock", "Tony", "Neerav"),          # 2
    ("Brock", "Tony", "Juan"),             # 3
)