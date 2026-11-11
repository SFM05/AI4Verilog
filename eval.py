import logging
from string import Template
import subprocess
import os
import shutil
import json
import re

from eval_result import EvalResult, Status


def lint(files, logDir):
    with open(f'{logDir}/linting.log', 'w', encoding='utf-8') as f:
        result = subprocess.run(
            ['verilator', files, '--lint-only', '-Wno-fatal'],
            stdout=f,
            stderr=f,
            text=True
        )

    return Status.FAIL if result.returncode else Status.PASS


def eqy_script(gold, gate, top, scriptPath, logDir):
    script = open(scriptPath, encoding='utf-8').read()
    script = Template.safe_substitute(Template(script),
                                      {'gold': gold, 'gate': gate, 'top': top})
    with open(f'{logDir}/prov.eqy', 'w', encoding='utf-8') as f:
        f.write(script)

    with open(f'{logDir}/eqy.log', 'w', encoding='utf-8') as f:
        result = subprocess.run(
            ['eqy', f'{logDir}/prov.eqy', '-d',
                f'{logDir}/eqy', '-f', '-j', '8'],
            input=script,
            stdout=f,
            stderr=f,
            text=True
        )

    return Status.FAIL if result.returncode else Status.PASS


def sby_script(gold: str, gate: str, top, scriptPath, logDir):
    rootDir = os.getcwd()
    gold = gold.split(' ')
    gold = [f'{rootDir}/{x}' for x in gold]
    gold = ' '.join(gold)

    gate = gate.split(' ')
    gate = [f'{rootDir}/{x}' for x in gate]
    gate = ' '.join(gate)

    script = open(scriptPath, encoding='utf-8').read()
    script = Template.safe_substitute(Template(script),
                                      {'gold': gold, 'gate': gate, 'top': top})
    with open(f'{logDir}/prov.sby', 'w', encoding='utf-8') as f:
        f.write(script)

    with open(f'{logDir}/sby.log', 'w', encoding='utf-8') as f:
        result = subprocess.run(
            ['sby', f'{logDir}/prov.sby', '-d', f'{logDir}/sby', '-f'],
            input=script,
            stdout=f,
            stderr=f,
            text=True
        )

    return Status.FAIL if result.returncode else Status.PASS


def synthesis(files, top, techlib, logDir):
    with open('scripts/syn.ys', 'r', encoding='utf-8') as f:
        script = f.read()
    script = Template.safe_substitute(Template(script),
                                      {'files': files, 'techlib': techlib, 'top': top})
    area = None
    depth = None
    re_area = re.compile(rf"Chip area for.+module '\\{top}':\s*(\d+\.\d+)")
    re_depth = re.compile(
        rf"Longest topological path in {top} \(length=(\d+)\):")

    with open(logDir, 'w', encoding='utf-8') as f:
        result = subprocess.run(
            ['yosys', '-s', '/dev/stdin'],
            input=script,
            stdout=f,
            stderr=f,
            text=True
        )

    area = None
    depth = None
    with open(logDir, 'r', encoding='utf-8') as f:
        for line in f:
            pattern = re_area.findall(line)
            if pattern:
                if area is None:
                    area = float(pattern[0])
                else:
                    area = max(area, float(pattern[0]))

            pattern = re_depth.findall(line)
            if pattern:
                if depth is None:
                    depth = float(pattern[0])
                else:
                    depth = max(area, float(pattern[0]))

    if (result.returncode):
        return {'status': Status.FAIL}
    else:
        return {'status': Status.PASS, 'area': area, 'depth': depth}


