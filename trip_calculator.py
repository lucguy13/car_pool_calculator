from settings import TOTAL_PRICE_PER_TRIP, TRIP_NAMES, PARTICIPANT_NAMES, PASSENGERS_PRESETS
from colorama_wrapper import Colour
import dateparser
from copy import deepcopy
import csv
import os

# -------------------- #
# Globals              #
# -------------------- #

col = Colour()

RESULTS_FOLD_PATH = os.path.join(os.path.dirname(__file__), 'Results')

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

    def gather_participants(self):

        print("\nTrip: " + col.blue(self.trip_name))
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
            resp = input("--- Add participants ---\n. Selection: participant name / preset number / 'clear' to empty list / '' for done: ")
            if resp.upper() == 'CLEAR':
                self.participants = []
                continue
            elif resp.upper() == "":
                if self.participants:
                    print(col.blue("Done"))
                else:
                    print(col.blue("No driving that day"))
                print("Done adding participants")
                break
            elif resp.isnumeric():
                # Apply preset
                if int(resp) > len(PASSENGERS_PRESETS):
                    print(col.red("Invalid preset"))
                    continue
                else:
                    for preset_participant in PASSENGERS_PRESETS[int(resp)]:
                        if preset_participant not in PARTICIPANT_NAMES:
                            print(col.yellow("Participant {} in preset is invalid, skipping it".format(preset_participant)))
                        else:
                            if preset_participant not in self.participants:
                                self.participants.append(preset_participant)
                    print(col.blue("Preset loaded"))
                    continue
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
                            # Only add if not already in the list
                            if participant_name not in self.participants:
                                found = participant_name
                if found != '':
                    self.participants.append(found)
                else:
                    print(col.red("No matching participants"))
    
    def add_participant(self, participant_name):
        if participant_name not in PARTICIPANT_NAMES:
            raise ValueError()
        if participant_name not in self.participants:
            self.participants.append(participant_name)

    def __str__(self):
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
    
    def init_date_from_user(self):
        # Input date
        while True:
            date = dateparser.parse(input("What is the week date ? : "))
            date = date.strftime("%Y-%m-%d")
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

    def load_from_csv(self, CSV_FOLDER_PATH, CSV_NAME):
        # Read csv
        self.date = dateparser.parse(CSV_NAME[9:-4])
        date_formatted = self.date.strftime("%Y-%m-%d")
        # Open file and save balance for every trip
        with open(os.path.join(CSV_FOLDER_PATH, CSV_NAME), 'r') as csvfile:
            fieldnames = ['Participant name'] + TRIP_NAMES + ["Week Total"]
            reader = csv.DictReader(csvfile, fieldnames=fieldnames)
            # For every participant (every row)
            for i, row in enumerate(reader):
                # Skip header
                if i == 0:
                    continue
                # For every trip
                for trip_name in TRIP_NAMES:
                    if trip_name not in self.trips:
                        self.trips[trip_name] = TripClass(trip_name)
                    # If participant depense balance is not 0, then he was part of the trip
                    balance = float(row[trip_name])
                    if balance != 0:
                        self.trips[trip_name].add_participant(row['Participant name'])     
        self.calculate()
            
    def collect_trips_info(self):
        print(col.blue("\nWEEK " + str(self.date)))
        for trip_name in TRIP_NAMES:
            if trip_name not in  self.trips:
                self.trips[trip_name] = TripClass(trip_name)
            self.trips[trip_name].gather_participants()

    def calculate(self):
        self.week_balance = Balance()
        for trip_name in self.trips:
            trip_balance = self.trips[trip_name].calculate()
            self.week_balance = self.week_balance + trip_balance
        return self.week_balance

    def print_summary(self):
        print(col.blue("Week {} balance:".format(self.date)))
        print(self.week_balance)

    def save_detailed(self, OUTPUT_FOLDER_PATH):
        # Create file name from week date
        date_formatted = self.date
        csv_name = 'DETAILED_' + date_formatted + '.csv'
        CSV_PATH = os.path.join(OUTPUT_FOLDER_PATH, csv_name)
        # Open file and save balance for every trip
        with open(CSV_PATH, 'w') as csvfile:
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
    
    def add_edit_weeks(self):
        # User selection add carpool weeks
        while True:
            # If carpool is empty add a new week directly
            if not self.Weeks:
                print("Carpool is empty\n")
                self.add_week()
            # Show the current weeks in selected carpool
            print(col.blue("\n---- Selected carpool menu: ----"))
            self.print_current_weeks()
            print("A) Add a new week")
            print("D) Done")
            # Selection
            resp = input("What do you want to do?: ")
            if resp.isnumeric():
                if (int(resp) > len(self.Weeks)) or (int(resp) < 1):
                    print(col.red("Invalid response"))
                    continue
                else:
                    print(col.blue("Editing week"))
                    self.Weeks[int(resp)-1].collect_trips_info()
                    continue
            elif resp.upper() == 'A':
                print(col.blue("Adding a new week\n"))
                self.add_week()
                continue
            elif resp.upper() == 'D':
                print("Done")
                break
            else:
                print(col.red("Invalid response"))
                continue

    def add_week(self):
        print(col.blue("---- Adding a new week to the carpool ----"))
        self.Weeks.append(WeekClass())
        self.Weeks[-1].init_date_from_user()
        self.Weeks[-1].collect_trips_info()

    def load_weeks(self):
        # Select folder to use
        print('Found the folowing weeks:')
        for root, found_dirs_, found_files_ in os.walk(RESULTS_FOLD_PATH):
            found_dirs = found_dirs_
            break
        for i, carpool in enumerate(found_dirs):
            print(str(i+1) + ') ' + carpool)
        while True:
            resp = input("Select the carpool to load: ")
            if resp.isnumeric() is False:
                print("Invalid response")
                continue
            else:
                choice = int(resp)
                if choice > len(found_dirs):
                    print("Invalid response")
                    continue
                else:
                    print(col.blue("Selected"))
                    folder_to_use = found_dirs[choice-1]
                    break
        # Load the results from it
        FOLDER_TO_USE = os.path.join(RESULTS_FOLD_PATH, folder_to_use)
        for root, found_dirs_, found_files_ in os.walk(FOLDER_TO_USE):
            week_files = found_files_
            break
        for week_file in week_files:
            if week_file.upper().find("DETAILED") == -1:
                continue
            self.Weeks.append(WeekClass())
            self.Weeks[-1].load_from_csv(FOLDER_TO_USE, week_file)
        # Print summary
        print(col.green("Finished loading carpool:"))
        self.calculate()
        self.print_summary()

    def collect_trip_info(self):
        for week in self.Weeks:
            week.collect_trips_info()

    def print_summary(self):
        print(col.blue("\n--- Week summary ---\n"))
        for week in self.Weeks:
            week.print_summary()
        print(col.blue("\n--- Total Summary ---\n"))
        print(self.total_balance)

    def print_current_weeks(self):
        for i, week in enumerate(self.Weeks):
            print("{}) {}".format(i+1, week))

    def calculate(self):
        self.total_balance = Balance()
        for week in self.Weeks:
            week_balance = week.calculate()
            self.total_balance = self.total_balance + week_balance

    def _save(self, folder_path, file_name):
        CSV_PATH = os.path.join(folder_path, file_name + '.csv')
        # Open file and save total summary
        with open(CSV_PATH, 'w') as csvfile:
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
                # Create result name from oldest and newest dates
                earliest_date = oldest_date = self.Weeks[0].date
                for week in self.Weeks:
                    if week.date > oldest_date:
                        oldest_date = week.date
                    if week.date < earliest_date:
                        earliest_date = week.date
                RESULT_NAME = 'SUMMARY_' + str(earliest_date) + '_TO_' + str(oldest_date)
                # Create a folder for it
                if not os.path.exists(RESULTS_FOLD_PATH):
                    os.makedirs(RESULTS_FOLD_PATH)
                NEW_RESULT_FOLD_PATH = os.path.join(RESULTS_FOLD_PATH, RESULT_NAME)
                if not os.path.exists(NEW_RESULT_FOLD_PATH):
                    os.makedirs(NEW_RESULT_FOLD_PATH)
                # Save summary
                self._save(NEW_RESULT_FOLD_PATH, RESULT_NAME)
                # Save every week summary
                for week in self.Weeks:
                    week.save_detailed(NEW_RESULT_FOLD_PATH)
                break
            elif resp.upper() == 'N':
                print(col.yellow("Not saving"))
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

    # User selection Load or start a new carpool
    while True:
        resp = input("What do you want to do? 1) Make a new carpool 2) Load an existing one: ")
        # Add a new carpool
        if resp == '1':
            print(col.blue("Making a new carpool\n"))
            break
        # Load an existing one
        elif resp == '2':
            print(col.blue("Making a new carpool"))
            carpool_calc.load_weeks()
            print(col.blue("Ready to modify it"))
            break
        else:
            print(col.red("Invalid response"))
            continue

    # Edit carpool weeks
    carpool_calc.add_edit_weeks()

    # Calculate and print summary
    carpool_calc.calculate()
    carpool_calc.print_summary()

    # Save
    carpool_calc.save()

    print(col.blue("Exiting"))