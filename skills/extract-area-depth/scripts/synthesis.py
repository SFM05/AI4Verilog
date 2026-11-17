import subprocess
import argparse
from string import Template
import os
import shutil
import re
from pathlib import Path


def excute_ys(root, files, top, techlib, outDir, params):
    files = ' '.join(files)

    with open(f'{root}/syn.ys', 'r', encoding='utf-8') as f:
        script = f.read()

    if params is None:
        param_section = ''
    else:
        param_section = ''
        for item in params:
            param_section += f'chparam -set {item[0]} {item[1]} {top}\n'

    script = Template(script)
    script = Template.safe_substitute(
        script,
        {'files': files,
         'top': top,
         'techlib': techlib,
         'outdir': outDir,
         'root': root,
         'param_section': param_section}
    )

    result = subprocess.run(
        ['yosys', '-s', '/dev/stdin',
         '-l', f'{outDir}/syn.log'],
        input=script,
        capture_output=True,
        text=True
    )

    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+',
                        help='Verilog files')
    parser.add_argument('--top',
                        help='Topmodule name')
    parser.add_argument('--techlib',
                        help="Techlib/PDK used for synthesis")
    parser.add_argument('--output',
                        help='Output dir')
    parser.add_argument('--param', default=None, nargs=2, action='append',
                        help='Parameters used in modules')

    args = parser.parse_args()

    files = args.files
    top = args.top
    techlib = args.techlib
    outputDir = args.output
    params = args.param

    if os.path.exists(outputDir):
        shutil.rmtree(outputDir)
    os.makedirs(outputDir)

    SCRIPT_DIR = Path(__file__).resolve().parent
    result = excute_ys(
        SCRIPT_DIR,
        files,
        top,
        techlib,
        outputDir,
        params
    )

    re_area = re.compile(rf"Chip area for.+module '\\{top}':\s*(\d+\.\d+)")
    re_depth = re.compile(
        rf"Longest topological path in {top} \(length=(\d+)\):")
    area = None
    depth = None
    for line in result.stdout.splitlines():
        pattern = re_area.findall(line)
        if pattern:
            if area is None:
                area = float(pattern[0])
            else:
                area = max(area, float(pattern[0]))

        pattern = re_depth.findall(line)
        if pattern:
            if depth is None:
                depth = int(pattern[0])
            else:
                depth = max(area, int(pattern[0]))

    if not result.returncode:
        print('Synthesis PASS')
        print(f'area = {area}, depth = {depth}')
    else:
        print('Synthesis FAIL')
