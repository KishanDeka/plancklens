"""
Taylens simulated maps librabry
"""

import os
from os.path import join as opj
import healpy as hp
import numpy as np


from plancklens import utils

class taylens_cmbs:
    def __init__(self):
        pass

    def hashdict(self):
	return {'sim_lib': 'ffp10 lensed scalar cmb inputs, freq 0'}

    @staticmethod
    def get_sim_tlm(idx):
	"""
	    Args:
	        idx: simulation index

	    Returns:
	        lensed temperature simulation healpy alm array

	"""
	return 1e6 * hp.read_alm(opj(os.environ["CFS"],'cmb/data/generic/cmb/ffp10/mc/scalar/ffp10_lensed_scl_cmb_000_alm_mc_%04d.fits'%idx), hdu=1)

    @staticmethod
    def get_sim_elm(idx):
	"""
	    Args:
	        idx: simulation index

	    Returns:
	        lensed E-polarization simulation healpy alm array

	"""
	return 1e6 * hp.read_alm(opj(os.environ["CFS"],'cmb/data/generic/cmb/ffp10/mc/scalar/ffp10_lensed_scl_cmb_000_alm_mc_%04d.fits'%idx), hdu=2)

    @staticmethod
    def get_sim_blm(idx):
	"""
	    Args:
	        idx: simulation index

	    Returns:
	        lensed B-polarization simulation healpy alm array

	"""
	return 1e6 * hp.read_alm(opj(os.environ["CFS"],'cmb/data/generic/cmb/ffp10/mc/scalar/ffp10_lensed_scl_cmb_000_alm_mc_%04d.fits'%idx), hdu=3)

