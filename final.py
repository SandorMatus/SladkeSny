import json
import os
from datetime import datetime
from FlightRadar24 import FlightRadar24API
import glob  # For file handling

# Function to convert timestamp to formatted date and time
def convert_timestamp(ts):
    if ts is None:
        return (None, None)  # Return None for both date and time if timestamp is null
    try:
        date_time = datetime.utcfromtimestamp(ts)  # Use utcfromtimestamp directly
        formatted_date = date_time.strftime('%d-%b-%Y')  # Format: DD-MMM-YYYY
        formatted_time = date_time.strftime('%H:%M')    # Format: HH:MM
        return (formatted_date, formatted_time)
    except (ValueError, OverflowError):
        return (None, None)  # Return None if the timestamp is invalid

# Main function to process the JSON data for arrivals and departures
def convert(json_data):
    arrivals = json_data['airport']['pluginData']['schedule']['arrivals']['data']
    mock_data = []

    for arrival in arrivals:
        flight = arrival['flight']
        identification = flight['identification']
        status = flight['status']
        aircraft = flight['aircraft']
        owner = flight['owner']
        airport = flight['airport']
        time = flight['time']

        # Get airline information safely
        airline = flight.get('airline')
        if airline is None:
            airline_code = 'Unknown'
            airline_name = 'Unknown'
        else:
            airline_code = airline.get('code', {}).get('iata', 'Unknown')
            airline_name = airline.get('name', 'Unknown')

        # Extracting the arrival date and time
        arrival_date = convert_timestamp(time['scheduled']['arrival'])[0]
        arrival_time_actual = convert_timestamp(time['real']['arrival'])[1]
        arrival_time_scheduled = convert_timestamp(time['scheduled']['arrival'])[1]

        # Extracting the departure date and time
        departure_date = convert_timestamp(time['scheduled']['departure'])[0]
        departure_time_actual = convert_timestamp(time['real']['departure'])[1]
        departure_time_scheduled = convert_timestamp(time['scheduled']['departure'])[1]

        mock_data_arrival = {
            'airline-code': airline_code,
            'airline-name': airline_name,
            'flight-code': identification['number']['default'],
            'departure-airport-code': airport['origin']['code']['iata'],
            'departure-airport-name': airport['origin']['name'],
            'departure-date': departure_date,
            'departure-time-scheduled': departure_time_scheduled,
            'departure-time-actual': departure_time_actual,
            'departure-terminal': airport['origin']['info']['terminal'],
            'departure-gate': airport['origin']['info']['gate'],
            'airplane-manufacturer': aircraft['model']['text'],
            'airplane-type': aircraft['model']['code'],
            'baggage-claim': airport['destination']['info'].get('baggage'),
            'arrival-airport-code': json_data['airport']['pluginData']['details']['code']['iata'],
            'arrival-airport-name': json_data['airport']['pluginData']['details']['name'],
            'arrival-date': arrival_date,
            'arrival-time-scheduled': arrival_time_scheduled,
            'arrival-time-actual': arrival_time_actual,
            'arrival-terminal': airport['destination']['info'].get('terminal'),
            'arrival-gate': airport['destination']['info'].get('gate'),
            'tail-number': aircraft.get('registration')
        }

        mock_data.append(mock_data_arrival)

    # Similar processing for departures
    departures = json_data['airport']['pluginData']['schedule']['departures']['data']
    for departure in departures:
        flight = departure['flight']
        identification = flight['identification']
        status = flight['status']
        aircraft = flight['aircraft']
        owner = flight['owner']
        airport = flight['airport']
        time = flight['time']

        # Get airline information safely
        airline = flight.get('airline')
        if airline is None:
            airline_code = 'Unknown'
            airline_name = 'Unknown'
        else:
            airline_code = airline.get('code', {}).get('iata', 'Unknown')
            airline_name = airline.get('name', 'Unknown')

        # Extracting the arrival date and time
        arrival_date = convert_timestamp(time['scheduled']['arrival'])[0]
        arrival_time_actual = convert_timestamp(time['real']['arrival'])[1]
        arrival_time_scheduled = convert_timestamp(time['scheduled']['arrival'])[1]

        # Extracting the departure date and time
        departure_date = convert_timestamp(time['scheduled']['departure'])[0]
        departure_time_actual = convert_timestamp(time['real']['departure'])[1]
        departure_time_scheduled = convert_timestamp(time['scheduled']['departure'])[1]

        mock_data_departures = {
            'airline-code': airline_code,
            'airline-name': airline_name,
            'flight-code': identification['number']['default'],
            'departure-airport-code': json_data['airport']['pluginData']['details']['code']['iata'],
            'departure-airport-name': json_data['airport']['pluginData']['details']['name'],
            'departure-date': departure_date,
            'departure-time-scheduled': departure_time_scheduled,
            'departure-time-actual': departure_time_actual,
            'departure-terminal': airport['origin']['info']['terminal'],
            'departure-gate': airport['origin']['info']['gate'],
            'airplane-manufacturer': aircraft['model']['text'],
            'airplane-type': aircraft['model']['code'],
            'baggage-claim': airport['destination']['info'].get('baggage'),
            'arrival-airport-code': airport['destination']['code']['iata'],
            'arrival-airport-name':  airport['destination']['name'],
            'arrival-date': arrival_date,
            'arrival-time-scheduled': arrival_time_scheduled,
            'arrival-time-actual': arrival_time_actual,
            'arrival-terminal': airport['destination']['info'].get('terminal'),
            'arrival-gate': airport['destination']['info'].get('gate'),
            'tail-number': aircraft.get('registration')
        }

        mock_data.append(mock_data_departures)

    return mock_data

