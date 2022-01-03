import json
import numpy as np
import matplotx
from si_prefix import si_format
import tempfile
import subprocess
from pathlib import Path


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

    plot_keys = get_top(10, d["values"], average_over, selection)

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
            "label": key,
            "borderColor": color,
            "fill": False,
            # round to integer for small output files
            # also sanitize negative values
            "data": np.clip(vals.astype(int), 0, None).tolist(),
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
    top10 = get_chartjs_json("data/time_series_covid19_confirmed_global.json")
    top10_europe = get_chartjs_json(
        "data/time_series_covid19_confirmed_global.json",
        selection=[
            # Europe
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
        ],
    )

    with open("README.md.in") as f:
        readme_in = f.read()

    readme_out = readme_in.format(top10=top10, top10_europe=top10_europe)

    with open("README.md", "w") as f:
        f.write(readme_out)



if __name__ == "__main__":
    _main()
