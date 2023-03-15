# This is a new library for simulated CMB maps.

import os
from os.path import join as opj
import healpy as hp
import numpy as np 

class taylens_sims:
    def __init__(self,fwhm_T, fwhm_P):
        self.cmbs = opj(os.environ["TAY"],'lcmb%03d_3.fits')
        self.noise = opj(os.environ["TAY"],'ffp10_noise_143_full_map_mc_%05d.fits')
        self.fwhm_T = fwhm_T
        self.fwhm_P = fwhm_P

    def hashdict(self):
        return {'cmbs':self.cmbs, 'noise':self.noise, 'data':self.data, 
                'fwhm_T':self.fwhm_T, 'fwhm_P':self.fwhm_P}

    def get_sim_tmap(self, idx):
        r"""Returns temperature map for a simulation

            Args:
                idx: simulation index

            Returns:
                simulation *idx*, including noise

        """
        tmp_m = hp.read_map(self.cmbs % idx, field=0, dtype=np.float64)
        tmp_m = hp.smoothing(tmp_m,fwhm_T)
        return  tmp_m + 1e6*(hp.read_map(self.noise % idx, field=0, dtype=np.float64))

    def get_sim_pmap(self, idx):
        r"""Returns polarization map for a simulation

            Args:
                idx: simulation index

            Returns:
                Q and U simulation *idx*, including noise

        """
        tmp_q = hp.read_map(self.cmbs % idx, field=1, dtype=np.float64)
        rmp_q = hp.smoothing(tmp_q,fwhm_P)
        Q = tmp_q + hp.read_map(self.noise % idx, field=1, dtype=np.float64)
        del tmp_q
        tmp_u = hp.read_map(self.cmbs % idx, field=2, dtype=np.float64)
        tmp_u = hp.smoothing(tmp_u,fwhm_P)
        U = tmp_u + 1e6(hp.read_map(self.noise % idx, field=2, dtype=np.float64))
        
        return Q, U
        
        