# Load JSON data from a file
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Write results to a text file
def write_results_to_file(mock_data, output_file_path):
    with open(output_file_path, 'a') as file:
        for entry in mock_data:
            file.write(f"{json.dumps(entry)}\n")  # Write each entry as a new line

# Main execution
if __name__ == "__main__":
    # Create an instance of the API
    fr_api = FlightRadar24API()

    # Fetch initial airport details
    airports = fr_api.get_airport_details("LOWW", 100, 1)

    # Check if the initial API call was successful
    if not airports or 'airport' not in airports or 'pluginData' not in airports['airport']:
        print("Error retrieving airport details.")
        exit(1)

    # Access current total flights
    arrivals = airports.get('airport', {}).get('pluginData', {}).get('schedule', {}).get('arrivals', {}).get('item', {})
    total_flights = arrivals.get('total', 0)

    # Get the current date and format it
    current_date = datetime.now().strftime("%Y-%m-%d")  # Format: YYYY-MM-DD
    folder_name = f'Flights_{current_date}'

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Created directory: {folder_name}")

    i = 1

    while total_flights > 0:
        # Fetch airport details
        airports = fr_api.get_airport_details("LOWW", 100, i)

        # Check and update total flights
        arrivals = airports.get('airport', {}).get('pluginData', {}).get('schedule', {}).get('arrivals', {}).get('item', {})

        # Save the data to a text file in JSON format in the created folder
        file_path = os.path.join(folder_name, f'airports_data_{i}.txt')
        with open(file_path, 'w') as file:
            json.dump(airports, file, indent=4)  # Added indent for pretty printing

        total_flights -= 100
        i += 1

    # Output the total number of flights
    print(f"Current number of flights: {total_flights}")

    # Specify the folder names to process
    output_file_path = 'flights_data_summary.txt'  # Specify your desired output file name

    all_results = []  # To store results from all files

    file_pattern = os.path.join(folder_name, 'airports_data_*.txt')
    
    # Process each file matching the pattern
    for file_path in glob.glob(file_pattern):
        print(f"Processing file: {file_path}")
        json_data = load_json(file_path)
        results = convert(json_data)
        all_results.extend(results)  # Add results from this file to the overall list

    # Write all results to the output file
    write_results_to_file(all_results, output_file_path)
    print(f"Results written to {output_file_path}")
