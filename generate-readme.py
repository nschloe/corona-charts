import json
import subprocess
import tempfile
from pathlib import Path

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


def get_chartjs_json(infile, selection=None):
    with open(infile) as f:
        d = json.load(f)

    average_over = 7

    plot_keys = get_top(5, d["values"], average_over, selection)

    plot_keys = sort_descending_by_last_average(plot_keys, d["values"], average_over)

    # compute rolling average
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
            "label": key,
            "borderColor": color,
            "fill": False,
            # round to integer for small output files
            # also sanitize negative values
            "data": np.clip(vals.astype(int), 0, None).tolist(),
        }
        for key, vals, color in zip(plot_keys, all_values, colors)
    ]

    # pick out one in seven, starting from the end
    dates = d["dates"][::-1][::7][::-1]
    for dataset in datasets:
        dataset["data"] = dataset["data"][::-1][::7][::-1]

    data = {
        "config": {
            "type": "line",
            "data": {
                "labels": dates,
                "datasets": datasets,
            },
            "options": {
                # don't show markers
                "elements": {"point": {"radius": 0}},
                # show only months
                "scales": {
                    "xAxes": [{"type": "time", "time": {"unit": "month"}}],
                },
            },
        }
    }

    # write dict to file
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        tmpfile = tmpdir / "tmp.json"
        with open(tmpfile, "w") as f:
            json.dump(data, f)
        # run prettier on the file
        subprocess.check_call(["prettier", "--write", str(tmpfile)])
        # get string
        with open(tmpfile) as f:
            json_content = f.read()

    return json_content


def _main():
    top10_confirmed_world = get_chartjs_json(
        "data/time_series_covid19_confirmed_global.json"
    )
    top10_deaths_world = get_chartjs_json("data/time_series_covid19_deaths_global.json")
    european_contries = [
        "Austria",
        "Belgium",
        "Czechia",
        "Denmark",
        "Germany",
        "Greece",
        "France",
        "Ireland",
        "Italy",
        "Netherlands",
        "Poland",
        "Portugal",
        "Spain",
        "Sweden",
        "Switzerland",
        "Czechia",
        "United Kingdom",
    ]
    top10_confirmed_europe = get_chartjs_json(
        "data/time_series_covid19_confirmed_global.json", selection=european_contries
    )
    top10_deaths_europe = get_chartjs_json(
        "data/time_series_covid19_deaths_global.json", selection=european_contries
    )

    with open("README.md.in") as f:
        readme_in = f.read()

    readme_out = readme_in.format(
        top10_confirmed_world=top10_confirmed_world,
        top10_confirmed_europe=top10_confirmed_europe,
        top10_deaths_world=top10_deaths_world,
        top10_deaths_europe=top10_deaths_europe,
    )

    with open("README.md", "w") as f:
        f.write(readme_out)


if __name__ == "__main__":
    _main()
