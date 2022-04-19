import hashlib
import json
from pathlib import Path
from datetime import datetime

import matplotlib.pyplot as plt
import matplotx
import numpy as np


def get_top(k, d, average_over, selection=None):
    if selection is not None:
        d = {key: value for key, value in d.items() if key in selection}

    last_sums = [values[-1] - values[-average_over - 1] for values in d.values()]
    idx = np.argsort(last_sums)
    return [list(d.keys())[i] for i in idx][::-1][:k]


def sort_descending_by_last_average(keys, d, average_over):
    last_sums = [d[key][-1] - d[key][-average_over - 1] for key in keys]
    idx = np.argsort(last_sums)
    return [keys[k] for k in idx][::-1]


def get_color(string: str) -> str:
    return "#" + hashlib.md5(string.encode()).hexdigest()[:6]


def plot_data(infile, selection=None):
    with open(infile) as f:
        d = json.load(f)

    average_over = 7

    plot_keys = get_top(5, d["values"], average_over, selection)

    plot_keys = sort_descending_by_last_average(plot_keys, d["values"], average_over)

    # compute rolling average
    all_values = []
    for key in plot_keys:
        # <https://stackoverflow.com/a/14314054/353337>
        ret = np.copy(d["values"][key])
        ret[average_over:] = ret[average_over:] - ret[:-average_over]
        avg = ret[average_over - 1 :] / average_over
        all_values.append(avg)

    # cut dates accordingly
    d["dates"] = d["dates"][average_over - 1 :]

    dates = [datetime.strptime(dt, "%Y-%m-%d") for dt in d["dates"]]

    # style = matplotx.styles.duftify(matplotx.styles.onedark)
    style = matplotx.styles.dufte
    with plt.style.context(style):
        plt.figure(figsize=(10, 5))
        for key, vals in zip(plot_keys, all_values):
            vals = np.clip(vals, 0, None)
            plt.plot(dates, vals, label=key, color=get_color(key))

        matplotx.line_labels()


def _main():
    data_dir = Path(__file__).resolve().parent / ".." / "data"
    plot_data(data_dir / "time_series_covid19_confirmed_global.json")
    plt.savefig("top5-world-infections.svg", bbox_inches="tight", transparent=True)
    plt.close()

    plot_data(data_dir / "time_series_covid19_deaths_global.json")
    plt.savefig("top5-world-deaths.svg", bbox_inches="tight", transparent=True)
    plt.close()

    european_contries = [
        "Austria",
        "Belarus",
        "Belgium",
        "Bulgaria",
        "Croatia",
        "Czechia",
        "Denmark",
        "Estonia",
        "Germany",
        "Greece",
        "Finland",
        "France",
        "Hungary",
        "Iceland",
        "Ireland",
        "Italy",
        "Latvia",
        "Lithuania",
        "Netherlands",
        "Norway",
        "Poland",
        "Portugal",
        "Romania",
        "Serbia",
        "Spain",
        "Sweden",
        "Switzerland",
        "Czechia",
        "Ukraine",
        "United Kingdom",
    ]
    plot_data(
        data_dir / "time_series_covid19_confirmed_global.json",
        selection=european_contries,
    )
    plt.savefig("top5-europe-infections.svg", bbox_inches="tight", transparent=True)
    plt.close()

    plot_data(
        data_dir / "time_series_covid19_deaths_global.json",
        selection=european_contries,
    )
    plt.savefig("top5-europe-deaths.svg", bbox_inches="tight", transparent=True)
    plt.close()


if __name__ == "__main__":
    _main()
