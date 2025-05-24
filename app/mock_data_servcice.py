from datetime import datetime, timedelta
import numpy as np
from peewee import chunked, fn
import pandas as pd
from app.data.schemas.solar.solar_schema import SolarInstallation, SiteRefYearProduction
from scipy.interpolate import PchipInterpolator

def backfill_missing_data():

    # Get all active sites with incomplete data
    sites = (SolarInstallation
            .select()
            .where(
                (SolarInstallation.status == 'Active') &
                (SolarInstallation.profile_updated_on.is_null(False)) &
                (SiteRefYearProduction.select(fn.COUNT(SiteRefYearProduction.id))
                                      .where(SiteRefYearProduction.site_id == SolarInstallation.site_id)
                                      < 35040)
            ))

    for site in sites:
        site_id = site.site_id

        existing = (SiteRefYearProduction
                .select()
                .where(SiteRefYearProduction.site_id == site_id)
                .order_by(SiteRefYearProduction.timestamp))

        if not existing:
            continue  # Skip sites with no data

        # Extract timestamps and values
        existing_ts = [rec.timestamp for rec in existing]
        existing_values = [rec.per_kw_generation for rec in existing]

        # Generate full 2001 timeline
        full_timeline = generate_2001_timestamps()

        # Find missing timestamps
        missing_ts = [ts for ts in full_timeline if ts not in existing_ts]

        if not missing_ts:
            continue

        x = np.array([ts.timestamp() for ts in existing_ts])
        y = np.array(existing_values)
        x_new = np.array([ts.timestamp() for ts in missing_ts])
        interpolator = PchipInterpolator(x, y)
        y_new = interpolator(x_new)
        data = []

        for ts, val in zip(missing_ts, y_new):
            interpolated = float(val)
            if not is_daylight(ts):
                interpolated = 0.0
            data.append({
                'site_id': site_id,
                'timestamp': ts,
                'per_kw_generation': interpolated
            })


        for batch in chunked(data, 1000):
            SiteRefYearProduction.insert_many(batch).execute()



def generate_2001_timestamps():
    """Generate all 15-minute intervals for 2001"""
    return [datetime(2001, 1, 1) + timedelta(minutes=15 * i)
            for i in range(35040)]

def is_daylight(ts):
    """Check if the timestamp is between 6:00 AM and 6:45 PM"""
    hour = ts.hour + ts.minute / 60
    return 6 <= hour <= 18.45