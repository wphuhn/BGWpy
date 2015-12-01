from __future__ import print_function

import os

from ..core.util import exec_from_dir
from ..core import MPITask, IOTask
from ..DFT import DFTTask

# Public
__all__ = ['QETask']


class QETask(DFTTask, IOTask):
    """Base class for Quantum Espresso calculations."""

    _TAG_JOB_COMPLETED = 'JOB DONE'

    def __init__(self, dirname, **kwargs):

        super(QETask, self).__init__(dirname, **kwargs)

        self.prefix = kwargs['prefix']
        self.savedir = self.prefix + '.save'

        self.runscript['PW'] = kwargs.get('PW', 'pw.x')
        self.runscript['PWFLAGS'] = kwargs.get('PWFLAGS', '')

    def exec_from_savedir(self):
        original = os.path.realpath(os.curdir)
        if os.path.realpath(original) == os.path.realpath(self.dirname):
            return exec_from_dir(self.savedir)
        return exec_from_dir(os.path.join(self.dirname, self.savedir))

    def write(self):
        self.check_pseudos()
        super(QETask, self).write()
        with self.exec_from_dirname():
            self.input.write()
            if not os.path.exists(self.savedir):
                os.mkdir(self.savedir)

