import json
import math

import dufte
import matplotlib.pyplot as plt
from si_prefix import si_format

plt.style.use(dufte.style)


def johnshopkins(which):
    # https://github.com/pomber/covid19
    # https://pomber.github.io/covid19/timeseries.json
    with open("timeseries.json") as f:
        data = json.load(f)

    return {key: [val[which] for val in values] for key, values in data.items()}


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

ref = 100


# x1 = 24
# x = [0, x1]
# alpha = math.log(2) / 2
# values = [ref, ref * math.exp(alpha * x1)]
# plt.semilogy(x, values, "k--", label="Doubling every 2 days", linewidth=0.5)
#
# x1 = 36
# x = [0, x1]
# alpha = math.log(2) / 3
# values = [ref, ref * math.exp(alpha * x1)]
# plt.semilogy(x, values, "k--", label="Doubling every 3 days", linewidth=0.5)
#
# x1 = 44
# x = [0, x1]
# alpha = math.log(2) / 4
# values = [ref, ref * math.exp(alpha * x1)]
# plt.semilogy(x, values, "k--", label="Doubling every 4 days", linewidth=0.5)

# x = [0, x1]
# alpha = math.log(2) / 4
# values = [ref, ref * math.exp(alpha * x1)]
# plt.semilogy(x, values, "k--", label="Doubling every 4 days", linewidth=0.5)


for key in plot_keys:
    values = d[key]
    # cut off leading zeros
    for k, val in enumerate(values):
        if val > 0:
            break
    values = values[k:]

    log_values = [math.log(val) for val in values]
    for k, val in enumerate(values):
        if val > ref:
            break

    # interpolate
    # (1 - t) * log_values[k - 1] + t * log_values[k] == log(100)
    t = (math.log(ref) - log_values[k - 1]) / (log_values[k] - log_values[k - 1])

    values = [ref] + values[k:]
    x = [0] + [1 - t + i for i in range(len(values) - 1)]

    # compute doubling period
    # if values[-1] > values[-2]:
    #     doubling_period = math.log(2) / math.log(values[-1] / values[-2])
    #     label = "{} ({:.2f})".format(key, doubling_period)
    # else:
    #     label = key
    label = "{} ({})".format(key, si_format(values[-1]))

    plt.semilogy(x, values, "-", label=label, linewidth=3.0)
    # plt.plot(x, values, "-", label=label, linewidth=3.0)

# plt.legend()
dufte.legend()
plt.title("confirmed COVID-19 infections")
plt.xlabel(f"days since passing {ref} cases")
plt.show()
