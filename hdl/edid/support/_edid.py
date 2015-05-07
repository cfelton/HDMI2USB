

from myhdl import *

class TWI(object):
    def __init__(self):
        self.start = Signal(bool(0))
        self.end = Signal(bool(0))
        self.read = Signal(bool(0))
        self.rdata = Signal(intbv(0)[8:])

    def m_master(self, clock, reset, scl_o, sda_o, sda_i):
                
        _scl = Signal(bool(0))
        _scd = Signal(bool(0))
        scl_posedge = Signal(bool(0))
        sda_posedge = Signal(bool(0))
        
        @always(delay(250))
        def sclgen():
            _scl.next = not _scl
            _scd.next = _scl

        @always(clock.posedge)
        def scledge():
            scl_posedge.next = not _scd and _scl
            scl_negedge.next = _scd and not _scl        

        States = enum('WAIT', 'START', 'RESTART', 'RESTART2', 
                      'STOP', 'STOP2', 'WBYTE_P', 'WBYTE_N',
                      'RBYTE_P', 'RBYTE_N',
                      'ACK', 'ACK_N', 'END')

        state = Signal(States.WAIT)
        bcnt = intbv(0, min=0, max=10)

        start, end = self.go, self.end
        cmd, rdata = self.cmd, self.rdata

        @always_seq(clock.posedge, reset=reset)
        def sm():

            # **********************************************
            if state == States.WAIT:
                bcnt[:] = 0
                end.next = False
                if start:
                    if cmd == Commands.Start:
                        state.next = States.START
                    elif cmd == Commands.Restart:
                        state.next = States.RESTART
                    elif cmd == Commands.Stop:
                        state.next = States.STOP
                    elif cmd == Commands.Read:
                        state.next = states.RBYTE_N
                    elif cmd == Commands.Write:
                        state.next = states.WBYTE_N

            # **********************************************
            elif state == States.END:
                end.next = True
                sstate.next = States.WAIT

            # **********************************************
            elif state == States.START:
                if scl_posedge:
                    sda_o.next = False
                if not sda_o and scl_negedge:
                    scl_o.next = False
                    state.next = States.END

            # **********************************************
            elif state == States.RESTART:
                
                
        return sm

    def read(self, addr, num=1):
        pass

    def write(self, addr, data, num=1):
        pass


def m_sync_with_edge(clock, sigin, sigout, pos, neg, N=3):
    sync_chain = [Signal(sigin.val) for _ in range(N)]

    @always(clock.posedge)
    def rtl():
        sync_chain[0].next = sigin
        for ii in range(1,N):
            sync_chain[ii].next = sync_chain[ii-1]
        
        pos.next = not sync_chain[N-1] and sync_chain[N-2]
        neg.next = sync_chain[N-1] and not sync_chain[N-2]

    @always_comb
    def rtl_assign():
        sigout.next = sync_chain[N-1]

    return rtl, rtl_assign


def edid_(clock, reset, scl_i, sda_i, sda_o):
    pass


def edid__lld(clock, reset, scl_i, sda_i, sda_o):
    
    @always_seq(clock.posedge, reset=rest)
    def rtl():
        pass


def test_edid(args=None):
    
    scl = Signal(bool(0))
    sda_i = Signal(bool(0))
    sda_o = Signal(bool(0))

    