module miter(
    input clk,
    input rst
);
    initial assume(rst == 0);

    reg [1:0] cnt_gold;
    reg [1:0] cnt_gate;

    gold u_gold(
        .clk(clk),
        .rst(rst),
        .cnt(cnt_gold)
    );
    gate u_gate(
        .clk(clk),
        .rst(rst),
        .cnt(cnt_gate)
    );

    always_comb begin
        assert(cnt_gold == cnt_gate);
    end
endmodule
