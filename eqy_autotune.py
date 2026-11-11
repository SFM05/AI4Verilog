import subprocess
from string import Template
import re
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

engines = [
    'smtbmc --nopresat boolector',
    'smtbmc boolector -- --noincr',
    'smtbmc --nopresat boolector -- --noincr',

    'smtbmc bitwuzla',
    'smtbmc --nopresat bitwuzla',
    'smtbmc bitwuzla -- --noincr',
    'smtbmc --nopresat bitwuzla -- --noincr',

    'smtbmc --unroll yices',
    'smtbmc --nopresat --unroll yices',
    'smtbmc --unroll yices -- --noincr',
    'smtbmc --nopresat --unroll yices -- --noincr',
    'smtbmc --nounroll yices',
    'smtbmc --nopresat --nounroll yices',
    'smtbmc --nounroll yices -- --noincr',
    'smtbmc --nopresat --nounroll yices -- --noincr',

    'smtbmc --unroll z3',
    'smtbmc --nopresat --unroll z3',
    'smtbmc --unroll z3 -- --noincr',
    'smtbmc --nopresat --unroll z3 -- --noincr',
    'smtbmc --nounroll z3',
    'smtbmc --nopresat --nounroll z3',
    'smtbmc --nounroll z3 -- --noincr',
    'smtbmc --nopresat --nounroll z3 -- --noincr',

    'abc pdr',

    'aiger suprove'
]

logging.basicConfig(
    level=logging.INFO,
    format="\033[34mAutotune\033[0m \033[32m%(asctime)s\033[0m [\033[34m%(name)s\033[0m] %(message)s",
    datefmt="%H:%M:%S",
)

clock_time_re = re.compile(
    r'summary: Elapsed clock time \[H:MM:SS \(secs\)\]: \d+:\d+:\d+ \((\d+)\)',
    re.MULTILINE
)
process_time_re = re.compile(
    r'summary: Elapsed process time \[H:MM:SS \(secs\)\]: \d+:\d+:\d+ \((\d+)\)',
    re.MULTILINE
)


def exec_eqy(raw_script, engine, timeout, i):
    logging.info(f'engine{i}: {engine}')
    script = Template.safe_substitute(raw_script, {'engine': engine})
    result = subprocess.run(
        ['timeout', str(timeout), 'eqy', '/dev/stdin',
            '-t',
            '-j', '8'],
        input=script,
        capture_output=True,
        text=True
    )

    if result.returncode == 124:
        logging.info(f'engine{i} {engine} timeout after {timeout}s')
        return None
    else:
        clock_time = clock_time_re.findall(result.stdout)
        process_time = process_time_re.findall(result.stdout)
        if clock_time and process_time:
            logging.info(f'engine{i}: {engine} finished,')
            logging.info(f'    process time: {int(process_time[0])}s')
            logging.info(f'    clock time: {int(clock_time[0])}s')

            if result.returncode:
                logging.info(f'    FAIL, rc = {result.returncode}')
            else:
                logging.info(f'    PASS, rc = {result.returncode}')

            return {'engine': engine,
                    'clock_time': int(clock_time[0]),
                    'process_time': int(process_time[0]),
                    'returncode': result.returncode}


def autotune(scriptPath, excluded=[]):
    with open(scriptPath, 'r', encoding='utf-8') as f:
        raw_script = f.read()
        raw_script = Template(raw_script)
    time = []

    for timeout in range(60, 610, 60):
        if time:
            return time

        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = [pool.submit(exec_eqy, raw_script, engine, timeout, i)
                       for engine, i in zip(engines, range(len(engines)))]

            for f in as_completed(futures):
                if f.result():
                    time.append(f.result())

    return time


if __name__ == '__main__':
    time = autotune('prov.eqy')
    for item in time:
        print(item)
