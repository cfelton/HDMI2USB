from __future__ import division
from __future__ import print_function

import os
import argparse
from argparse import Namespace

from myhdl import *

from support import TWIMaster
from support import prep_cosim

def run_testbench(args):
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=0, async=False)
    # slave (Verilog dut) perspective
    sda_i = Signal(bool(1))   # into the slave DUT
    sda_o = Signal(bool(1))   # out of the slave DUT
    scl_i = Signal(bool(1))   # into the slave DUT
    dvi_only = Signal(bool(0))

    twi = TWIMaster()
    
    tbdut = prep_cosim(clock, reset, sda_i, sda_o, scl_i,
                       dvi_only, args)

    @always(delay(10))
    def tbclk():
        clock.next = not clock

    def _test():
        
        tbtwi = twi.process(clock, reset, sda_o, sda_i, scl_i)

        def pulse_reset():
            reset.next = reset.active
            yield clock.posedge
            yield delay(113)
            reset.next = not reset.active
            yield delay(10)
            yield clock.posedge


        @instance
        def tbstim():
            yield pulse_reset()

            for ii in range(100):
                yield delay(10)

            print('start read command')        
            twi.read(addr=0x10)
            yield delay(100)    
            while twi.cmd is not None:
                yield delay(100)
                
            for ii in range(10):
                yield delay(10)

            print('end simulation')
            raise StopSimulation

        monsig = [Signal(bool(0)) for ii in range(16)]
        state = Signal(twi.States.wait)    
        @always(delay(1))
        def tbmon():
            monsig[0].next = sda_i
            monsig[1].next = sda_o
            monsig[2].next = scl_i
            state.next = twi.state
            
        return tbclk, tbstim, tbmon, tbtwi
            

    if args.trace:
        traceSignals.name = 'vcd/_test_edid'
        traceSignals.timescale = '1ns'
        fn = traceSignals.name + '.vcd'
        if os.path.isfile(fn):
            os.remove(fn)
        gt = traceSignals(_test)
    else:
        gt = _test()

    # run the simulation
    Simulation((gt, tbdut,)).run()


def test_edid():
    args = argparse.Namespace(
        trace=True,
        vtrace=True,
        vtrace_level=0,
        vtrace_module='tb_edid',
    )

    run_testbench(args)

    
if __name__ == '__main__':
    test_edid()    

