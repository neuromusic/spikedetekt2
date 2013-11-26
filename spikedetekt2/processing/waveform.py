"""Alignment routines."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import numpy as np


# -----------------------------------------------------------------------------
# Waveform class
# -----------------------------------------------------------------------------
class Waveform(object):
    def __init__(self, waveforms=None, masks=None, 
                 s_min=None,  # relative to the start of the chunk
                 s_start=None,
                 s_fracpeak=None, ichannel_group=None):
        self.waveforms = waveforms
        self.masks = masks
        self.s_min = s_min  # start of the waveform, relative to the start
                            # of the chunk
        # peak fractional time of the waveform, absolute (relative to the exp)
        self.s_start = s_start
        self.s_fracpeak_abs = s_fracpeak + s_start
        self.ichannel_group = ichannel_group
        
    def __cmp__(self, other):
        return self.s_fracpeak_abs - other.s_fracpeak_abs
        
    def __repr__(self):
        return '<Waveform on channel group {chgrp} at sample {smp}>'.format(
            chgrp=self.ichannel_group,
            smp=self.s_fracpeak_abs
        )


# -----------------------------------------------------------------------------
# Waveform extraction
# -----------------------------------------------------------------------------
def extract_waveform(component, chunk_extract=None,
                     threshold_strong=None, threshold_weak=None, 
                     probe=None, **prm):
    """
    * component: list of (isample, ichannel) pairs.
    * chunk_extract: nsamples x nchannels array
    * chunk_strong: nsamples x nchannels binary array
    * chunk_weak: nsamples x nchannels binary array
    
    """
    component_items = component.items
    s_start = component.s_start
    
    assert len(component_items) > 0
    # Find the channel_group of the spike.
    ichannel_group = probe.channel_to_group[component_items[0][1]]

    # Total number of channels across all channel groups.
    nsamples, nchannels = chunk_extract.shape
    assert nchannels == probe.nchannels
    
    # Get samples and channels in the component.
    if not isinstance(component_items, np.ndarray):
        component_items = np.array(component_items)
    
    # The samples here are relative to the start of the chunk.
    comp_s = component_items[:,0]  # shape: (component_size,)
    comp_ch = component_items[:,1]  # shape: (component_size,)
    
    # Get binary mask.
    masks_bin = np.zeros(nchannels, dtype=np.bool)  # shape: (nchannels,)
    masks_bin[sorted(set(comp_ch))] = 1
    
    # Get the temporal window around the waveform.
    # These values are relative to the start of the chunk.
    s_min, s_max = np.amin(comp_s) - 3, np.amax(comp_s) + 4  
    s_min = max(s_min, 0)
    s_max = min(s_max, nsamples)
    
    # Extract the waveform values from the data.
    # comp shape: (some_length, nchannels)
    # contains the filtered chunk on weak threshold crossings only
    # small temporal window around the waveform
    comp = np.zeros((s_max - s_min, nchannels), dtype=chunk_extract.dtype)
    comp[comp_s - s_min, comp_ch] = chunk_extract[comp_s, comp_ch]
    # the sample where the peak is reached, on each channel, relative to
    # the beginning
    
    # Find the peaks.
    peaks = np.argmax(comp, axis=0) + s_min  # shape: (nchannels,)
    # peak values on each channel
    # shape: (nchannels,)
    peaks_values = chunk_extract[peaks, np.arange(0, nchannels)] * masks_bin
    
    # Compute the float masks.
    masks_float = np.clip(  # shape: (nchannels,)
        (peaks_values - threshold_weak) / (threshold_strong - threshold_weak), 
        0, 1)
    
    # Compute the fractional peak
    power = prm.get('weight_power', 1.)
    comp_normalized = np.clip(
        (comp - threshold_weak) / (threshold_strong - threshold_weak),
        0, 1)
    comp_power = np.power(comp_normalized, power)
    u = np.arange(s_max - s_min)[:,np.newaxis]
    s_fracpeak = np.sum(comp_power * u) / np.sum(comp_power) + s_min
    
    # Realign spike with respect to s_fracpeak
    s_peak = int(s_fracpeak)
    # get block of given size around peaksample
    # WaveBlock = get_padded(FilteredArr,
                           # s_peak-s_before-1, s_peak+s_after+2)
    # # Perform interpolation around the fractional peak
    # old_s = np.arange(s_peak-s_before-1, s_peak+s_after+2)
    # new_s = np.arange(s_peak-s_before, s_peak+s_after)+(s_fracpeak-s_peak)
    # try:
        # f = interp1d(old_s, WaveBlock, bounds_error=True, kind='cubic', axis=0)
    # except ValueError: 
        # raise InterpolationError
    # Wave = f(new_s)
    
    # TODO
    waveforms = None
    masks = None
    
    return Waveform(waveforms=waveforms, masks=masks, 
                    s_min=s_min, s_start=s_start,
                    s_fracpeak=s_fracpeak, ichannel_group=ichannel_group)
    