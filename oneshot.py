import json
import argparse
import logging

from eval import eval_loop
from exec import exec_loop
from eval_result import EvalResult, Status
from exec_result import ExecResult

logging.basicConfig(
    level=logging.INFO,
    format="\033[34mOneshot\033[0m \033[32m%(asctime)s\033[0m [\033[34m%(name)s\033[0m] %(message)s",
    datefmt="%H:%M:%S",
)


def exec_tasks(
    tasks: dict,
    workDir: str,
    model: str,
    epochs: int,
    start_epoch: int = 0,
    start_task: int = 0
):
    exec_result = []
    logging.info(f'Start excuting tasks at {workDir}')
    for i in range(start_epoch, epochs):
        logging.info(f'Start epoch {i+1}/{epochs}')
        result = exec_loop(
            tasks=tasks,
            workDir=f'{workDir}/epoch{i}',
            promptPath='prompt/oneshot.md',
            model=model,
            agent='oneshot',
            start=start_task
        )
        exec_result.append(result)
    logging.info(f'Task excution finished.')
    return exec_result


def eval_tasks(
    tasks: list,
    workDir: str,
    techlib: str,
    epochs: int,
    start_epoch: int = 0,
    start_task: int = 0
):
    eval_result = []
    logging.info(f'Start evaluating tasks at {workDir}')
    for i in range(start_epoch, epochs):
        logging.info(f'Start epoch {i+1}/{epochs}')
        result = eval_loop(
            tasks=tasks,
            workDir=f'{workDir}/epoch{i}',
            techlib=techlib,
            start=start_task
        )
        eval_result.append(result)
    logging.info(f'Task evaluation finished')
    return eval_result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('task', type=str,
                        help='Description file `task.json`')
    parser.add_argument('--run', '-r', type=str,
                        help='Experiment name')
    parser.add_argument('--model', '-m', type=str,
                        help='Model, in the format provider/model#variant')
    parser.add_argument('--techlib', type=str,
                        help='Techlib used for synthesis')
    parser.add_argument('--epoch', type=int, default=1,
                        help='Epochs to run')
    parser.add_argument('--start', nargs=2, type=int, default=[0, 0],
                        help='Start index of the task (0 is the first)')
    parser.add_argument('--eval', action='store_true',
                        help='Evaluate')
    parser.add_argument('--exec', action='store_true',
                        help='Execute tasks')

    args = parser.parse_args()

    techlib = args.techlib
    runName = args.run
    is_eval = args.eval
    is_exec = args.exec
    model = args.model
    epochs = args.epoch
    start = args.start

    tasks: list
    with open(args.task, 'r', encoding='utf-8') as f:
        tasks = json.load(f)

    if is_exec:
        result: list[list[EvalResult]] = exec_tasks(
            tasks=tasks,
            workDir=f'runs/{runName}',
            model=model,
            epochs=epochs,
            start_epoch=start[0],
            start_task=start[1]
        )
        for epoch_result, i in zip(result, range(0, len(result))):
            print(f'epoch {i}:')
            print(' '*19, end=' ')
            print(f'{'Input':>12} {'Output':>12}    Session id')
            for task_result, j in zip(epoch_result, range(0, len(epoch_result))):
                print(f'{j+1:>3} {tasks[j]['name']:>15}', end=' ')
                print(task_result)
            print()

    if is_eval:
        result: list[list[EvalResult]] = eval_tasks(
            tasks=tasks,
            workDir=f'runs/{runName}',
            techlib=techlib,
            epochs=epochs,
            start_epoch=start[0],
            start_task=start[1]
        )
        for epoch_result, i in zip(result, range(0, len(result))):
            print(f'epoch {i}:')
            print(' '*19, end=' ')
            print(f'{'Linting':>8} {'Equivelance':>12} {'Synthesis':>10}', end=' ')
            print(f'{'depth':>14} {'area':>24}')
            for task_result, j in zip(epoch_result, range(0, len(epoch_result))):
                print(f'{j+1:>3} {tasks[j]['name']:>15}', end=' ')
                print(task_result)
            print()
