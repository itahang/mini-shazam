import numpy as np
import soundfile
from math import gcd
from scipy import signal

BANDS = [(0, 10), (10, 20), (20, 40), (40, 80), (80, 160), (160, 512)]
TARGET_SR = 11025
NPERSEG = 1024
N_TARGETS = 5
MAX_DT = 16384  


def down_sample(audio, sr, target_sr=TARGET_SR):
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    if sr == target_sr:
        return audio, sr
    g = gcd(target_sr, sr)
    return signal.resample_poly(audio, target_sr // g, sr // g), target_sr


def get_peaks(mag, alpha=1.0):
    """Returns (frames, bins) of the surviving peaks, sorted by frame."""
    n_frames = mag.shape[1]
    win_bins = np.zeros((n_frames, len(BANDS)), dtype=np.int64)
    win_mags = np.zeros((n_frames, len(BANDS)))

    for b, (s, e) in enumerate(BANDS):
        local = np.argmax(mag[s:e, :], axis=0)       # (n_frames,)
        win_bins[:, b] = s + local
        win_mags[:, b] = mag[s + local, np.arange(n_frames)]

    band_means = win_mags.mean(axis=0)               # (6,)
    t_idx, band_idx = np.where(win_mags > alpha * band_means)
    bins = win_bins[t_idx, band_idx]
    return t_idx, bins


def hash_it(segment):
    anchor = segment[0]
    target = segment[1:]
    a_bin = int(anchor[1])
    a_frame = int(anchor[0])

    t_bin = target[:, 1].astype(np.int64)
    dt = target[:, 0].astype(np.int64) - a_frame

    h = (a_bin << 23) | (t_bin << 14) | dt
    valid = (dt > 0) & (dt < MAX_DT)
    return h[valid], a_frame


def fingerprint(path, alpha=1.0):
    """Audio file -> list of (hash, anchor_frame)."""
    audio, sr = soundfile.read(path)
    mono, sr_down = down_sample(audio, sr)

    _, _, Zxx = signal.stft(mono, fs=sr_down, nperseg=NPERSEG, noverlap=0)
    mag = np.abs(Zxx)

    t_idx, bins = get_peaks(mag, alpha)
    pre_hash = np.column_stack([t_idx, bins])

    out = []
    for i in range(len(pre_hash) - N_TARGETS):
        h, a_frame = hash_it(pre_hash[i:i + N_TARGETS + 1])
        out.extend((hv, a_frame) for hv in h.tolist())
    return out

def crop(audio, sr, start_s, duration_s):
    a = int(start_s * sr)
    b = int((start_s + duration_s) * sr)
    return audio[a:b]


def fingerprint_audio(audio,sr, alpha=1.0):
    """Audio file -> list of (hash, anchor_frame)."""
    mono, sr_down = down_sample(audio, sr)

    _, _, Zxx = signal.stft(mono, fs=sr_down, nperseg=NPERSEG, noverlap=0)
    mag = np.abs(Zxx)

    t_idx, bins = get_peaks(mag, alpha)
    pre_hash = np.column_stack([t_idx, bins])

    out = []
    for i in range(len(pre_hash) - N_TARGETS):
        h, a_frame = hash_it(pre_hash[i:i + N_TARGETS + 1])
        out.extend((hv, a_frame) for hv in h.tolist())
    return out

