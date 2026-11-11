import json
import os
import argparse

from exec_result import ExecResult


def extract(
    tasks: dict,
    workDir: str
):
    exec_result = []
    for task in tasks:
        name = task['name']
        if os.path.exists(f'{workDir}/{name}/agent.json'):
            with open(f'{workDir}/{name}/agent.json', 'r', encoding='utf-8') as f:
                log = json.load(f)

            tokens = log['info']['tokens']
            result = ExecResult(
                input=tokens['input'],
                output=tokens['output'],
                cache_read=tokens['cache']['read'],
                cache_write=tokens['cache']['write'],
                ses_id=log['info']['id']
            )
            exec_result.append(result)
        else:
            result = ExecResult(None, None, None, None, None)

    return exec_result


def extract_loop(
    tasks: list,
    workDir: str,
    epochs: str
):
    exec_result = []
    for i in range(0, epochs):
        result = extract(tasks=tasks, workDir=f'{workDir}/epoch{i}')
        exec_result.append(result)
    return exec_result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('task', type=str,
                        help='Description file `task.json`')
    parser.add_argument('--run', '-r', type=str,
                        help='Experiment name')
    parser.add_argument('--epoch', type=int, default=1,
                        help='Epochs to run')

    args = parser.parse_args()

    runDir = args.run
    epochs = args.epoch

    tasks: list
    with open(args.task, 'r', encoding='utf-8') as f:
        tasks = json.load(f)

    result = extract_loop(
        tasks=tasks,
        workDir=f'runs/{runDir}',
        epochs=epochs
    )

    for epoch_result, i in zip(result, range(0, len(result))):
        print(f'epoch {i}:')
        print(' '*19, end=' ')
        print(f'{'Input':>12} {'Output':>12}    Session id')
        for task_result, j in zip(epoch_result, range(0, len(epoch_result))):
            print(f'{j+1:>3} {tasks[j]['name']:>15}', end=' ')
            print(task_result)
        print()
