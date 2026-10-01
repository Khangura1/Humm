
import numpy as np


from matching.contour import hz_to_midi


def test_hz_to_midi():
    assert hz_to_midi(np.array([440.0])) == 69.0  # 440 hz = 69 midi notes
    assert (
        hz_to_midi(np.array([880.0])) == 81.0
    )  # 880 hz = one octave up =  81 midi notes
    assert (
        hz_to_midi(np.array([220.0])) == 57.0
    )  # 220 hz = one octave down = 57 midi notes
    assert np.isnan(hz_to_midi(np.array([np.nan])))  # nan input should return nan
