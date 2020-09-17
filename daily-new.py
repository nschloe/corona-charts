from datetime import datetime
import matplotlib.pyplot as plt
import json
import numpy
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
    # convert to new
    for key, dd in d.items():
        new = [b - a for a, b in zip(dd["values"][:-1], dd["values"][1:])]
        d[key] = {"dates": dd["dates"][1:], "values": new}
    return d


def get_top10(d, average_over):
    last_averages = [
        sum(item["values"][-average_over:]) / average_over for item in d.values()
    ]
    idx = numpy.argsort(last_averages)
    return [list(d.keys())[i] for i in idx][::-1][:10]


def sort_descending_by_last_average(keys, d, average_over):
    last_averages = [
        sum(d[key]["values"][-average_over:]) / average_over for key in keys
    ]
    idx = numpy.argsort(last_averages)
    return [keys[k] for k in idx][::-1]


def _main():
    d = johnshopkins("confirmed")
    # d = johnshopkins("deaths")

    average_over = 7

    # plot_keys = get_top10(d, average_over)
    # Europe
    plot_keys = [
        "Germany",
        "France",
        "Spain",
        "Austria",
        "Switzerland",
        "Netherlands",
        "Sweden",
        "Italy",
        "United Kingdom",
        "Belgium",
        "Poland"
        # "Denmark",
        # "Greece",
    ]

    plot_keys = sort_descending_by_last_average(plot_keys, d, average_over)

    for idx, key in enumerate(plot_keys):
        dates = d[key]["dates"]
        values = d[key]["values"]

        # compute rolling sum over the last 7 days
        values = numpy.array(values)
        avg = numpy.zeros(len(values) - average_over + 1)
        for k in range(average_over):
            avg += values[k : len(values) - average_over + k + 1]
        avg /= average_over

        dates = dates[average_over - 1 :]
        values = avg

        # cut off leading zeros
        for k, val in enumerate(values):
            if val > 10:
                break
        dates = dates[k:]
        values = values[k:]

        label = "{} ({})".format(key, si_format(sum(values)))

        plt.plot(dates, values, "-", label=label, linewidth=3.0, zorder=len(plot_keys) - idx)

    plt.ylim(0)

    # plt.legend()
    dufte.legend()
    plt.title(f"daily new COVID-19 infections (avg last {average_over} days)")
    plt.show()


if __name__ == "__main__":
    _main()
