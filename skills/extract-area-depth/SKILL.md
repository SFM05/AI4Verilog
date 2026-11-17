---
name: extract-area-depth
description: 使用Yosys提取Verilog工程综合后的面积与逻辑深度
---

## 概述
本SKILL利用Yosys对Verilog工程进行综合，并提取最后的面积与逻辑深度。

## 前置条件
明确需要综合的目标文件和techlib/PDK。

## 工作流程
1. 执行`python3 scripts/synthesis.py <verilog-files> --top <topmodule> --techlib <techlib> --output <output-dir>`。脚本将会在`output-dir`中输出综合日志`syn.log`、综合过程中的RTL代码、面积日志`area.log`、逻辑深度日志`depth.log`。如果提及了需要实例化的参数，则添加`--param <parameter-name> <value>`，可以使用多次以添加多个参数。
2. 如果没有异常，脚本会在控制台输出`Synthesis PASS`，并输出综合后的面积与逻辑深度。
3. 进行数据分析或者异常分析。

## 数据分析
### 面积数据
可以从`area.log`中获取详细的面积数据，其中会呈现各部分使用的模块数目与面积。`$scopeinfo`是用来标记分区边界的，不用关注。
### 逻辑深度
可以从`depth.log`中获取详细的逻辑深度数据，其中会呈现最长的关键路径。路径中以`$abc$`开头的都是ABC引擎在优化阶段插入的逻辑，难以映射回原逻辑。因此，只需要关注以`\`开头的节点，描述出关键路径所经过的变量。如果最后一个节点仍然以`$abc$`开头，需要到输出的System Verilog文件中进行查找。

输出的System Verilog与综合过程的对应关系如下：
| | 步骤 | 输出 |
|---| ---     | ---             |
| 1 | proc    | `01_proc.sv`    |
| 2 | fsm     | `02_fsm.sv`     |
| 3 | memory  | `03_memory.sv`  |
| 4 | techmap | `04_techmap.sv` |
| 5 | abc     | `05_abc.sv`     |

## 异常分析
当发生异常时，脚本会在控制台输出提示，并最后输出`Synthesis FAIL`。接下来需要在输出的`syn.log`中查找异常具体发生在哪个阶段。

## 注意事项
如果目录以及存在，脚本会直接覆盖。因此，如果需要保存原来的记录，请更换输出目录或备份原目录。