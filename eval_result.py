from enum import IntEnum


class Status(IntEnum):
    PASS = 0
    FAIL = 1
    NA = 7

    @property
    def text(self):
        return {0: 'PASS', 1: 'FAIL', 7: 'N/A'}[self.value]

    @property
    def color(self):
        return {0: 32, 1: 31, 7: 33}[self.value]

    def __str__(self):
        return f'\033[{self.color}m{self.text}\033[0m'

    def __format__(self, spec):
        padded = format(self.text, spec)              # 宽度按纯文本算
        return f'\033[{self.color}m{padded}\033[0m'   # 再包颜色


class EvalResult:
    def __init__(self, lint=Status.NA, equiv=Status.NA, syn=Status.NA,
                 area_gold=None, area_gate=None,
                 depth_gold=None, depth_gate=None):
        self.linting = lint
        self.equiv = equiv
        self.syn = syn
        self.area_gold = area_gold
        self.area_gate = area_gate
        self.depth_gold = depth_gold
        self.depth_gate = depth_gate

    def __str__(self):
        s = f'{self.linting:>8} {self.equiv:>12} {self.syn:>10}'

        if (self.depth_gate is not None) and (self.depth_gold is not None):
            tmp = f'{self.depth_gate}({self.depth_gate-self.depth_gold:+})'
            if self.depth_gate-self.depth_gold <= 0:
                s += f' \033[32m{tmp:>14}\033[0m'
            else:
                s += f' \033[31m{tmp:>14}\033[0m'
        else:
            s += f' \033[33m{'N/A':>14}\033[0m'

        if (self.area_gate is not None) and (self.area_gold is not None):
            tmp = f'{self.area_gate:.4f}({self.area_gate-self.area_gold:+.4f})'
            if self.area_gate-self.area_gold < 0:
                s += f' \033[32m{tmp:>24}\033[0m'
            else:
                s += f' \033[31m{tmp:>24}\033[0m'
        else:
            s += f' \033[33m{'N/A':>24}\033[0m'

        return s
