---
name: vcd2csv
description: 将VCD文件转化为CSV表格
---

## 使用方法
### 列出所有信号
使用`python3 scripts/list_signals.py <vcd_file>`，可以列出vcd文件中所有的信号。

### 输出信号
使用`python3 scripts/vcd2csv.py <vcd_file>`来以csv表格解析vcd文件。

`--prefix <prefix>`为所有信号添加前缀，如`--prefix miter.`会在所有信号前拼接`miter.`。可留空。

使用`--clk <clock>`指定时钟（对于时序电路），用`--posedge`或`--negedge`分别指定上升沿敏感或下降沿敏感。此时会输出时钟边沿的时刻。如果不指定时钟（对于组合电路），则会输出信号列表所有发生变化的时刻。

使用`--stdin <signals>`从标准输入获取信号列表，`--file <file_path>`从文件中加载信号列表。信号列表为无表头csv格式的表格，第一列为信号名，第二列为格式。可解析的格式如下，留空默认为`bin`。
| 格式 | 含义 |
| --- | --- |
| `signed` | 有符号整数 |
| `unsigned` | 无符号整数 |
| `bin` | 二进制 |
| `bin_group` | 4位一组二进制 |
| `oct` | 八进制 |
| `hex` | 十六进制 |
| `fp16` | IEEE754 16位浮点数 |
| `fp32` | IEEE754 32位浮点数 |
| `fp64` | IEEE754 64位浮点数 |
| `qm.n` | 有符号定点数，整数m位，小数n位 |
| `uqm.n` | 无符号定点数，整数m位，小数n位 |

### 特殊信号说明
`smt_step`和`smt_clock`是smtbmc在运行时的“节拍”。含有`anyinit`的信号则表示指向的寄存器是任意值初始化，无需关注。