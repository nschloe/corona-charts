from datetime import datetime
import matplotlib.pyplot as plt
import json
import numpy as np
import pprint
import matplotx
from si_prefix import si_format

plt.style.use(matplotx.styles.dufte)


def read_data():
    with open("data/time_series_covid19_confirmed_global.json") as f:
        data = json.load(f)

    return data


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


def _main():
    # tpe = "confirmed"
    # tpe = "deaths"

    d = read_data()
    average_over = 7

    plot_keys = get_top(
        3,
        d["values"],
        average_over,
        # [
        #     # Europe
        #     "Austria",
        #     "Belgium",
        #     "Czechia",
        #     "Denmark",
        #     "Germany",
        #     "Greece",
        #     "France",
        #     "Ireland",
        #     "Italy",
        #     "Netherlands",
        #     "Poland",
        #     "Portugal",
        #     "Spain",
        #     "Sweden",
        #     "Switzerland",
        #     "Czechia",
        #     "United Kingdom",
        # ],
    )

    plot_keys = sort_descending_by_last_average(plot_keys, d["values"], average_over)

    # compute rolling average over the last n days
    all_values = []
    for idx, key in enumerate(plot_keys):
        # <https://stackoverflow.com/a/14314054/353337>
        ret = np.copy(d["values"][key])
        ret[average_over:] = ret[average_over:] - ret[:-average_over]
        avg = ret[average_over - 1 :] / average_over
        all_values.append(avg)

    colors = matplotx.styles.dracula["axes.prop_cycle"].by_key()["color"]

    datasets = [
        {
            "data": vals.tolist(),
            "label": key,
            "borderColor": color,
            "fill": False,
        }
        for key, vals, color in zip(plot_keys, all_values, colors)
    ]

    data = {
        "config": {
            "type": "line",
            "data": {
                "labels": d["dates"],
                "datasets": datasets,
            },
            "options": {
                "title": {
                    "display": True,
                    "text": f"Daily new COVID cases by country (avg last {average_over} days)",
                },
                "elements": {"point": {"radius": 0}},
            },
        }
    }

    with open("README.md", "w") as f:
        f.write("```chartjs\n")
        json.dump(data, f, indent=2)
        f.write("\n```\n")


if __name__ == "__main__":
    _main()
