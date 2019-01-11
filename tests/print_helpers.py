from datetime import datetime


def print_data_sources(data_sources):
    for source in data_sources:
        print("Data source: " + source['dataStreamId'])
        print("Type: " + source['dataType']['name'])
        for field in source['dataType']['field']:
            print("  - {}: {} {}".format(
                field['format'],
                field['name'],
                "(optional)" if 'optional' in field and field['optional'] else ""))
        if 'application' in source:
            if 'packageName' in source['application']:
                print("App: " + source['application']['packageName'])
            if 'name' in source['application']:
                print("Application name: " + source['application']['name'])
        if 'device' in source:
            print("Gerät: {} - {} (Typ: {} mit uid: {})".format(
                source['device']['manufacturer'],
                source['device']['model'],
                source['device']['type'],
                source['device']['uid']))
        print("---------------------------------------------")


def print_workouts(workouts):
    for workout in workouts:
        print("- {} ({} - {})".format(
            workout['activity'],
            str(workout['start_time']),
            str(workout['end_time'])))


def print_weights(weights):
    for weight in weights:
        print("Gewicht {}kg am {}.".format(
           weight['weight'],
           str(weight['time'])))


def print_birthday_data(raw_birthday_data):
    for entry in raw_birthday_data['point']:
        bd = datetime.fromtimestamp(entry['value'][0]['intVal'])
        print(" - {}: {}.{}.{}".format(datetime.fromtimestamp(int(entry["startTimeNanos"]) / 1000000000),
                                       bd.day, bd.month, bd.year))


def print_nutrient_meal_days(days):
    for i, day in enumerate(days):
        print("== Tag {} ==".format(i))
        for meal in day:
            print(meal['name'] + ':')
            for item in meal['items']:
                print(" - {}: {}kcal ({})".format(item['name'], item['calories'] if 'calories' in item else '--',
                                                   item['end_time']))
