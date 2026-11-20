import struct
import re


def bytes2fmt(s: str, fmt: str) -> str:
    match fmt:
        case 'signed':
            assert (len(s) >= 2)
            if s[0] == '0':
                n = int(s[1:], base=2)
            else:
                n = int(s[1:], base=2)-2**(len(s)-1)
            return str(n)

        case 'unsigned':
            n = int(s, base=2)
            return str(n)

        case 'bin':
            return s

        case 'bin_group':
            splitted = [s[i:min(i+4, len(s))] for i in range(0, len(s), 4)]
            return '0b'+"'".join(splitted)

        case 'hex':
            return hex(int(s, base=2))

        case 'oct':
            return oct(int(s, base=2))

        case 'fp16':
            f = struct.unpack('>e', int(s, base=2).to_bytes(16//8))
            return str(*f)

        case 'fp32':
            f = struct.unpack('>f', int(s, base=2).to_bytes(32//8))
            return str(*f)

        case 'fp64':
            f = struct.unpack('>d', int(s, base=2).to_bytes(64//8))
            return str(*f)

        case _:
            q_format = re.findall(r'^q(\d+).(\d+)$', fmt)
            if q_format:
                m, n = q_format[0]
                m = int(m)
                n = int(n)
                assert (m+n+1 == len(s))
                n = (int(s[1:], base=2) - 2**(len(s)-1)) / (2**n)
                return str(n)

            uq_format = re.findall(r'^uq(\d+).(\d+)$', fmt)
            if uq_format:
                m, n = uq_format[0]
                m = int(m)
                n = int(n)
                assert (m+n == len(s))
                n = int(s, base=2)/(2**n)
                return str(n)

            raise ValueError(f'unsupport format {fmt}')
