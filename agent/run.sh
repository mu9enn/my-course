#!/usr/bin/env bash
# Run one batch and publish its actual status. Logs and credentials stay local.
set -u
cd "$(dirname "$0")/.."
if [ "${1:-}" = "--finish-current" ]; then
  # Wait for the already running batch to release its lock.
  python3 - <<'PY'
import fcntl
with open('agent/.run.lock', 'w') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
PY
elif [ "${1:-}" != "--publish-only" ]; then
  python3 agent/translate.py run --book "${1:-rlhf-book}" --all
fi
python3 - <<'PY'
# coding: utf-8
import importlib.util,json,re
from pathlib import Path
spec=importlib.util.spec_from_file_location('dispatch','agent/translate.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
state=json.loads(mod.STATE.read_text()) if mod.STATE.exists() else {}
readme=Path('README.md');text=readme.read_text()
for book in mod.CONFIG['books']:
    tasks=list(mod.inventory(book))
    done=sum(state.get(n+'/'+r,{}).get('status')=='done' for n,r,_,_ in tasks)
    lines=['# 中文教学版进度','',f'最近批次已结束，已生成 **{done}/{len(tasks)}** 篇。','',
    '由 Claude Code 调用 Qwen3.6-35B-A3B-FP8 辅助制作。生成成功不代表已通过独立技术审核；代码、公式、引用和许可证按原作保留。','',
    '来源与许可见 [LOCALIZATION.md](LOCALIZATION.md)。未完成文件可能仍为英文或部分中文，以下状态为准。','',
    '| 文档 | 生成状态 |','| --- | --- |']
    for name,relative,_,_ in tasks:
        label={'done':'已生成','failed':'失败，待重做'}.get(state.get(name+'/'+relative,{}).get('status'),'未完成')
        lines.append(f'| [{relative}]({relative}) | {label} |')
    Path('zh',book,'TRANSLATION.md').write_text('\n'.join(lines)+'\n')
    if book=='rlhf-book':
        text=re.sub(r'^RLHF 本轮.*$',f'RLHF 本轮已结束，已生成 {done}/{len(tasks)} 篇；逐篇状态见 [汉化进度](zh/rlhf-book/TRANSLATION.md)。图片和图内英文、代码注释、参考文献、网站模板及部分维护说明沿用原文，不属于整站界面汉化。',text,flags=re.M)
    else:
        text=re.sub(r'^\| Missing Semester.*$',f'| Missing Semester · MIT | [课程首页](zh/missing-semester/index.md) · [汉化进度](zh/missing-semester/TRANSLATION.md) | 保留上游各年份结构，已生成 {done}/{len(tasks)} 篇；以逐篇状态为准 |',text,flags=re.M)
    print(f'{book}: Generated {done}/{len(tasks)} documents.')
readme.write_text(text)
PY
for source in original/rlhf-book original/missing-semester; do
  if [ -n "$(git -C "$source" status --porcelain)" ]; then
    echo "Original submodule changed; publication stopped: $source" >&2
    exit 1
  fi
done
git add README.md LICENSE NOTICE.md .gitignore .gitmodules agent original zh || exit 1
python3 - <<'PY'
import json,subprocess
from pathlib import Path
secret=json.loads(Path('agent/secrets.local.json').read_text())['api_key'].encode()
files=subprocess.check_output(['git','diff','--cached','--name-only','--diff-filter=ACM','-z']).split(b'\0')
for raw in files:
    if not raw:continue
    name=raw.decode()
    if not Path(name).is_file():continue
    body=subprocess.check_output(['git','show',':'+name])
    if secret in body:raise SystemExit('Credential found in staged file; publication stopped: '+name)
PY
if [ "$?" -ne 0 ]; then exit 1; fi
if ! git diff --cached --quiet; then
  git commit -m 'Publish Chinese RLHF teaching materials and generation status' || exit 1
fi
GIT_TERMINAL_PROMPT=0 git push -u origin main
