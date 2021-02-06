import json
import matplotlib.pyplot as plt
import numpy
import datetime
import time
from read_in_csv import *

# with open('saved_sbb_table.txt', 'r') as file:
#     sbb_data = json.load(file)

intermediate_data_name = 'main_table.csv'

sbb_data = csv_to_dict(intermediate_data_name)
city = []
lat_data = []
lon_data = []
duration = []
for key in sbb_data:
    if sbb_data[key] is not None:
        city.append(key)
        lat_data.append(sbb_data[key][0])
        lon_data.append(sbb_data[key][1])
        duration.append(sbb_data[key][2])
        # duration.append(
        #     sum(x * int(t) for x, t in zip([3600, 60, 1], (sbb_data[key][2].replace('00d', '')).split(":")))
        # )

print(len(lon_data))
# cap_max = int(input('Current maximum is ' + str(max(duration)) + '. Cap maximum at: '))
cap_max = 14400*2.5
print(type(duration))
print(cap_max)
print(type(cap_max))
for i in range(len(duration)):
    if duration[i] > cap_max:
        print(duration[i])
        duration[i] = cap_max
print(max(duration))


plt.scatter(lon_data, lat_data, c=duration, cmap='Set2')
plt.show()

# import matplotlib.pyplot as plt
# import numpy as np
#
# # Fixing random state for reproducibility
# np.random.seed(19680801)
#
#
# N = 100
# r0 = 0.6
# x = 0.9 * np.random.rand(N)
# y = 0.9 * np.random.rand(N)
# area = (20 * np.random.rand(N))**2  # 0 to 10 point radii
# c = np.sqrt(area)
# r = np.sqrt(x ** 2 + y ** 2)
# area1 = np.ma.masked_where(r < r0, area)
# area2 = np.ma.masked_where(r >= r0, area)
# plt.scatter(x, y, s=area1, marker='^', c=c)
# plt.scatter(x, y, s=area2, marker='o', c=c)
# # Show the boundary between the regions:
# theta = np.arange(0, np.pi / 2, 0.01)
# plt.plot(r0 * np.cos(theta), r0 * np.sin(theta))
#
# plt.show()