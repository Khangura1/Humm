"""Audio matching error types"""


class MatchingError(Exception):
    """parent error"""


class WavFormatError(MatchingError):
    """Not reading the right type of file"""


class NotEnoughAudioError(MatchingError):
    """hum is too short, too quiet, or too unclear"""
