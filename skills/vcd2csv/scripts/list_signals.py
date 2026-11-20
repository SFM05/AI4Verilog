from vcdvcd import VCDVCD
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('vcd', type=str,
                        help='VCD file')
    args = parser.parse_args()

    vcd = VCDVCD(args.vcd)

    print('\n'.join(vcd.references_to_ids.keys()))
