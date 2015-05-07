module tb_edidslave;

    reg rst_n;
    reg clk;
    reg sda_i;
    wire sda_o;
    reg  scl_i;
    reg  dvi_only;

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
    wire sda;

    assign sda_o = sda;
    assign sda = ~sda_i ? 1'b0 : 1'bz;
    assign scl = scl_i;
    
    edidslave 
      dut(
	  rst_n,
	  clk,
	  sda,
	  sda,
	  scl,
	  dvi_only
	  );

endmodule
