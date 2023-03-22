"""
Time shift
==========

Time shifts in irradiance data is common, e.g., due daylight savings, incorrect
timezone, or drift in datalogger timing.
"""

# %%
# Incorrect timezone
# ----------------
# First, let's take an existing dataset and purposefully set an incorrect
# timezone in order to investigate how this can be detected.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pvlib

filename = '../notebooks/data/solar_irradiance_dtu_2019_extended.csv'
df = pd.read_csv(filename, index_col=0, parse_dates=True)

# Remove timezone information
df = df.tz_convert(None)

# Set incorrect timezone
df = df.tz_localize('Etc/GMT-4', ambiguous='NaT', nonexistent='NaT')

# Calculate solar position using pvlib
location = pvlib.location.Location(latitude=55.7906, longitude=12.5253)
solpos = location.get_solarposition(df.index)
df['zenith'] = solpos['apparent_zenith']

# Calculate Global Horizontal Irradiance (GHI) from Diffuse Horizontal
# Irradiance (DHI) and Direct Normal Irradiance (DNI) using the closure
# equation.
df['ghi_calc'] = df['dhi'] + df['dni']*np.cos(np.deg2rad(df['zenith']))

# Compare the calculated and measured GHI:
df.plot.scatter(x='ghi', y='ghi_calc', s=0.1, alpha=0.1, grid=True)
plt.show()

# %%
# In the above plot the measured and calculated GHI should ideally lie on a
# stright line. Clearly this is not the case, but rather there are distinct
# oval features, which is a common indication that the timezone is incorrect.

# %%
# 2-D heat map visualization
# --------------------------
# Another very useful way of detecting time offset is to visualize the
# irradiance data using a heat map with the hour of day on the y-axis and the
# date on the x-axis.


# Calculate sunrise/sunset for the entire period
days = pd.date_range(df.index[0], df.index[-1])
sunrise_sunset = location.get_sun_rise_set_transit(days)

# Convert sunrise/sunset from datetime to decimal hours
sunrise_sunset['sunrise'] = sunrise_sunset['sunrise'].dt.hour + \
    sunrise_sunset['sunrise'].dt.minute/60
sunrise_sunset['sunset'] = sunrise_sunset['sunset'].dt.hour + \
    sunrise_sunset['sunset'].dt.minute/60

df['hourofday'] = df.index.hour + df.index.minute/60

# Create dataframe with rows corresponding to days and columns to hours
df_2d = df[['ghi']].set_index([df.index.date, df.hourofday]).unstack(level=0)

# Calculate the extents of the 2D plot [x_start, x_end, y_start, y_end]
xlims = mdates.date2num([df.index[0].date(), df.index[-1].date()])
extent = [xlims[0], xlims[1], 0, 24]

# Plot heat map
fig, ax = plt.subplots()
im = ax.imshow(df_2d['ghi'],  aspect='auto', origin='lower', cmap='jet',
               extent=extent, vmin=0, vmax=1000)

# Plot sunrise and sunset
ax.plot(mdates.date2num(sunrise_sunset.index),
        sunrise_sunset[['sunrise', 'sunset']].to_numpy(),
        c='r', linestyle='--', lw=2)

# Add colorbar
cbar = fig.colorbar(im, ax=ax, orientation='vertical', pad=0.01, label='GHI [W/m$^2$]')

# Format plot
ax.set_xlim(xlims)
ax.set_yticks([0, 6, 12, 18, 24])
ax.set_ylabel('Time of day [h]')
ax.set_facecolor('grey')
ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

plt.show()

# %%
# In the above heat map the red lines represents sunrise and sunset times. It
# can be noted that the non-zero irradiance values are not all contained
# within the daytime period (between sunrise and sunset). This, is a clear
# indication that there is a timezone offset. Shifts in time due to daylight
# savings can also be detected using this method.
