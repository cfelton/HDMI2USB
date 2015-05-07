
from __future__ import division
from __future__ import print_function

import os
import shlex
import subprocess

from myhdl import *


def prep_cosim(clock, reset, sda_i, sda_o, scl_i, dvi_only, args=None):

    print('Compiling Verilog ...')
    vfiles = ['tb_edid.v']
    vstr = "-D VTRACE" if args.vtrace else ""
    dstr = "{} -D VTRACE_LEVEL={} -D VTRACE_MODULE={} ".format(
           vstr, args.vtrace_level, args.vtrace_module)
    cmd = 'iverilog -g2001 -o edid -y ./ {} {}'.format(dstr, ' '.join(vfiles))
    cmd = shlex.split(cmd)
    rc = subprocess.call(cmd)
    assert rc == 0, 'failed Verilog compile'
    if not os.path.exists('vcd'):
        os.makedirs('vcd')

    print('Cosimulation setup ...')
    dstr = '-lxt2 ' if args.vtrace else '-none'
    cmd = 'vvp -m ./myhdl.vpi edid {}'.format(dstr)

    gcosim = Cosimulation(cmd,
                          rst_n = reset,
                          clk = clock,
                          sda_i = sda_i,
                          sda_o = sda_o,
                          scl_i = scl_i,
                          dvi_only = dvi_only)

    return gcosim