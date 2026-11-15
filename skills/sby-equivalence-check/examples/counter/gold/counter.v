module counter (
    input clk,
    input rst,
    output reg [1:0] cnt
);
    always @(posedge clk or negedge rst) begin
        if (!rst) cnt <= 0;
        else cnt <= cnt + 1;
    end
endmodule
