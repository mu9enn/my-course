#!/usr/bin/env python3
"""One source document, one Claude Code conversation. Standard library only."""
import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time

AGENT = Path(__file__).resolve().parent
ROOT = AGENT.parent
CONFIG = json.loads((AGENT / 'config.json').read_text())
STATE = AGENT / 'progress.json'


def save(state):
    temporary = STATE.with_suffix('.tmp')
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(STATE)


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(book=None, patterns=None):
    for name, spec in CONFIG['books'].items():
        if book and name != book:
            continue
        source = ROOT / 'original' / name
        paths = sorted({p for pattern in spec['include'] for p in source.glob(pattern) if p.is_file()})
        for path in paths:
            relative = path.relative_to(source).as_posix()
            if any(fnmatch.fnmatch(relative, p) for p in spec['exclude']):
                continue
            if patterns and not any(fnmatch.fnmatch(relative, p) for p in patterns):
                continue
            yield name, relative, path, ROOT / 'zh' / name / relative


def initialize():
    lock = {}
    for name, spec in CONFIG['books'].items():
        source = ROOT / 'original' / name
        if not source.exists():
            source.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(['git', 'clone', '--depth', '1', '--branch', spec['branch'], spec['url'], str(source)], check=True)
        commit = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
        lock[name] = {**{k: spec[k] for k in ('url', 'branch', 'title_zh', 'license_note')}, 'commit': commit}
        edition = ROOT / 'zh' / name
        if not edition.exists():
            shutil.copytree(source, edition, ignore=shutil.ignore_patterns('.git', '.github', '.claude', 'CLAUDE.md', 'AGENTS.md', 'CNAME', '.venv', '__pycache__'))
            (edition / 'LOCALIZATION.md').write_text(
                '# ' + spec['title_zh'] + '\n\n独立、非官方中文教学改编。\n\n'
                + '原作：' + spec['url'] + '\n\n来源提交：`' + commit + '`\n\n'
                + spec['license_note'] + '\n\n'
                + '原作者署名和许可证保留在本仓库原有文件中。新增译者解释明确标注。\n\n'
                + '本目录初始复制上游全仓库，保留资源及构建文件；尚未完成的文档仍为英文。'
                + '请在项目根目录运行 `python3 agent/translate.py status` 查看实际中文改写进度。\n'
            )
        print(name + ': ' + str(edition))
    (AGENT / 'sources.lock.json').write_text(json.dumps(lock, ensure_ascii=False, indent=2) + '\n')


