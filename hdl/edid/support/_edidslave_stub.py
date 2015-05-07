
from myhdl import *


def edidslave(rst_n, clk, sda_i, sda_o, scl_i, dvi_only):
    # this is a stub to create the testbench
    # interface it doesn't do anything!!!!
    @always_seq(clk.posedge, reset=rst_n)
    def rtl():
        if dvi_only:
            sda_o.next = sda_i ^ scl_i
            
    return rtl

    
def convert():
    rst_n = ResetSignal(0, active=0, async=False)
    clk = Signal(bool(0))
    sda_i = Signal(bool(0))
    sda_o = Signal(bool(0))
    scl_i = Signal(bool(0))
    dvi_only = Signal(bool(0))

    toVerilog(edidslave, rst_n, clk, sda_i, sda_o, scl_i, dvi_only)

    
if __name__ == '__main__':
    convert()
    
            