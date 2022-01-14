import math
import torch

import amfm_decompy.basic_tools as basic
import amfm_decompy.pYAAPT as pYAAPT_np


def pYAAPT(
    waveform,
    sample_rate,
    fmin=60,
    fmax=400,
    frame_length=400,
    hop_length=200,
    interpolated=False,
):
    """pyaapt uses time in ms to define frame_length, frame_space"""

    n_frames = math.ceil(waveform.shape[-1] / hop_length)

    flength = int(1000 * frame_length / sample_rate)
    hlength = int(1000 * hop_length / sample_rate)

    def _pyaapt(waveform):
        if isinstance(waveform, torch.Tensor):
            waveform = waveform.numpy()

        signal = basic.SignalObj(
            data=waveform,
            fs=sample_rate,
        )
        f = pYAAPT_np.yaapt(
            signal,
            f0_min=fmin,
            f0_max=fmax,
            frame_length=flength,
            frame_space=hlength,
            fft_length=frame_length,
        )
        vuv = torch.from_numpy(f.vuv).float()
        if interpolated:
            f = f.samp_interp
        else:
            f = f.samp_values

        f = torch.from_numpy(f).float()
        if len(f) != n_frames:
            n_diff = n_frames - len(f)
            if interpolated:
                diff = torch.ones((n_diff,)) * f[..., -1]
            else:
                diff = torch.zeros((n_diff,))
            f = torch.cat((f, diff))
            vuv = torch.cat(
                (
                    vuv,
                    torch.zeros(
                        n_diff,
                    ).bool(),
                )
            )
        return f, vuv

    if waveform.ndim == 1:
        return _pyaapt(waveform)
    f0, vuv = [], []
    for x in waveform:
        f_, vuv_ = _pyaapt(x)
        f0.append(f_)
        vuv.append(vuv_)
    return torch.stack(f0), torch.stack(vuv)
