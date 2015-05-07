module tb_edidslave;

reg rst_n;
reg clk;
reg sda_i;
wire sda_o;
reg scl_i;
reg dvi_only;

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

edidslave dut(
    rst_n,
    clk,
    sda_i,
    sda_o,
    scl_i,
    dvi_only
);

endmodule
