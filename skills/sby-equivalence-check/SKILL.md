---
name: sby-equivalence-check
description: 使用SBY检查Verilog设计的等价性
---

## 概述
本SKILL指导使用SBY对Verilog设计进行等价性检查。

## 前置条件
明确以下内容：
- 需要检查的Gold设计（参考设计）和Gate设计（待验证设计）。
- 不需要检验等价性的端口。若没有提出，则默认全部检验。
- 检验等价性的时刻。如果没有指出，则认为Gold设计和Gate设计的输出在任意时刻时刻都要相等。
- 时序电路需明确复位方式。
- 输入信号的约束。若未提及输入信号的约束，则不对输入信号做任何约束。

## 工作流程
1. 检查Gold和Gate的接口表述是否一致。如果存在不一致且没有被排除的端口，则提出异常。
2. 将待测试文件移至脚本所在的目录。
3. 检查是否有现有的miter电路与sby脚本。如果有，则检查miter电路和脚本是否符合“编写miter电路”部分与“编写sby脚本”部分的要求。如果符合要求，进入第4步。
4. 编写miter模块。
5. 编写SBY脚本（脚本后缀名需为`.sby`）。
6. 运行SBY脚本：使用`sby <script>`来运行脚本。`-f`表示覆盖原输出，`-t`表示在临时路径中运行。使用`-h`获取更多参数的帮助。
7. 可以在一开始时使用`--autotune`自动调优最佳的求解器。建议此时在脚本中添加autotune段以限制最长的尝试时间。
```shell
[autotune]
timeout <time>
```
8. 进行测试：首先将gold设计复制一份，作为gate输入miter电路，检查结果是否为通过。再修改副本，保证不等价，检查是否为不通过。确认以上两点后接入真正的gate电路进行验证，否则需要修改。
6. 处理输出。


## 编写miter电路
1. 在miter电路文件（如`miter.sv`）中按如下方式写入：
```verilog
module miter(
    // list all inputs here
);
    // declare all outputs here
    // gold & gate should have their own output

    // reset section
    // constraints section

    gold u_gold(
        // instantiate the gold module
    );

    gate u_gate(
        // instantiate the gate module
    );

    // assertion section
endmodule
```
2. 编写断言模块（assertion section）：
- 对于任意时刻都要相等的端口，可以使用`always_comb`时刻进行检查，时序电路也可以使用`always_ff`在边沿检查。
```verilog
always_comb begin
    assert(/* gold output */ == /* gate output */);
end
```

- 对于需要特定条件下进行检查的端口，可以在`always_comb`或`always_ff`中嵌套`if`。必要时可以在之前添加其他逻辑，以辅助条件判断。
```verilog
always_ff @(posedge clk) begin
    if (/* condition expression */) begin
        assert(/* gold output */ == /* gate output */);
    end
end
```

3. 编写复位模块（reset section）：
- 对于简单的复位（如仅需拉低或拉高`rst`），可以使用`initial assume(!rst);`。
- 对于复杂的复位时序，需要在SBY脚本的script段中使用`fminit`初始化。

4. 编写约束模块（constraints section）：
可以使用`assume(\* expression *\)`对信号进行约束。


## 编写SBY脚本
一个SBY脚本结构如下：
```shell
[options]
mode <prove / bmc>
depth <depth>

[engines]
# list engines here

[script]
read_verilog -sv <gold design>
rename <top module> gold       # to avoid the redefinition of top module
read_verilog -sv <gate design>
rename <top module> gate       # to avoid the redefinition of top module

read_verilog -sv <miter>
prep -top <miter top module>
# other statements

[files]
# list all file paths used in the scipt
```
### mode的选取
可以选用bmc（有界模型检查）或prove（无界模型检查）。一般而言，bmc速度更快，但不能保证两个设计时刻等价；prove速度显著更慢，但可以保证两个设计时刻等价。如无特殊要求，应当首先使用bmc。
### depth的选取
对于纯组合电路，一般取depth=1，此时bmc和prove等价。对于时序电路，depth一般取流水线长度+2~4。
### 求解器的选取

| 模式 | 求解器 |
|:---:|:---:|
| bmc | smtbmc [all solvers] </Br> btor btormc/pono/rIC3 </Br> abc bmc3/sim3 </Br> aiger aigbmc/rIC3 |
| prove | smtbmc [all solvers] </Br> abc pdr </Br> aiger avy/suproe/rIC3 </Br> btor rIC3|

smtbmc求解器包括：yices, boolector, bitwuzla, z3

### 使用`fminit [options] <module name>`初始化
用`-posedge <signal>`或`negedge <signal>`用来指定上升沿或下降沿时钟，用`-seq <signal> <sequence>`为指定信号设定初始化序列（0/1/'z，'z表示不定。最后一个信号会一直持续），用`-set <signal> <value>`固定一个信号的值。

例如：`fminit -posedge clk -sequence rst_n 0,'z check`表示对`check`模块的`rst_n`信号开始时拉低，随后不做约束。

### 文件的重命名
在`[files]`段中，可以对同名的文件按`<new filename> <source file path>`的格式进行重命名。



## 处理结果
如果等价性检查通过，SBY会在最后输出`DONE (PASS, rc=0)`。

否则需要检查报错信息。如果是miter电路或脚本存在问题，需要进行修改。如果是不等价设计，求解器会在summary中输出断言失败的位置与相关的反例`.vcd`文件。此时需要阅读相关文件，确认是设计不等价还是约束或复位条件错误。