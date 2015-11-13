from __future__ import print_function
import os

from .bgwtask  import BGWTask
from .kgrid    import get_kpt_grid
from .inputs   import SigmaInput

# Public
__all__ = ['SigmaTask']


class SigmaTask(BGWTask):
    """Self-energy calculation."""

    _TASK_NAME = 'Sigma task'

    _input_fname  = 'sigma.inp'
    _output_fname = 'sigma.out'

    def __init__(self, dirname, **kwargs):
        """
        Arguments
        ---------

        dirname : str
            Directory in which the files are written and the code is executed.
            Will be created if needed.


        Keyword arguments
        -----------------
        (All mandatory unless specified otherwise)

        structure : pymatgen.Structure
            Structure object containing information on the unit cell.
        ngkpt : list(3), float
            K-points grid. Number of k-points along each primitive vector
            of the reciprocal lattice.
        qshift : list(3), float
            Q-point used to treat the Gamma point.
        ibnd_min : int
            Minimum band index for GW corrections.
        ibnd_max : int
            Maximum band index for GW corrections.
        wfn_co_fname : str
            Path to the wavefunction file produced by pw2bgw.
        rho_fname : str
            Path to the density file produced by pw2bgw.
        vxc_fname : str
            Path to the vxc file produced by pw2bgw.
        eps0mat_fname : str
            Path to the eps0mat file produced by epsilon.
        epsmat_fname : str
            Path to the epsmat file produced by epsilon.
        extra_lines : list, optional
            Any other lines that should appear in the input file.
        extra_variables : dict, optional
            Any other variables that should be declared in the input file.


        Properties
        ----------

        sigma_fname : str
            Path to the sigma_hp.log file produced.

        eqp0_fname : str
            Path to the eqp0.dat file produced.

        eqp1_fname : str
            Path to the eqp1.dat file produced.

        """

        super(SigmaTask, self).__init__(dirname, **kwargs)

        # Compute k-points grids
        # Maybe I should make these properties...
        structure = kwargs.pop('structure')
        ngkpt = kwargs['ngkpt']
        kpts_ush, wtks_ush = get_kpt_grid(structure, ngkpt)

        extra_lines = kwargs.get('extra_lines',[])
        extra_variables = kwargs.get('extra_variables',{})

        # Input file
        self.input = SigmaInput(
            kwargs['ibnd_min'],
            kwargs['ibnd_max'],
            kpts_ush,
            *extra_lines,
            **extra_variables)

        self.input.fname = self._input_fname

        # Set up the run script
        self.wfn_co_fname = kwargs['wfn_co_fname']
        self.rho_fname = kwargs['rho_fname']
        self.vxc_fname = kwargs['vxc_fname']
        self.eps0mat_fname = kwargs['eps0mat_fname']
        self.epsmat_fname = kwargs['epsmat_fname']

        self.runscript['SIGMA'] = 'sigma.cplx.x'
        self.runscript['SIGMAOUT'] = self._output_fname
        self.runscript.append('$MPIRUN $SIGMA &> $SIGMAOUT')

    @property
    def wfn_co_fname(self):
        return self._wfn_co_fname

    @wfn_co_fname.setter
    def wfn_co_fname(self, value):
        self._wfn_co_fname = value
        self.update_link(value, 'WFN_inner')

    @property
    def rho_fname(self):
        return self._rho_fname

    @rho_fname.setter
    def rho_fname(self, value):
        self._rho_fname = value
        self.update_link(value, 'RHO')

    @property
    def vxc_fname(self):
        return self._vxc_fname

    @vxc_fname.setter
    def vxc_fname(self, value):
        self._vxc_fname = value
        self.update_link(value, 'vxc.dat')

    @property
    def eps0mat_fname(self):
        return self._eps0mat_fname

    @eps0mat_fname.setter
    def eps0mat_fname(self, value):
        self._eps0mat_fname = value
        dest = 'eps0mat'
        if value.endswith('.h5'):
            dest += '.h5'
        self.update_link(value, dest)

    @property
    def epsmat_fname(self):
        return self._epsmat_fname

    @epsmat_fname.setter
    def epsmat_fname(self, value):
        self._epsmat_fname = value
        dest = 'epsmat'
        if value.endswith('.h5'):
            dest += '.h5'
        self.update_link(value, dest)

    def write(self):
        super(SigmaTask, self).write()
        with self.exec_from_dirname():
            self.input.write()

    @property
    def sigma_fname(self):
        """Path to the sigma_hp.log file produced."""
        return os.path.join(self.dirname, 'sigma_hp.log')
    
    @property
    def eqp0_fname(self):
        """Path to the eqp0.dat file produced."""
        return os.path.join(self.dirname, 'eqp0.dat')
    
    @property
    def eqp1_fname(self):
        """Path to the eqp1.dat file produced."""
        return os.path.join(self.dirname, 'eqp1.dat')
    