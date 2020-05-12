from datetime import datetime
import matplotlib.pyplot as plt
import json
import math
import dufte
from si_prefix import si_format

plt.style.use(dufte.style)


def johnshopkins(which):
    # https://github.com/pomber/covid19
    # https://pomber.github.io/covid19/timeseries.json
    with open("timeseries.json") as f:
        data = json.load(f)

    d = {
        key: {
            "dates": [datetime.strptime(val["date"], "%Y-%m-%d") for val in values],
            "values": [val[which] for val in values],
        }
        for key, values in data.items()
    }
    print(d["Germany"]["values"])
    print()
    # convert to new
    for key, dd in d.items():
        new = [b - a for a, b in zip(dd["values"][:-1], dd["values"][1:])]
        d[key] = {
            "dates": dd["dates"][1:],
            "values": new
        }
    return d


d = johnshopkins("confirmed")
# d = johnshopkins("deaths")

plot_keys = [
    # "Austria",
    # "Belgium",
    "Brazil",
    # "Denmark",
    "France",
    "Germany",
    # "Iran",
    "Italy",
    # "Japan",
    # "Netherlands",
    # "Poland",
    # "Portugal",
    "Russia",
    "Spain",
    # "South Korea",
    # "Korea, South",
    # "Sweden",
    # "Switzerland",
    "Turkey",
    "United Kingdom",
    # "United States",
    "US",
]

for key in plot_keys:
    dates = d[key]["dates"]
    values = d[key]["values"]
    # cut off leading zeros
    for k, val in enumerate(values):
        if val > 10:
            break
    dates = dates[k:]
    values = values[k:]

    label = "{} ({})".format(key, si_format(sum(values)))

    plt.plot(dates, values, "-", label=label, linewidth=3.0)

plt.ylim(-100)

# plt.legend()
dufte.legend()
plt.title("daily new COVID-19 infections")
plt.show()
