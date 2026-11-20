from vcdvcd import VCDVCD
import argparse
import csv
from io import StringIO

from fmt import bytes2fmt


def export_ff(clk, vcd, signals, fmts, posedge, negedge):
    table = []
    for i in range(0, len(clk.tv)-1):
        time, value = clk.tv[i]
        _, value_next = clk.tv[i+1]

        if value == '1' and value_next == '0' and posedge:  # posedge
            row = [str(time), '↑']
            for signal, fmt in zip(signals, fmts):
                row.append(bytes2fmt(vcd[signal][time], fmt=fmt))
            table.append(row)
            # print(', '.join(selected_values))

        if value == '0' and value_next == '1' and negedge:  # negedge
            row = [str(time), '↓']
            for signal, fmt in zip(signals, fmts):
                row.append(bytes2fmt(vcd[signal][time], fmt=fmt))
            # print(', '.join(selected_values))
            table.append(row)

    return table


def export_comb(times, vcd, signals, fmts):
    table = []
    for time in times:
        row = [str(time)]
        for signal, fmt in zip(signals, fmts):
            row.append(bytes2fmt(vcd[signal][time], fmt=fmt))
        # print(', '.join(selected_values))
        table.append(row)

    return table


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('vcd', type=str,
                        help='VCD file')
    parser.add_argument('--clk', type=str, nargs='?',
                        help='Clock signals')
    parser.add_argument('--prefix', type=str, nargs='?',
                        help='Prefix for all signals')
    parser.add_argument('--posedge', action='store_true',
                        help='Posedge sensitive for clock')
    parser.add_argument('--negedge', action='store_true',
                        help='Negedge sensitive for clock')
    parser.add_argument('--stdin', type=str, nargs='?',
                        help='Signals and format from stdin')
    parser.add_argument('--file', type=str, nargs='?',
                        help='Signals and format from csv file')

    args = parser.parse_args()

    vcd = VCDVCD(args.vcd)
    prefix = args.prefix if args.prefix is not None else ''
    clk: str = args.clk
    posedge = args.posedge
    negedge = args.negedge

    signals = []
    fmts = []
    if args.stdin is not None:
        for row in csv.reader(StringIO(args.stdin)):
            signals.append(row[0])
            if len(row) == 1:
                fmts.append('bin')
            elif not row[1]:
                fmts.append('bin')
            else:
                fmts.append(row[1])
    elif args.file is not None:
        with open(args.file, encoding='utf-8') as f:
            for row in csv.reader(f):
                signals.append(row[0])
                if len(row) == 1:
                    fmts.append('bin')
                elif not row[1]:
                    fmts.append('bin')
                else:
                    fmts.append(row[1])
    else:
        raise RuntimeError('No signal input either from stdin or file.')

    if clk is None:
        print('time, ', end='')
        print(', '.join(signals))

        if prefix != '':
            signals = [prefix+i for i in signals]
        times = set()
        for signal in signals:
            tv = vcd[signal].tv
            for time, _ in tv:
                times.add(time)
        times = sorted(times)

        table = export_comb(times, vcd, signals, fmts)
    else:
        print(f'time, {clk}, ', end='')
        print(', '.join(signals))

        if prefix != '':
            clk = prefix+clk
            signals = [prefix+i for i in signals]

        if not (posedge or negedge):
            raise ValueError('Need a sensitive edge type')
        if clk not in list(vcd.references_to_ids.keys()):
            raise ValueError(f'Unknown clock signal {clk}')
        clk_signal = vcd[clk]

        table = export_ff(clk_signal, vcd, signals, fmts, posedge, negedge)

    for row in table:
        print(', '.join(row))
