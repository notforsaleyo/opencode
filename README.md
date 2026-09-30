# 개요
opencode 설정할거 겁나 많아서 다른 컴퓨터에서 작업하는게 엄두가 안남.

그래서 저장소 만들어서 포터블하게 해보려고.

아래부터는 기계가 쓴 내용이니 사실상 안읽어도 됨. (그냥 저장소 링크 주고 README 읽고 알아서 하라 하면 된다.)

# 설정 동기화

이 저장소는 OpenCode V2·mise 등이 **이미 준비된 컴퓨터에서 설정 파일을 동기화**하기 위한 것입니다. OpenCode, mise, WezTerm, Obsidian과 다른 프로그램의 설치·업그레이드·실행 상태 점검 절차가 아닙니다. WezTerm·Obsidian의 설치 여부와 관계없이 해당 설정 파일만 다룹니다. 현재 OpenCode의 활성 전역 설정 폴더(`opencode debug paths config`)가 이 Git 저장소여야 합니다. 기본 위치는 `%USERPROFILE%\.config\opencode`입니다.

`cli.json`, `opencode.jsonc`, `dcp.jsonc`, `AGENTS.md`, `skills/`, `custom-plugins/` 등은 저장소 안에서 곧바로 사용하는 설정입니다. 저장소 밖 파일은 다음과 같이 대응합니다.

| 저장소 공유본 | 이 컴퓨터의 실제 파일 |
| --- | --- |
| `shared/wezterm.lua` | `%USERPROFILE%\.wezterm.lua` |
| `shared/mise-config.toml` | `%USERPROFILE%\.config\mise\config.toml` |
| `shared/Microsoft.PowerShell_profile.ps1` | PowerShell의 `$PROFILE` 중 mise 활성화 부분 |

WezTerm의 실제 `.wezterm.lua`는 같은 폴더의 선택적 `.wezterm.local.lua`를 읽습니다. 이 로컬 파일은 Git 동기화 대상이 아니며 `return { baseFont = { '글꼴 이름' }, fontSize = 18, powershell = '실제 pwsh.exe 경로', sublimeEditor = '"실제 subl.exe 경로" --wait' }`처럼 기기별 글꼴·크기와 외부 프로그램 경로를 지정합니다. 네 항목은 각각 선택 사항이고, 파일이나 항목이 없으면 `shared/wezterm.lua`의 기본값을 사용합니다. 로컬 오버라이드는 공유 파일을 수정하지 않습니다.

"설정 가져와 줘" 또는 "설정 커밋해서 올려 줘"라고 요청하면 `skills/opencode-sync/SKILL.md`를 따릅니다.

- **가져오기:** 기존 로컬 변경을 보존하면서 원격 변경을 통합하고, 공유본의 내용을 위 실제 파일에 반영합니다. 기존 PowerShell 프로필의 다른 내용은 보존합니다. 충돌하거나 어느 변경을 쓸지 불명확하면 임의로 버리지 않고 알립니다.
- **올리기:** 실제 파일에서 바뀐 공유 설정을 저장소의 공유본에 반영합니다. 포함할 변경을 검토한 뒤 관련 파일만 커밋하고 원격에 푸시합니다. 미커밋 작업을 강제로 버리거나 강제 푸시하지 않습니다.
- 컴퓨터마다 다른 **외부 응용프로그램 실행 경로**(예: WezTerm의 PowerShell·Sublime Text)는 설치된 위치만 확인해 해당 기기의 `.wezterm.local.lua`에 지정합니다. 사용자 이름을 별도의 예외로 취급하거나 단순 치환으로 설치 경로를 추측하지 않습니다. 공유본의 기본값과 색상·단축키 등은 공유하지만 `.wezterm.local.lua`의 기기별 오버라이드는 공유하지 않습니다.
- 모든 **MCP 서버 설정**은 종류·활성 여부와 관계없이 동기화하지 않습니다. 추적 중인 `opencode.jsonc` 안에 개인 MCP를 추가했다면 `.gitignore`로 그 항목을 제외할 수 없으므로 커밋 전 분리해야 합니다. DCP 플러그인은 MCP 서버 설정이 아닙니다.
- 모델/GitHub 인증, `service.json`, 세션 DB, 로그, 캐시, `node_modules/`, 가상환경과 실행 파일도 동기화하지 않습니다. `backlog/`와 `handoff/`는 설정 올리기 대상이 아니며 각자의 스킬을 따릅니다. 특히 대화 원문을 원격 Git에 올리기 전에는 공개 범위를 확인합니다.

에이전트의 작업 범위는 **설정 파일을 올바른 위치에 반영하고 요청한 Git 동기화까지 수행하는 것**입니다. OpenCode·mise·WezTerm·Obsidian·플러그인 설치, 서비스 재시작, 플러그인 로딩·단축키 동작 시험, 백로그 조회는 이 요청으로 수행하지 않습니다. 적용 후 프로그램에서 직접 확인하는 일은 사용자에게 맡깁니다.

