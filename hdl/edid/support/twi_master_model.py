
from myhdl import *

class TWIMaster(object):

    def __init__(self):
        self.half_period = 10000
        self.negedge_dly = 200
        self.posedge_dly = 200
        
        self.cmd = None
        self.cmd_options = ('wait', 'read', 'write',)
        self.addr = 0
        self.nbytes = 0
        self.devaddr = 0x50;
        self.States = None
        self.readarray = None
        self.writearray = None
        self.obyte = intbv(0)[8:]
        self.ibyte = intbv(0)[8:]
        
    def read(self, addr=0xAA, nbytes=64):
        """ read an address, emulated memory read.
        This performs a standard memory read address implemented
        in most TWI (I2C) EEPROMs.  This is also the read used
        in HDMI DDC.  The read is an TWI write (write the address)
        followed by a TWI read, the commands are back to back with
        a restart inbetween.
        """
        self.addr = addr
        self.nbytes = nbytes
        self.readarray = [None for _ in range(nbytes)]
        self.cmd = 'read'

    def write(self, addr=0xAA, writearray=None):
        """ write an address, emulate memory write.
        """
        self.addr = addr
        self.writearray = writearray
        self.nbytes = len(writearray)
        self.cmd = 'write'

    def process(self, clock, reset, sda_i, sda_o, scl_o):

        self.sda_i = sda_i
        self.sda_o = sda_o
        self.scl_o = scl_o

        States = enum('wait', 'read_mem', 'write_mem', 'end')
        state = Signal(States.wait)
        self.States = States
        self.state = state
        
        @instance
        def sm():
            while True:
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                if state == States.wait:
                    if self.cmd is not None:
                        if self.cmd == 'read':
                            state.next = States.read_mem
                        elif self.cmd == 'write':
                            state.next = States.write_mem
                        else:
                            raise ValueError(
                                "invalid command {}".format(self.cmd))
                    yield delay(10)

                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                elif state == States.read_mem:
                    # to read a memory address ...
                    yield self._sm_start()
                    self.obyte[:] = (self.devaddr << 1) | 0
                    yield self._sm_write()
                    self.obyte[:] = self.addr
                    yield self._sm_cont()
                    yield self._sm_write()
                    yield self._sm_restart()
                    self.obyte[:] = (self.devaddr << 1) | 1
                    yield self._sm_write()
                    for ii in range(self.nbytes):
                        yield self._sm_cont()
                        yield self._sm_read()
                        self.readarray[ii] = self.ibyte
                        print("{:10d}:   {:02X}".format(now(),
                                                       int(self.ibyte)))
                    yield self._sm_stop()
                    self.cmd = None                        
                    state.next = States.end    


                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                elif state == States.write_mem:
                    # to write a memory address ...
                    yield self._sm_start()
                    self.obyte[:] = (self.devaddr << 1) | 0
                    yield self._sm_write()
                    self.obyte[:] = self.addr
                    yield self._sm_cont()
                    yield self._sm_write()
                    for ii in range(self.nbytes):
                        yield self._sm_cont()
                        self.obyte[:] = self.writearray[ii]
                        yield self._sm_write()
                        
                    yield self._sm_stop()
                    self.cmd = None                        
                    state.next = States.end

                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                elif state == States.end:
                    assert self.scl_o
                    self.sda_o.next = True
                    state.next = States.wait
                    yield delay(10)

                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                else:
                    raise ValueError(
                        'invalid state {}'.format(state))
                                            
        return sm
        

    #-------------------------------------------------------------
    # state-machine state handlers
    def _sm_start(self):
        #print('  start')
        assert self.scl_o
        self.sda_o.next = False
        yield delay(self.half_period)
        self.scl_o.next = False
        yield delay(self.negedge_dly)

    def _sm_restart(self):
        #print('  restart')
        assert self.scl_o
        yield delay(self.half_period)
        self.scl_o.next = False
        yield delay(self.negedge_dly)
        self.sda_o.next = True
        yield delay(self.half_period)
        self.scl_o.next = True
        yield delay(self.posedge_dly)
        self.sda_o.next = False
        yield delay(self.half_period)
        self.scl_o.next = False
        yield delay(self.negedge_dly)


    def _sm_stop(self):
        #print('  stop')
        assert self.scl_o
        yield delay(self.half_period)
        self.scl_o.next = False
        yield delay(self.negedge_dly)
        self.sda_o.next = True
        yield delay(self.half_period)
        self.scl_o.next = True

    def _sm_read(self):
        #print('  read')
        assert not self.scl_o
        self.sda_o.next = True
        for ii in range(7, -1, -1):
            yield delay(self.half_period)
            self.scl_o.next = True
            yield delay(self.posedge_dly)
            self.ibyte[ii] = self.sda_i            
            yield delay(self.half_period)
            self.scl_o.next = False
            yield delay(self.negedge_dly)

        # drive ack bit
        self.sda_o.next = False
        yield delay(self.half_period)
        self.scl_o.next = True
        yield delay(self.posedge_dly)
        assert not self.sda_i            

    def _sm_write(self):
        #print('  write')
        assert not self.scl_o
        for ii in range(7, -1, -1):
            self.sda_o.next = self.obyte[ii]
            yield delay(self.half_period)
            self.scl_o.next = True
            yield delay(self.half_period)
            self.scl_o.next = False
            yield delay(self.negedge_dly)

        # get the ack bit
        self.sda_o.next = True
        yield delay(self.half_period)
        self.scl_o.next = True
        yield delay(self.posedge_dly)
        assert not self.sda_i

    def _sm_cont(self):
        yield delay(self.half_period)
        self.scl_o.next = False
        yield delay(self.negedge_dly)

        