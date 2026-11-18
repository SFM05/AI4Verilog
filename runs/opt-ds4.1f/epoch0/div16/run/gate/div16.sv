module div_16bit (
    input  logic [15:0] A,
    input  logic [ 7:0] B,
    output logic [15:0] result,
    output logic [15:0] odd
);

    // 16 级恢复余数除法，每级产生 1 位商。
    //
    // B == 0 时输出 result/odd 都被强制为 0，因此 B == 0 时的内部余数属于
    // 不必关心的状态，商位也只需要对外表现为 0。利用这一点，在部分级中把
    // b_nonzero 直接并入商位，并让该商位同时作为余数选择信号（gen_gated），
    // 使 AND 可以融入选择逻辑，从而减小面积；其余级保持原始结构
    // （gen_plain），避免关键路径（odd 所在路径）被拉长。
    // MASK 的逐级选择是在不增加逻辑深度的前提下折中得到的。

    localparam bit [15:0] MASK = 16'hf7fd;

    logic [ 7:0] b_reg;
    logic        b_nonzero;
    logic [ 7:0] remainder [0:16];
    logic [ 8:0] candidate [0:15];
    logic [ 8:0] difference[0:15];
    logic [15:0] quotient;
    logic [15:0] gt;

    assign b_reg        = B;
    assign b_nonzero    = |B;
    assign remainder[0] = 8'd0;

    genvar i;
    generate
        for (i = 0; i < 16; i = i + 1) begin : gen_restoring_div
            localparam bit G = MASK[i];

            assign candidate[i]  = {remainder[i], A[15-i]};
            assign difference[i] = candidate[i] - {1'b0, b_reg};

            if (G) begin : gen_gated
                // 商位先与 b_nonzero 相与，再同时送给输出与余数选择
                assign quotient[15-i] = b_nonzero & (candidate[i] >= {1'b0, b_reg});
                assign gt[15-i]       = quotient[15-i];
            end else begin : gen_plain
                // 余数选择使用未门控的比较结果，输出商位再单独门控
                assign gt[15-i]       = (candidate[i] >= {1'b0, b_reg});
                assign quotient[15-i] = b_nonzero & gt[15-i];
            end

            assign remainder[i+1] = gt[15-i] ? difference[i][7:0] : candidate[i][7:0];
        end
    endgenerate

    assign result = quotient;
    assign odd    = {8'd0, remainder[16] & {8{b_nonzero}}};

endmodule
