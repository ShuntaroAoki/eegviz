import os

import mne
import numpy as np
import pandas as pd


__all__ = ['EvData']


class EvData(object):
    def __init__(self, fname=None):
        self.__fname = fname
        self.__mneraw = None

        self.__ch    = None
        self.__times = None
        self.__tmax  = None
        self.__tmin  = None
        self.__sf    = None

        self.__events_df = None

        if self.__fname is not None:
            self.__mneraw = self.__load_from_file(self.__fname)

            self.__ch    = self.__mneraw.ch_names
            self.__times = self.__mneraw.times
            self.__tmax  = max(self.__times)
            self.__tmin  = min(self.__times)
            self.__sf    = self.__mneraw.info['sfreq']

            self.__events_df = parse_annotation(list(self.__mneraw.annotations))

    @property
    def channels(self):
        return self.__ch

    @property
    def times(self):
        return self.__times

    @property
    def sampling_frequency(self):
        return self.__sf

    @property
    def event_names(self):
        return list(self.__events_df['description'].unique())

    @property
    def events_dataframe(self):
        return self.__events_df

    @property
    def channel_unit(self):
        chinfo = self.__mneraw.info['chs']
        chunit = {c['ch_name']: unit_fiff_to_human(c['unit']) for c in chinfo}
        return chunit

    @property
    def channel_unit_multiplier(self):
        chinfo = self.__mneraw.info['chs']
        chumul = {c['ch_name']: int(c['unit_mul']) for c in chinfo}
        return chumul

    @property
    def _mne_raw(self):
        return self.__mneraw

    def get_data(self, period=None, channel=None, return_times=False, verbose=False):
        '''Returns EEG data.

        Parameters
        ----------
        period : list, None
            Time period to be included (in sec.). Default (None): all.

        channel : str, list, slice, None
            Channel(s) to be included. Default (None): all channels.

        return_times : bool
            Returns times or not.

        verbose : bool
            Ouputs verbose messages or not.

        Returns
        -------
        data : ndarray, shape = (n_channels, n_times)
        times : ndarray, shape = (n_times,), optional
        '''

        if period is None:
            return self.__mneraw.get_data(picks=channel, return_times=return_times, verbose=verbose)
        else:
            tmin = max([period[0], self.__tmin])
            tmax = min([period[1], self.__tmax])

            min_ind = np.argmin(np.abs(self.times - tmin))
            max_ind = np.argmin(np.abs(self.times - tmax))

            if period[1] > self.__tmax:
                max_ind = None

            return self.__mneraw.get_data(picks=channel, start=min_ind, stop=max_ind, return_times=return_times, verbose=verbose)

    def get_data_by_event(self, event_name, pre=1, post=1, channel=None, return_times=False, verbose=False):
        '''Returns EEG data around given event.

        Parameters
        ----------
        event_name : str
            Event name.

        pre, post : int, float
            Time duration before and after the event to be included.

        channel : str, list, slice, None
            Channel(s) to be included. Default (None): all channels.

        return_times : bool
            Returns times or not.

        verbose : bool
            Ouputs verbose messages or not.

        Returns
        -------
        data_list : list
            List of ndarrays or tuples.
        '''

        ev_onsets    = self.get_event_onset_time(event_name)
        ev_durations = self.get_event_duration(event_name)

        datas = []

        for onset, duration in zip(ev_onsets, ev_durations):
            tmin = max([onset - pre, self.__tmin])
            tmax = min([onset + duration + post, self.__tmax])

            d = self.get_data(channel=channel, period=[tmin, tmax], return_times=return_times, verbose=verbose)
            datas.append(d)

        return datas

    def get_event_onset_time(self, event_name):
        '''Returns onset times of given event.'''
        return list(self.__events_df.query('description == "{}"'.format(event_name))['onset'])

    def get_event_duration(self, event_name):
        '''Returns durations of given event.'''
        return list(self.__events_df.query('description == "{}"'.format(event_name))['duration'])

    def get_event_timestamp(self, event_name):
        '''Returns timestamps of given event.'''
        return list(self.__events_df.query('description == "{}"'.format(event_name))['orig_time'])

    def __load_from_file(self, fname):
        ext = os.path.splitext(fname)[1]
        if ext == '.vhdr':
            print('Loading {} with mne.io.read_raw_brainvision'.format(fname))
            return mne.io.read_raw_brainvision(fname)
        elif ext == '.edf':
            print('Loading {} with mne.io.read_raw_edf'.format(fname))
            return mne.io.read_raw_edf(fname)

        else:
            raise ValueError('Unknown file type: {}'.format(ext))


def parse_annotation(annot):
    '''Parses MNE annotations and returns them as a Pandas dataframe.'''
    events_df = pd.DataFrame(columns=['onset', 'duration', 'description', 'orig_time'])
    for a in annot:
        events_df = pd.concat([events_df, pd.DataFrame(a, index=[0])], ignore_index=True)
    return events_df


def unit_fiff_to_human(unit):
    '''Convert FIFF unit code to human readable form.'''

    table = {
        -1: "<No unit>",
        0: "unitless",
        1: "meter",
        2: "kilogram",
        3: "second",
        4: "ampere",
        5: "Kelvin",
        6: "mole",
        7: "radian",
        8: "steradian",
        9: "candela",
        10: "mol/m^3",
        101: "herz",
        102: "Newton",
        103: "pascal",
        104: "joule",
        105: "watt",
        106: "coulomb",
        107: "volt",
        108: "farad",
        109: "ohm",
        110: "one per ohm",
        111: "weber",
        112: "tesla",
        113: "Henry",
        114: "celcius",
        115: "lumen",
        116: "lux",
        117: "V/m^2",
        201: "T/m",
        202: "Am",
        203: "Am/m^2",
        204: "Am/m^3",
    }
    return table[int(unit)]