def eval(logger: logging.Logger,
         task: dict,
         workDir: str,  # 会在workDir下自动创建${name}文件夹
         techlib: str):
    name = task['name']
    top = task['top']
    folderPath = task['folderPath']
    files = task['files']
    backend = task['backend']
    scriptPath = task['script']

    # region 准备文件
    source = [f'{folderPath}/{x}' for x in files]
    source = ' '.join(source)
    gate = [f'{workDir}/{name}/run/gate/{x}' for x in files]
    gate = ' '.join(gate)
    # endregion

    # region 准备路径
    logDir = f'{workDir}/{name}/eval-log'
    if (os.path.exists(logDir)):
        shutil.rmtree(logDir)
    os.makedirs(logDir)
    # endregion

    # region 语法检查
    logger.info('Running Verilator to check lint...')
    result = lint(gate, logDir)
    if result == Status.PASS:
        logger.info('\033[32mLinting PASS.\033[0m')
    else:
        logger.info('\033[31mLinting FAIL.\033[0m')
        return EvalResult(Status.FAIL)
    # endregion

    # region 等价性检验
    equiv_available = True
    if backend == 'eqy':
        logger.info('Using EQY to check equivalence...')
        result = eqy_script(gold=source, gate=gate, top=top,
                            scriptPath=scriptPath, logDir=logDir)
        if (result == Status.PASS):
            logger.info('\033[32mEquivalence check PASS.\033[0m')
        else:
            logger.info('\033[31mEquivalence check FAIL.\033[0m')
            return EvalResult(Status.PASS, Status.FAIL)

    elif backend == 'sby':
        logger.info('Using SBY to check equivalence...')
        result = sby_script(gold=source, gate=gate, top=top,
                            scriptPath=scriptPath, logDir=logDir)
        if (result == Status.PASS):
            logger.info('\033[32mEquivalence check PASS.\033[0m')
        else:
            logger.info('\033[31mEquivalence check FAIL.\033[0m')
            return EvalResult(Status.PASS, Status.FAIL)

    else:
        logger.error('\033[31mUnknown backend!\033[0mSkip equivalence check.')
        equiv_available = False
    # endregion

    # region 综合与指标提取
    logger.info('Running yosys to synthesis...')
    gold_result = synthesis(source, top, techlib,
                            f'{logDir}/syn_gold.log',)
    gate_result = synthesis(gate, top, techlib,
                            f'{logDir}/syn_gate.log',)
    if (gold_result['status'] == Status.PASS and gate_result['status'] == Status.PASS):
        logger.info('\033[32mSynthesis PASS.\033[0m')
        logger.info(
            f'Gold design: area = {gold_result['area']}, depth = {gold_result['depth']}')
        logger.info(
            f'Gate design: area = {gate_result['area']}, depth = {gate_result['depth']}')
        return EvalResult(
            Status.PASS,
            Status.PASS,
            Status.PASS,
            area_gold=gold_result['area'],
            area_gate=gate_result['area'],
            depth_gold=gold_result['depth'],
            depth_gate=gate_result['depth']
        )

    elif (gold_result['status'] != Status.PASS):
        logger.error('\033[31mGold synthesisi FAIL.\033[0m')
        return EvalResult(
            Status.PASS,
            Status.PASS if equiv_available else Status.NA,
            Status.FAIL
        )
    else:
        logger.error('\033[31mGold synthesisi FAIL.\033[0m')
        return EvalResult(
            Status.PASS,
            Status.PASS if equiv_available else Status.NA,
            Status.FAIL
        )

    # endregion


def eval_loop(
    tasks: dict,
    workDir: str,
    techlib: str,
    start: int = 0
):
    eval_result = []
    for i in range(start, len(tasks)):
        task = tasks[i]
        name = task['name']
        logger = logging.getLogger(f'{name}({i+1}/{len(tasks)})')
        logger.info(f'Evaluating task {name}[{i+1}/{len(tasks)}]...')

        result = eval(
            logger=logger,
            task=task,
            workDir=workDir,
            techlib=techlib
        )
        eval_result.append(result)

        logger.info(f'Task {name} finished.')

    return eval_result


if __name__ == '__main__':
    with open('task.json', 'r') as f:
        tasks = json.load(f)
    result = eval_loop(tasks, workDir='runs/test',
                       techlib='/edatools/NangateOpenCellLibrary_typical.lib')
    print(result[0])
