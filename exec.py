import logging
import subprocess
import signal
import os
import json
import shutil
from string import Template
from exec_result import ExecResult


def _kill_group(proc, sig=signal.SIGKILL):
    try:
        os.killpg(os.getpgid(proc.pid), sig)
    except ProcessLookupError:
        pass


def run_opencode(
    logger: logging.Logger,
    prompt: str,
    model: str,
    agent: str,
    cwd: str,
    attachedFiles: str = None
):
    ses_id = None

    cmd = ['opencode', 'run', prompt,
           '-m', model,
           '--agent', agent,
           '--format', 'json']
    if attachedFiles:
        cmd.append('-f')
        cmd.append(attachedFiles)

    env = os.environ.copy()
    env['PWD'] = f'{env['PWD']}/{cwd}'

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            encoding="utf-8",
            errors="replace",
        )

        for line in proc.stdout:                       # 逐行读，边读边解析
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and obj.get('sessionID'):
                ses_id = obj['sessionID']
            if isinstance(obj, dict) and obj.get('type'):
                logger.info(f'Opencode action type: {obj['type']}')

        proc.wait()                                     # 读完之后再 wait

    except KeyboardInterrupt:
        if proc is not None:
            _kill_group(proc)
            proc.wait()

    rc = proc.returncode if proc is not None else -1
    return (rc, ses_id)


def exec(task: dict,
         workDir: str,            # 会在workDir下自动创建${name}文件夹
         promptPath: str,
         model: str,
         agent: str,
         logger: logging.Logger):
    name = task['name']

    top = task['top']
    folderPath = task['folderPath']
    files = task['files']

    # region 准备文件
    source = [f'{folderPath}/{x}' for x in files]
    gold = [f'{workDir}/{name}/run/gold/{x}' for x in files]

    if os.path.exists(f'{workDir}/{name}'):
        shutil.rmtree(f'{workDir}/{name}')
    os.makedirs(f'{workDir}/{name}')

    runDir = f'{workDir}/{name}/run'
    os.makedirs(f'{runDir}/gold')
    for src, dest in zip(source, gold):
        shutil.copy(src, dest)

    source = ' '.join(source)
    gold = ' '.join(gold)
    # endregion

    # region 启动opencode后端
    logger.info('Starting opencode backend...')
    prompt = open(promptPath, encoding='utf-8').read()
    prompt = Template.safe_substitute(Template(prompt), top=top)
    rc, ses_id = run_opencode(
        logger=logger,
        prompt=prompt,
        model=model,
        agent=agent,
        cwd=runDir
    )
    if rc:
        logger.error(f'Error occurs. Opencode exited with code = {rc}')
    # ses_id = 'ses_e73aaae0fffed9kmQBLeTIh6Dg'
    # endregion

    # region 导出对话
    if ses_id:
        logger.info(f'Export session log, id = {ses_id}')
        with open(f'{workDir}/{name}/agent.json', 'w', encoding='utf-8') as f:
            subprocess.run(
                ['opencode', 'session', 'export', ses_id],
                stdout=f,
                stderr=subprocess.STDOUT,
                text=True
            )
            logger.info(f'Export sucessfully.')
        with open(f'{workDir}/{name}/agent.json', 'r', encoding='utf-8') as f:
            log = json.load(f)

        tokens = log['info']['tokens']
        logger.info(
            f'input = {tokens['input']+tokens['cache']['read']}, {tokens['cache']['read']} cached.')
        logger.info(
            f'output = {tokens['output']+tokens['cache']['write']}, {tokens['cache']['write']} cached.')
        return ExecResult(
            input=tokens['input'],
            output=tokens['output'],
            cache_read=tokens['cache']['read'],
            cache_write=tokens['cache']['write'],
            ses_id=ses_id
        )
    else:
        logger.info(f'Capture session id failed.')
        return ExecResult(None, None, None, None, None)
    # endregion


def exec_loop(tasks: dict,
              workDir: str,
              promptPath: str,
              model: str,
              agent: str,
              start: int = 0):
    exec_result = []
    for i in range(start, len(tasks)):
        task = tasks[i]
        name = task['name']
        logger = logging.getLogger(f'{name}({i+1}/{len(tasks)})')
        logger.info(f'Excuting task {name}[{i+1}/{len(tasks)}]...')

        result = exec(
            logger=logger,
            task=task,
            workDir=workDir,
            promptPath=promptPath,
            model=model,
            agent=agent
        )
        exec_result.append(result)

        logger.info(f'Task {name} finished.')

    return exec_result


if __name__ == '__main__':
    with open('task.json', 'r') as f:
        tasks = json.load(f)
    result = exec_loop(tasks=tasks,
                       workDir='runs/test',
                       promptPath='prompt/oneshot.md',
                       model='deepseek/deepseek-flash#low',
                       agent='oneshot')
    print(result[0])
