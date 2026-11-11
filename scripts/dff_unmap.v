/* 
    This file is an inverse mapping from Nangate45 PDK to Yosys 
    internal register/latch library.
    Please note, the unmapping is NOT ALIGNED with the PROPER BEHAVIOR!
    The unmapping is aligned with the real logic depth.
*/

(* techmap_celltype = "DFF_X1" *)
module DFF_X1 (
    input  CK,
    input  D,
    output Q,
    output QN
);
    assign QN = Q;
    // wire q_int;
    // assign Q = q_int;
    // \$_NOT_ inv (
    //     .A(q_int),
    //     .Y(QN)
    // );
    \$_DFF_P_ ff (
        .C(CK),
        .D(D),
        .Q(Q)
    );
endmodule

(* techmap_celltype = "DFFR_X1" *)
module DFFR_X1 (
    input  CK,
    input  D,
    input  RN,
    output Q,
    output QN
);
    assign QN = Q;
    // wire q_int;
    // assign Q = q_int;
    // \$_NOT_ inv (
    //     .A(q_int),
    //     .Y(QN)
    // );
    \$_DFF_PN0_ ff (
        .C(CK),
        .D(D),
        .R(RN),
        .Q(Q)
    );
endmodule

(* techmap_celltype = "DFFS_X1" *)
module DFFS_X1 (
    input  CK,
    input  D,
    input  SN,
    output Q,
    output QN
);
    assign QN = Q;
    // wire q_int;
    // assign Q = q_int;
    // \$_NOT_ inv (
    //     .A(q_int),
    //     .Y(QN)
    // );
    \$_DFF_PN1_ ff (
        .C(CK),
        .D(D),
        .R(SN),
        .Q(Q)
    );
endmodule

(* techmap_celltype = "DFFRS_X1" *)
module DFFRS_X1 (
    input  CK,
    input  D,
    input  RN,
    input  SN,
    output Q,
    output QN
);
    assign QN = Q;
    // wire q_int;
    // assign Q = q_int;
    // \$_NOT_ inv (
    //     .A(q_int),
    //     .Y(QN)
    // );
    \$_DFFSR_PNN_ ff (
        .C(CK),
        .D(D),
        .R(RN),
        .S(SN),
        .Q(Q)
    );
endmodule

(* techmap_celltype = "DLL_X1" *)
module DLL_X1 (
    input  D,
    input  GN,
    output Q
);
    \$_DLATCH_N_ latch (
        .D(D),
        .E(GN),
        .Q(Q)
    );
endmodule

(* techmap_celltype = "DLH_X1" *)
module DLH_X1 (
    input  D,
    input  G,
    output Q
);
    \$_DLATCH_P_ latch (
        .D(D),
        .E(G),
        .Q(Q)
    );
endmodule
