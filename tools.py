from datetime import timedelta

import pandas as pd
from stravalib import Client as StravaClient
from stravalib.protocol import ApiV3


STREAM_TYPES = [
    'time', 'latlng', 'distance', 'altitude', 'velocity_smooth','heartrate',
    'cadence', 'watts', 'temp', 'moving', 'grade_smooth'
]


class Client(StravaClient):
    """
    Thin wrapper around the stravalib client that adds a bit more ease of use
    but *should* be compatible in every way.
    """
    def exchange_code_for_token(self, *args, **kwargs):
        token = super().exchange_code_for_token(*args, **kwargs)
        self = Client(access_token=token['access_token'])
        # self.protocol = ApiV3(access_token=token['access_token'])

    def get_last_activity(self):
        generator = self.get_activities(limit=1)
        return next(generator)

    def get_activity_streams_dataframe(self, *args, start_date=None, **kwargs):
        if len(args) < 2 and 'types' not in kwargs:
            kwargs['types'] =  STREAM_TYPES
        if len(args) < 4 and 'series_type' not in kwargs:
            kwargs['series_type'] =  'time'
        
        streams = self.get_activity_streams(*args, **kwargs)
        df = pd.DataFrame({key: streams[key].data for key in streams})

        df = df.rename(
            index=str,
            columns={
                'watts': 'power',
                'velocity_smooth': 'speed',
                'temp': 'temperature',
                'grade_smooth': 'gradient'
            }
        )
        df['time'] = df['time'].apply(lambda t: start_date + timedelta(seconds=t))
        df = df.set_index('time')

        return df
