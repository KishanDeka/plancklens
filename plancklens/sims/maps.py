from __future__ import print_function

import os
import pickle as pk
import healpy as hp
import numpy as np

from plancklens.utils import clhash, hash_check
from plancklens.helpers import mpi
from plancklens.sims import phas

class cmb_maps(object):
    r"""CMB simulation library combining a lensed CMB library and a transfer function.

        Args:
            sims_cmb_len: lensed CMB library (e.g. *plancklens.sims.planck2018_sims.cmb_len_ffp10*)
            cl_transf: CMB temperature transfer function
            nside: healpy resolution of the maps. Defaults to 2048.
            lib_dir(optional): hash checks will be cached, as well as possibly other things for subclasses.
            cl_transf_P: CMB pol transfer function (if different from cl_transf)

    """
    def __init__(self, sims_cmb_len, cl_transf, nside=2048, cl_transf_P=None, lib_dir=None):
        if cl_transf_P is None:
            cl_transf_P = np.copy(cl_transf)

        self.sims_cmb_len = sims_cmb_len
        self.cl_transf_T = cl_transf
        self.cl_transf_P = cl_transf_P
        self.nside = nside

        if lib_dir is not None:
            fn_hash = os.path.join(lib_dir, 'sim_hash.pk')
            if mpi.rank == 0 and not os.path.exists(fn_hash):
                pk.dump(self.hashdict(), open(fn_hash, 'wb'), protocol=2)
            mpi.barrier()
            hash_check(self.hashdict(), pk.load(open(fn_hash, 'rb')))

    def hashdict(self):
        ret = {'sims_cmb_len':self.sims_cmb_len.hashdict(),'nside':self.nside,'cl_transf':clhash(self.cl_transf_T)}
        if not (np.all(self.cl_transf_P == self.cl_transf_T)):
            ret['cl_transf_P'] = clhash(self.cl_transf_P)
        return ret

    def get_sim_tmap(self,idx):
        """Returns temperature healpy map for a simulation

            Args:
                idx: simulation index

            Returns:
                healpy map

        """
        tmap = self.sims_cmb_len.get_sim_tlm(idx)
        hp.almxfl(tmap,self.cl_transf_T,inplace=True)
        tmap = hp.alm2map(tmap,self.nside)
        return tmap + self.get_sim_tnoise(idx)

    def get_sim_pmap(self,idx):
        """Returns polarization healpy maps for a simulation

            Args:
                idx: simulation index

            Returns:
                Q and U healpy maps

        """
        elm = self.sims_cmb_len.get_sim_elm(idx)
        hp.almxfl(elm,self.cl_transf_P,inplace=True)
        blm = self.sims_cmb_len.get_sim_blm(idx)
        hp.almxfl(blm, self.cl_transf_P, inplace=True)
        Q,U = hp.alm2map_spin([elm,blm], self.nside, 2,hp.Alm.getlmax(elm.size))
        del elm,blm
        return Q + self.get_sim_qnoise(idx),U + self.get_sim_unoise(idx)

    def get_sim_tnoise(self,idx):
        assert 0,'subclass this'

    def get_sim_qnoise(self, idx):
        assert 0, 'subclass this'

    def get_sim_unoise(self, idx):
        assert 0, 'subclass this'

class cmb_maps_noisefree(cmb_maps):
    def __init__(self,sims_cmb_len,cl_transf,nside=2048, cl_transf_P=None):
        super(cmb_maps_noisefree, self).__init__(sims_cmb_len, cl_transf, nside=nside, cl_transf_P=cl_transf_P)

    def get_sim_tnoise(self,idx):
        return np.zeros(hp.nside2npix(self.nside))

    def get_sim_qnoise(self, idx):
        return np.zeros(hp.nside2npix(self.nside))

    def get_sim_unoise(self, idx):
        return np.zeros(hp.nside2npix(self.nside))

class cmb_maps_nlev(cmb_maps):
    r"""CMB simulation library combining a lensed CMB library, transfer function and idealized homogeneous noise.

        Args:
            sims_cmb_len: lensed CMB library (e.g. *plancklens.sims.planck2018_sims.cmb_len_ffp10*)
            cl_transf: CMB transfer function, identical in temperature and polarization
            nlev_t: temperature noise level in :math:`\mu K`-arcmin
            nlev_p: polarization noise level in :math:`\mu K`-arcmin
            nside: healpy resolution of the maps
            lib_dir(optional): noise maps random phases will be cached there. Only relevant if *pix_lib_phas is not set*
            pix_lib_phas(optional): random phases library for the noise maps (from *plancklens.sims.phas.py*).
                                    If not set, *lib_dir* arg must be set.


    """
    def __init__(self,sims_cmb_len, cl_transf, nlev_t, nlev_p, nside, lib_dir=None, pix_lib_phas=None):
        if pix_lib_phas is None:
            assert lib_dir is not None
            pix_lib_phas = phas.pix_lib_phas(lib_dir, 3, (hp.nside2npix(nside),))
        assert pix_lib_phas.shape == (hp.nside2npix(nside),), (pix_lib_phas.shape, (hp.nside2npix(nside),))
        self.pix_lib_phas = pix_lib_phas
        self.nlev_t = nlev_t
        self.nlev_p = nlev_p

        super(cmb_maps_nlev, self).__init__(sims_cmb_len, cl_transf, nside=nside, lib_dir=lib_dir)


    def hashdict(self):
        ret = {'sims_cmb_len':self.sims_cmb_len.hashdict(),
                'nside':self.nside,'cl_transf':clhash(self.cl_transf_T),
                'nlev_t':self.nlev_t,'nlev_p':self.nlev_p, 'pixphas':self.pix_lib_phas.hashdict()}
        if not (np.all(self.cl_transf_P == self.cl_transf_T)):
            ret['cl_transf_P'] = clhash(self.cl_transf_P)
        return ret

    def get_sim_tnoise(self,idx):
        """Returns noise temperature map for a simulation

            Args:
                idx: simulation index

            Returns:
                healpy map

        """
        vamin = np.sqrt(hp.nside2pixarea(self.nside, degrees=True)) * 60
        return self.nlev_t / vamin * self.pix_lib_phas.get_sim(idx, idf=0)

    def get_sim_qnoise(self, idx):
        """Returns noise Q-polarization map for a simulation

            Args:
                idx: simulation index

            Returns:
                healpy map

        """
        vamin = np.sqrt(hp.nside2pixarea(self.nside, degrees=True)) * 60
        return self.nlev_p / vamin * self.pix_lib_phas.get_sim(idx, idf=1)

    def get_sim_unoise(self, idx):
        """Returns noise U-polarization map for a simulation

            Args:
                idx: simulation index

            Returns:
                healpy map

        """
        vamin = np.sqrt(hp.nside2pixarea(self.nside, degrees=True)) * 60
        return self.nlev_p / vamin * self.pix_lib_phas.get_sim(idx, idf=2)