def execute(name, relative, source, target, state):
    task_id = name + '/' + relative
    source_hash = fingerprint(source)
    run_id = time.strftime('%Y%m%d-%H%M%S') + '-' + str(time.time_ns())[-6:]
    log = AGENT / 'logs' / name / (relative.replace('/', '__') + '.' + run_id + '.log')
    log.parent.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith(('ANTHROPIC_', 'CLAUDE'))}
    env.update({
        'ANTHROPIC_API_KEY': json.loads((AGENT / 'secrets.local.json').read_text())['api_key'],
        'ANTHROPIC_BASE_URL': CONFIG['base_url'],
        'ANTHROPIC_MODEL': CONFIG['model'],
        'CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC': '1',
        'CLAUDE_CODE_MAX_OUTPUT_TOKENS': str(CONFIG['max_output_tokens']),
        'API_TIMEOUT_MS': str(CONFIG['timeout_seconds'] * 1000),
    })
    for tier in ('HAIKU', 'SONNET', 'OPUS'):
        env['ANTHROPIC_DEFAULT_' + tier + '_MODEL'] = CONFIG['model']
    command = [os.path.expanduser(CONFIG['claude_bin']), '--bare', '--safe-mode', '--setting-sources', '',
               '--strict-mcp-config', '--no-session-persistence', '--model', CONFIG['model'],
               '--tools', 'Read,Write,Edit', '--allowedTools', 'Read,Write,Edit',
               '--permission-mode', 'dontAsk', '--output-format', 'text',
               '--add-dir', str(ROOT), '--append-system-prompt', (AGENT / 'PROMPT.md').read_text(), '-p']
    prompt = (f'请完成这一篇中文教学改写。\n原文：{source}\n目标：{target}\n'
              f'术语表：{AGENT / "TERMS.md"}\n读者：{CONFIG["books"][name]["audience"]}\n'
              '这是一次重新生成任务，以英文原文为唯一内容依据；不要沿用目标中已有的译者补充。'
              '即使目标已有中文也必须依据当前要求重新改写并覆盖，不能只检查后宣告完成。'
              '请读英文原文后直接覆盖目标文件，完整保留原文教学内容。'
              '只写指定目标文件，读完长文的所有部分再完成改写和自查。')
    record = {'status': 'running', 'source_sha256': source_hash, 'log': str(log.relative_to(ROOT)), 'started': run_id}
    state[task_id] = record
    save(state)
    print('正在改写 ' + task_id, flush=True)
    started = time.monotonic()
    previous = fingerprint(target) if target.exists() else None
    try:
        with log.open('w') as output:
            process = subprocess.Popen(command, cwd=str(ROOT / 'zh' / name),
                                       env=env, stdin=subprocess.PIPE, stdout=output,
                                       stderr=subprocess.STDOUT, text=True, start_new_session=True)
            try:
                process.communicate(prompt, timeout=CONFIG['timeout_seconds'])
            except (subprocess.TimeoutExpired, KeyboardInterrupt):
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                raise
        changed = target.exists() and fingerprint(target) != previous and fingerprint(target) != source_hash
        if process.returncode != 0 or not changed:
            raise RuntimeError(f'Claude exit={process.returncode}, 文件发生改写={changed}；请查看日志')
        record.update(status='done', output_sha256=fingerprint(target))
    except KeyboardInterrupt:
        record.update(status='failed', error='用户中断')
        raise
    except Exception as error:
        record.update(status='failed', error=str(error))
        print(str(error), flush=True)
    finally:
        record['seconds'] = round(time.monotonic() - started, 2)
        save(state)
    print(f'{record["status"]}: {task_id} ({record["seconds"]}s)', flush=True)
    return record['status'] == 'done'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['init', 'list', 'run', 'status'])
    parser.add_argument('--book', choices=list(CONFIG['books']))
    parser.add_argument('--file', action='append', help='原仓库内路径或 glob，可重复；请给 glob 加引号')
    parser.add_argument('--limit', type=int, default=1, help='本次最多调用数，默认 1')
    parser.add_argument('--all', action='store_true', help='运行所有匹配且尚未完成的文件')
    parser.add_argument('--force', action='store_true', help='明确覆盖并重做匹配文件，含人工改动')
    args = parser.parse_args()
    if args.command == 'init':
        initialize()
        return
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    tasks = list(inventory(args.book, args.file))
    if not tasks:
        parser.error('没有匹配文件；请先 init，检查 --book / --file')
    if args.command == 'list':
        for name, relative, _, _ in tasks:
            print(name + '/' + relative)
        print(f'{len(tasks)} 个文件')
    elif args.command == 'status':
        for name in CONFIG['books']:
            selected = [(n, r) for n, r, _, _ in tasks if n == name]
            if selected:
                done = sum(state.get(n + '/' + r, {}).get('status') == 'done' for n, r in selected)
                failed = sum(state.get(n + '/' + r, {}).get('status') == 'failed' for n, r in selected)
                print(f'{name}: 已完成 {done}/{len(selected)}，失败 {failed}')
    else:
        # Prevent accidental overlapping runs writing the same files/state.
        import fcntl
        with (AGENT / '.run.lock').open('w') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                parser.error('已有批次正在运行')
            count, failures = 0, 0
            for name, relative, source, target in tasks:
                prior = state.get(name + '/' + relative, {})
                if not args.force and prior.get('status') == 'done' and prior.get('source_sha256') == fingerprint(source) and target.exists():
                    continue
                if not target.parent.exists():
                    parser.error('中文工作副本不存在；请先 init')
                if not args.force and target.exists() and fingerprint(target) != fingerprint(source):
                    print('跳过已有改动（需 --force 重做）: ' + name + '/' + relative)
                    continue
                if not args.all and count >= args.limit:
                    break
                failures += not execute(name, relative, source, target, state)
                count += 1
            print(f'本批次调用 {count} 次，失败 {failures}；完成仅表示写入成功，教学质量仍需人工抽查。')
            if failures:
                raise SystemExit(1)


if __name__ == '__main__':
    main()
