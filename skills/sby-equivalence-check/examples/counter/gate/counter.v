module counter (
    input clk,
    input rst,
    output reg [1:0] cnt
);
    always @(posedge clk or negedge rst) begin
        if (!rst) cnt <= 2'b0;
        else cnt <= cnt + 2'b1;
    end
endmodule
