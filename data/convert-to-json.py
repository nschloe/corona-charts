import csv
import json
from datetime import datetime

roots = [
    "time_series_covid19_confirmed_global",
    "time_series_covid19_deaths_global",
]

for root in roots:
    with open(f"{root}.csv") as f:
        data = [row for row in csv.reader(f)]

    dates = [datetime.strptime(string, "%m/%d/%y") for string in data[0][4:]]

    values = {}
    for row in data[1:]:
        country_name = row[1]
        assert len(row[4:]) == len(dates)
        new_data = [int(string) for string in row[4:]]
        if country_name in values:
            for i in range(len(new_data)):
                values[country_name][i] += new_data[i]
        else:
            values[country_name] = new_data

    with open(f"{root}.json", "w") as f:
        json.dump(
            {"dates": [date.strftime("%Y-%m-%d") for date in dates], "values": values},
            f,
        )
