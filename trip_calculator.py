from settings import TOTAL_PRICE_PER_TRIP, TRIP_NAMES, PARTICIPANT_NAMES
from colorama_wrapper import Colour
import dateparser
from copy import deepcopy
import csv

# -------------------- #
# Globals              #
# -------------------- #

col = Colour()

# -------------------- #
# Utility classes      #
# -------------------- #

class Participant():
    def __init__(self, name):
        self.name = name

class Balance():
    def __init__(self):
        self.balance = {}
        for name in PARTICIPANT_NAMES:
            self.balance[name] = 0

    def __add__(self, other):
        tot = deepcopy(self)
        for name in PARTICIPANT_NAMES:
            tot.balance[name] = self.balance[name] + other.balance[name]
        return tot

    def __getitem__(self, key):
        return self.balance[key]

    def __setitem__(self, key, new_val):
        self.balance[key] = new_val

    def __str__(self):
        string = ''
        for name in PARTICIPANT_NAMES:
            string += (name + ": {}\n".format(self.balance[name]))
        return string

class TripClass():
    price = TOTAL_PRICE_PER_TRIP

    def __init__(self, trip_name):
        self.trip_name = trip_name
        self.participants = []
        self.balance = Balance()

        print("\nTrip: " + col.blue(trip_name))
        # Gather participants
        while True:
            # Print current ones
            if not self.participants:
                print("No participants added")
            else:
                print("Current participants: ", end='')
                for participant in self.participants:
                    print(col.blue(participant) + ' / ', end='')
                print()
            # Add more
            resp = input("Type participant's name (or 'Restart' / 'End / '' empty for none): ")
            if resp.upper() == 'RESTART':
                self.participants = []
                continue
            elif resp.upper() == "END":
                print("Done adding participants")
                break
            elif resp.upper() == "":
                print("No driving that day")
                break
            else:
                # Find participant
                found = ''
                for participant_name in PARTICIPANT_NAMES:
                    if participant_name.upper().find(resp.upper()) != -1:
                        # Invalidate if more than one participant corresponds
                        if found != '':
                            print(col.red("More than one participants corresponds, try again"))
                            found = ''
                            break
                        else:
                            found = participant_name
                if found != '':
                    self.participants.append(found)

    def __str__():
        string = ''
        for participant in self.participants:
            string += participant + '\n'
        return string

    def calculate(self):
        # Calc price per person
        if self.participants == 0:
            self.price_per_person = 0
        else:
            self.price_per_person = TOTAL_PRICE_PER_TRIP / (len(self.participants) + 1) # Take driver into account
        # Calc how much each participant owes
        self.balance = Balance()
        for participant_name in PARTICIPANT_NAMES:
            if participant_name in self.participants:
                self.balance[participant_name] = self.price_per_person
            else:
                self.balance[participant_name] = 0
        return self.balance

