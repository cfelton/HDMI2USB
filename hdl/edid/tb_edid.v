
`timescale 1ns/1ps 

`ifndef VTRACE_LEVEL
 `define VTRACE_LEVEL 0
`endif

`ifndef VTRACE_MODULE
 `define VTRACE_MODULE tb_edid
`endif

module tb_edid;

    reg rst_n;
    reg clk;
    reg sda_i;
    wire sda_o;
    reg  scl_i;
    reg  dvi_only;

`ifdef VTRACE		
    initial begin
	$dumpfile("vcd/_tb_edid.vcd");
	$dumpvars(`VTRACE_LEVEL, `VTRACE_MODULE);
    end
`endif    
    

    initial begin
	$from_myhdl(
		    rst_n,
		    clk,
		    sda_i,
		    scl_i,
		    dvi_only
		    );
	$to_myhdl(
		  sda_o
		  );
    end

    wire scl;
    tri1 sda;

    assign sda_o = (sda == 1'b0) ? 1'b0 : 1'b1;
    assign sda = ~sda_i ? 1'b0 : 1'bz;
    assign scl = scl_i;
    
    edidslave 
      dut(
	  rst_n,
	  clk,
	  sda,
	  scl,
	  dvi_only
	  );

endmodule
