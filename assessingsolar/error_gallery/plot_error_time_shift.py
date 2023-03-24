"""
Time shift
==========

Time shifts in irradiance data is common, e.g., due daylight savings, incorrect
timezone, or erroneous datalogger timing.
"""

# %%
# Incorrect timezone
# ------------------
# First, let's take an existing dataset and purposefully set an incorrect
# timezone in order to investigate how this can be detected.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pvlib
# sphinx_gallery_thumbnail_number = 2

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

# %%
# Next, let's calculate the Global Horizontal Irradiance (GHI) from Diffuse
# Horizontal Irradiance (DHI) and Direct Normal Irradiance (DNI) using the
# closure equation:
# :math:`GHI = DHI + DNI \cdot \cos(solar\_zenith)`

df['ghi_calc'] = df['dhi'] + df['dni']*np.cos(np.deg2rad(df['zenith']))

# %%
# Then, let's compare the calculated and measured GHI:
df.plot.scatter(x='ghi', y='ghi_calc', s=0.1, alpha=0.1, grid=True)
plt.show()

# %%
# In the above plot, the measured and calculated GHI should ideally lie on a
# straight line. Clearly, this is not the case, but rather there are distinct
# oval features, which is a common indication that the time zone, and thus
# solar angles are incorrect.
#
# To confirm this suspicion, it is useful to generate the same plot as above,
# but with each point colored according to the DNI at that time step. From the
# below plot it can be seen that the calculated and measured GHI match when the
# DNI is zero, i.e., when the calculated GHI is independet of the zenith angle.
fig, ax = plt.subplots()
im = ax.scatter(x=df['ghi'], y=df['ghi_calc'], c=df['dni'], cmap='plasma',
                s=0.1, alpha=0.1)
cbar = fig.colorbar(im)
cbar.solids.set(alpha=1)

# %%
# Hour vs. date heat map
# ----------------------
# Another very useful way of detecting time offset is to visualize the
# irradiance data using a heat map with the hour of day on the y-axis and the
# date on the x-axis. This is particularly useful for longer time series, and
# can provide more information of the time zone offset and potential influence
# of daylight savings.


def plot_hour_date_heatmap(s, sunrise_sunset=True):
    """Plot heatmap with hour on y-axis and date on x-axis."""
    hour_of_day = s.index.hour + s.index.minute/60

    # Create dataframe with rows corresponding to days and columns to hours
    df_2d = s.set_axis([s.index.date, hour_of_day]).unstack(level=0)

    # Calculate the extents of the 2D plot [x_start, x_end, y_start, y_end]
    xlims = [mdates.date2num(df_2d.columns[0]), mdates.date2num(df_2d.columns[-1])]
    extent = xlims + [df_2d.index[0], df_2d.index[-1]]

    # Plot heat map
    fig, ax = plt.subplots(figsize=(6, 2.5))
    im = ax.imshow(df_2d,  aspect='auto', origin='lower', cmap='jet',
                   extent=extent, vmin=0, vmax=1000)

    # Add colorbar
    fig.colorbar(im, ax=ax, orientation='vertical', pad=0.01, label='GHI [W/m$^2$]')

    # Plot sunrise and sunset
    if sunrise_sunset:
        # Calculate sunrise/sunset for the entire period
        days = pd.date_range(s.index[0], s.index[-1])
        sunrise_sunset = location.get_sun_rise_set_transit(days)

        # Convert sunrise/sunset from datetime to decimal hours
        sunrise_sunset['sunrise'] = sunrise_sunset['sunrise'].dt.hour + \
            sunrise_sunset['sunrise'].dt.minute/60
        sunrise_sunset['sunset'] = sunrise_sunset['sunset'].dt.hour + \
            sunrise_sunset['sunset'].dt.minute/60

        ax.plot(mdates.date2num(sunrise_sunset.index),
                sunrise_sunset[['sunrise', 'sunset']].to_numpy(),
                c='r', linestyle='--', lw=2)

    # Format plot
    ax.set_xlim(xlims)
    ax.set_yticks([0, 6, 12, 18, 24])
    ax.set_ylabel('Time of day [h]')
    ax.set_facecolor('grey')
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    plt.show()


plot_hour_date_heatmap(df['ghi'])

# %%
# In the above heat map, the red lines represent sunrise and sunset. It can be
# noted that the non-zero irradiance values are not all contained within the
# daytime period. This is a clear indication that there is an issue with the
# time zone. Shifts in time due to daylight savings are also easily detected
# using this method.

# %%
# Correction
# ----------
# Fortunately, issues with time zones are typically rather easy to fix. In most
# cases it is sufficient to simply choose the correct time zone. Since the
# original data was in UTC, the correct localization would be
# .. ipython::
#
#     df = df.tz_localize('UTC')
#
# %%
# In case that the timestamps include daylights savings, e.g., for Central
# European Time (CET), it may be necessary to utilize ambigious='infer'
# .. ipython::
#
#     df = df.tz_localize('infer', ambiguous='infer')