class WeekClass():
    def __init__(self):
        self.trips = {}
        self.week_balance = Balance()
        # Input date
        while True:
            date = dateparser.parse(input("What is the week date ? : "))
            print("Date parsed as: {}".format(date))
            # Validate
            while True:
                valid = input("Is the date right? (Y/N): ")
                if valid.upper() == 'Y':
                    valid = True
                    print(col.green("Date validated"))
                    self.date = date
                    break
                elif valid.upper() == 'N':
                    valid = False
                    print(col.red("Date invalidated"))
                    break
                else:
                    print(col.yellow("Invalid answer"))
                    continue
            # Break on valid date
            if valid is True:
                break
            else:
                continue

    def collect_trips_info(self):
        print(col.blue("\nWEEK " + str(self.date)))
        for trip_name in TRIP_NAMES:
            self.trips[trip_name] = TripClass(trip_name)

    def calculate(self):
        self.week_balance = Balance()
        for trip_name in self.trips:
            trip_balance = self.trips[trip_name].calculate()
            self.week_balance = self.week_balance + trip_balance
        return self.week_balance

    def print_summary(self):
        print(col.blue("Week {} balance:".format(self.date)))
        print(self.week_balance)

    def save_detailed(self):
        # Create file name from week date
        date_formatted = self.date.strftime("%Y-%m-%d")
        csv_name = 'DETAILED_' + date_formatted + '.csv'
        # Open file and save balance for every trip
        with open(csv_name, 'w') as csvfile:
            fieldnames = ['Participant name'] + TRIP_NAMES + ["Week Total"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for participant_name in PARTICIPANT_NAMES:
                value_dict = {}
                value_dict['Participant name'] = participant_name
                for trip_name in self.trips:
                    trip = self.trips[trip_name]
                    value_dict[trip_name] = "{:.2f}".format(trip.balance[participant_name])
                value_dict['Week Total'] = "{:.2f}".format(self.week_balance[participant_name])
                writer.writerow(value_dict)
            print(col.green("Saved details for week: {}".format(str(self.date))))

    def __str__(self):
        return "Week date: {}".format(self.date)

class CarpoolCalculatorClass():
    Weeks = []
    total_balance = Balance()
    
    def add_weeks(self):
        print(col.blue("--- Selecting weeks of carpool ---\n"))
        while True:
            resp = input("Press " + col.blue('A') + " to add a new week, " + col.blue('D') + " for done, " + col.blue('V') + " for view: ")
            if resp.upper() == 'A':
                self.Weeks.append(WeekClass())
            elif resp.upper() == 'D':
                print("Done adding weeks")
                break
            elif resp.upper() == 'V':
                if not self.Weeks:
                    print("No week added")
                for week in self.Weeks:
                    print(week)
            else:
                print(col.yellow("Invalid answer"))
                continue

    def collect_trip_info(self):
        for week in self.Weeks:
            week.collect_trips_info()

    def print_summary(self):
        print(col.blue("\n--- Week summary ---\n"))
        for week in self.Weeks:
            week.print_summary()
        print(col.blue("\nTOTAL SUMMARY:"))
        print(self.total_balance)

    def calculate(self):
        self.total_balance = Balance()
        for week in self.Weeks:
            week_balance = week.calculate()
            self.total_balance = self.total_balance + week_balance

    def _save(self):
        # Fetch oldest and newest date
        earliest_date = oldest_date = self.Weeks[0].date
        for week in self.Weeks:
            if week.date > oldest_date:
                oldest_date = week.date
            if week.date < earliest_date:
                earliest_date = week.date
        earliest_date = earliest_date.strftime("%Y-%m-%d")
        oldest_date = oldest_date.strftime("%Y-%m-%d")
        csv_name = 'SUMMARY_' + str(earliest_date) + '_TO_' + str(oldest_date) + '.csv'
        # Open file and save total summary
        with open(csv_name, 'w') as csvfile:
            fieldnames = ['Participant name'] + ["Total"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for participant_name in self.total_balance.balance:
                value_dict = {}
                value_dict['Participant name'] = participant_name
                value_dict['Total'] = "{:.2f}".format(self.total_balance[participant_name])
                writer.writerow(value_dict)
            print(col.green("Saved summary"))

    def save(self):
        # Ask user if saving
        while True:
            resp = input("Save the results ? (Y/N): ")
            if resp.upper() == 'Y':
                print(col.blue("Saving"))
                # Save summary
                self._save()
                # Save every week summary
                for week in self.Weeks:
                    week.save_detailed()
                break
            elif resp.upper() == 'N':
                print(col.warning("Not saving"))
                break
            else:
                print(col.red("Invalid reponse"))
                continue


# -------------------- #
# Main                 #
# -------------------- #

if __name__ == "__main__":
    carpool_calc = CarpoolCalculatorClass()

    print(col.blue("\n-----------------------------------"))
    print(col.blue("WELCOME TO THE CAR POOL CALCULATOR!"))
    print(col.blue("-----------------------------------\n"))

    # Add weeks until specified finished
    carpool_calc.add_weeks()

    # Collect info about each week
    print(col.blue("\n--- Collecting trip info for each week ---\n"))
    carpool_calc.collect_trip_info()

    # Calculate and print summary
    carpool_calc.calculate()
    carpool_calc.print_summary()

    # Save
    carpool_calc.save()

    print(col.blue("Exiting"))