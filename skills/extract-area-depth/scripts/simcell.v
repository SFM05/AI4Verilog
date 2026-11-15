module \$_NOT_ (
    A,
    Y
);
    input A;
    output Y;
    assign Y = ~A;
endmodule

module \$_DFF_P_ (
    D,
    C,
    Q
);
    input D, C;
    output reg Q;
    always @(posedge C) begin
        Q <= D;
    end
endmodule

module \$_DFF_PN0_ (
    D,
    C,
    R,
    Q
);
    input D, C, R;
    output reg Q;
    always @(posedge C or negedge R) begin
        if (R == 0) Q <= 0;
        else Q <= D;
    end
endmodule

module \$_DFF_PN1_ (
    D,
    C,
    R,
    Q
);
    input D, C, R;
    output reg Q;
    always @(posedge C or negedge R) begin
        if (R == 0) Q <= 1;
        else Q <= D;
    end
endmodule

module \$_DFFSR_PNN_ (
    C,
    S,
    R,
    D,
    Q
);
    input C, S, R, D;
    output reg Q;
    always @(posedge C, negedge S, negedge R) begin
        if (R == 0) Q <= 0;
        else if (S == 0) Q <= 1;
        else Q <= D;
    end
endmodule

module \$_DLATCH_N_ (
    E,
    D,
    Q
);
    input E, D;
    output reg Q;
    always @* begin
        if (E == 0) Q <= D;
    end
endmodule

module \$_DLATCH_P_ (
    E,
    D,
    Q
);
    input E, D;
    output reg Q;
    always @* begin
        if (E == 1) Q <= D;
    end
endmodule
