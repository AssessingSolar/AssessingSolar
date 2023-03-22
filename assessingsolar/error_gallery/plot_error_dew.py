"""
Dew on radiometers
==================

Dew on radiometers cause a deviation of the measured irradiance compared to
the true value.
"""

# %%
# This issue is most often observed during the morning on cold days for
# unventilated and unheated pyranometers.
#
# The issue of dew on pyranometers is illustrated in the image below of a
# shaded and unshaded pyranometer installed at the DTU Climate Station in
# Copenhagen (January 12th 2021).
#
# Note how the shaded pyranometer is covered in dew drops, whereas the unshaded
# is not. The reason for this is that the direct irradiance on the unshaded
# pyranometer has already evaporated the dew on the unshaded pyranometer,
# although this process is not instantaneous and the unshaded pyranometer has
# also been affected for some time during the day.
#
# .. image:: ../graphics/dew_pyranometers_dtu_20210112.jpg
#   :alt: Image of two pyranometers, one with dew and one without.
#   :width: 400
#
# Influence of dew
# ----------------
# Let's take a look at some irradiance measuremens from DTU's Climate Station
# and see if we can observe this pheonmena.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pvlib

filename = '../notebooks/data/solar_irradiance_dtu_2019_extended.csv'
df = pd.read_csv(filename, index_col=0, parse_dates=True)

# Calculate Global Horizontal Irradiance (GHI) from Diffuse Horizontal
# Irradiance (DHI) and Direct Normal Irradiance (DNI) using the closure
# equation.
df['ghi_calc'] = df['dhi'] + df['dni']*np.cos(np.deg2rad(df['zenith']))
df['is_daytime'] = df['zenith'] < 90
df['hourofday'] = df.index.hour

# Compare the calculated and measured GHI:
df.plot.scatter(x='ghi', y='ghi_calc', s=1, alpha=0.5, grid=True)
plt.show()

# %%
# Zooming in at the low irradiance region, it is possible to detect swirling
# lines, where measured GHI is initially higher than GHI_calc and then the
# reverse occurs.
df[df['is_daytime']].plot.scatter(x='ghi', y='ghi_calc', s=1, alpha=0.5,
                                  grid=True, xlim=(-10, 400), ylim=(-10, 400))
plt.show()

# %%
# A closer inspection of the data, let's us find a specific day where this
# phenomena is pronounced. As an example we'll look at May 11th 2019.
df['2019-05-11 03':'2019-05-11 20'].plot.scatter(
    x='ghi', y='ghi_calc', s=1, grid=True, c='hourofday', cmap='plasma',
    sharex=False)
plt.show()

# %%
# From the above plot, it's clear that this phenomena occurs in the morning.
# Let's see if we can also see the issue in the raw measurements for the same
# day:
df.loc['2019-05-11 03':'2019-05-11 20',
       ['dni', 'ghi_calc', 'ghi', 'dhi']].plot(grid=True, alpha=0.5)
plt.show()

# %%
# The wobly nature of the GHI measurements are clearly not realistic and are
# caused by the dew. In the beginning the measured GHI is reduced but then as
# the dew evaporates, more irradiance is focused onto the GHI sensors and the
# measured irradiance is overestimated.

# %%
# Let's attempt to see if we can detect the dewy periods using a traditional
# Kd vs. Kt plot. This type of plot is commonly used in quality assessment
# of irradiance measurements.
df['Kd'] = df['dhi'] / df['ghi']
df['dni_extra'] = pvlib.irradiance.get_extra_radiation(df.index)
df['ghi_extra'] = df['dni_extra'] * np.cos(np.deg2rad(df['zenith']))
df['Kt'] = df['ghi'] / df['ghi_extra']

df['2019-05-11 03':'2019-05-11 20'].plot.scatter(
    x='Kt', y='Kd', grid=True, xlim=(0, 1.1), ylim=(0, 1.1), s=5,
    c='hourofday', cmap='plasma', sharex=False)
plt.show()

# %%
# The morning irradiance measurements effected by dew are within the zone valid
# data, thus this type of plot does not seem to be useful for detecting periods
# with dew.

# %% Pyrheliometers
# Pyrheliometers are much less affected by dew due to the smaller view to the
# sky hemisphere. The rain shield, which is typically mounted on the front of
# a pyrheliometer, also helps reduce the long-wave radiation exchange with the
# sky. Additionally, when there is direct irradiance, the dew on a
# pyrheliometer is typically evaporated before any of the other instruments.
# In short, dew is much more uncommon on pyrheliometers although it can be
# observed.
