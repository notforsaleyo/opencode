# 개요
opencode 설정할거 겁나 많아서 다른 컴퓨터에서 작업하는게 엄두가 안남.

그래서 저장소 만들어서 포터블하게 해보려고.

아래부터는 기계가 쓴 내용이니 사실상 안읽어도 됨. (그냥 저장소 링크 주고 README 읽고 알아서 하라 하면 된다.)

# Windows 네이티브 OpenCode 환경

Windows에서 직접 실행하는 **OpenCode V2 TUI**와 WezTerm의 개인 환경 저장소입니다. OpenCode 데스크톱 앱은 사용하지 않으며, OpenCode CLI·Node.js·OpenSpec·Python은 mise로 관리합니다. 활성 전역 설정 폴더(`opencode debug paths config`) 자체가 이 Git 작업 폴더여야 합니다. 기본 위치는 `%USERPROFILE%\.config\opencode`이며 실제 위치는 명령으로 확인합니다.

`cli.json`과 `opencode.jsonc`는 OpenCode가 **실제로 읽는 설정**이며 Git으로 추적합니다. `dcp.jsonc`, 전역 `AGENTS.md`, `skills/`, `backlog/`, Codex 사용량 플러그인 래퍼도 추적합니다. `shared/wezterm.lua`는 실제 `%USERPROFILE%\.wezterm.lua`와 동기화할 Windows WezTerm 설정본입니다. `shared/mise-config.toml`과 `shared/Microsoft.PowerShell_profile.ps1`은 실제 전역 mise 설정과 PowerShell 프로필의 복원용 사본입니다. 대화의 임시 전달은 `skills/session-handoff/`가 담당합니다.

**추적하지 않는 항목:** 모든 MCP 서버 설정(로컬·원격, 활성·비활성), 모델/GitHub 인증, `service.json`, 세션 DB, 로그, 캐시, 실행 파일, `node_modules/`, Python 가상 환경 및 기타 설치물. `opencode.jsonc`와 `cli.json`에 자격 증명을 직접 적지 마세요. MCP 설정은 `opencode.jsonc`처럼 추적 중인 파일에 추가하면 `.gitignore`로 보호되지 않으므로 동기화 전에 별도로 제외해야 합니다. 이 저장소에 비밀 정보나 대화 원문을 커밋하기 전에 공개 범위를 확인해야 합니다. `handoff/`에 보관한 원본 대화를 원격에 푸시하면 Git 이력에도 남습니다.

## 다른 Windows 컴퓨터에서 복원

Git과 mise를 설치한 뒤 저장소의 mise 설정으로 Windows용 OpenCode V2 CLI(데스크톱 앱 아님)·Node.js·OpenSpec·Python을 설치합니다. OpenCode 모델 로그인과 GitHub 인증은 각 컴퓨터에서 따로 수행합니다. WezTerm 자체와 `움돋모노12` 글꼴도 필요한 경우 별도로 설치합니다. 프롬프트 외부 편집기로 Sublime Text를 사용하며 `C:\Program Files\Sublime Text\subl.exe` 경로를 가정합니다.

> https://github.com/notforsaleyo/opencode.git 저장소를 받아 README의 Windows 네이티브 환경 복원 지침을 적용해 주세요. 기존 로컬 설정을 보존하고 실제 전역 설정 폴더를 Git 작업 폴더로 만들어 주세요.

에이전트용 절차:

1. 이 저장소의 `AGENTS.md`, Git 상태, 원격, 대상 컴퓨터의 설정 경로를 확인합니다. OpenCode가 아직 설치되지 않았다면 기본 경로 `%USERPROFILE%\.config\opencode`를 사용하고, 설치 후 `opencode debug paths config`로 검증합니다. 설정 폴더가 비어 있으면 그 자리에 clone합니다. 파일이 이미 있으면 저장소 밖에 백업해 차이를 검토·병합하고 **활성 설정 폴더 자체**가 이 Git 작업 폴더가 되게 합니다. 기존 인증·서비스 파일·세션을 덮어쓰거나 DB를 복사하지 않습니다. 미커밋 변경을 강제로 버리지 않습니다.
   mise는 Windows에서 Scoop으로 설치할 수 있습니다(`scoop install mise`). 기존 `%USERPROFILE%\.config\mise\config.toml`과 PowerShell `$PROFILE`을 확인·백업하고, 저장소의 `shared/mise-config.toml`을 전역 mise 설정에, `shared/Microsoft.PowerShell_profile.ps1`의 활성화 줄을 PowerShell 프로필에 병합합니다. 다른 도구와 사용자 지정 프로필 내용은 보존합니다. PowerShell 외부에서도 mise 도구를 사용하려면 사용자 `Path`에 `%LOCALAPPDATA%\mise\shims`를 `WindowsApps`보다 앞에 추가합니다. 시스템 `Path`에 다른 Node.js가 먼저 있으면 이를 제거하기 전까지 shim보다 우선합니다. 새 PowerShell에서 `mise install`, `mise doctor`, `opencode --version`, `opencode debug paths config`, `node --version`, `openspec --version`, `python --version`으로 확인하고, 프로필을 읽지 않는 새 셸에서도 shim 경로를 확인합니다. `@opencode/cli`는 설치 후 스크립트로 Windows 실행 파일을 선택하므로 mise 설정에서 해당 스크립트만 허용하고 npm 설치 방식을 지정합니다. `latest`로 선언한 도구의 업그레이드는 `mise upgrade`로 수행합니다.
2. 실제 `cli.json`, `opencode.jsonc`, `dcp.jsonc`를 검토해 기기별 경로·설치 상태를 확인합니다. `cli.json`은 TUI 전용이고 `opencode.jsonc`는 서비스·프로젝트 전역 설정입니다. 두 파일의 Codex 래퍼 경로는 각각의 설정 파일을 기준으로 한 상대 경로입니다. 공유 파일에서 별도 복사할 필요는 없습니다. OpenCode 2.0.17 이상이 `session.verbosity: "low"`를 지원합니다. MCP 서버 설정은 복원하지 않습니다. 개별 기기에 개인 MCP를 추가한다면 추적 중인 `opencode.jsonc`에 쓴 값은 로컬 Git 변경으로 남으므로 커밋 대상에서 제외합니다.
3. `opencode.jsonc`의 DCP `@tarquinen/opencode-dcp@3.2.0`가 로드되는지 확인합니다. Codex 사용량 플러그인은 `custom-plugins/codex-usage-tui/`에서 `npm install --prefix <해당 폴더> --no-package-lock`로 의존성을 설치합니다. 설치된 패키지의 `opencode2-plugin` 경로가 `opencode.jsonc`의 서버 플러그인 참조와 일치해야 합니다. `node_modules/`는 Git에 추가하지 않습니다. 래퍼는 `/codex-usage` 명령을 유지하면서 자동 사용량 알림은 끕니다.
4. `shared/wezterm.lua`를 실제 `%USERPROFILE%\.wezterm.lua`에 적용합니다. 기존 설정이 다르면 백업 후 필요한 부분을 병합합니다. 파일 상단의 `baseFont`, `fontSize`, `tabFontSize`, `powershell`, `sublimeEditor`를 이 컴퓨터의 글꼴·화면·설치 경로에 맞게 확인하고, 적용 후 WezTerm 설정 로딩과 단축키를 확인합니다. WezTerm은 새 터미널에 `EDITOR`와 `VISUAL`을 전달하며, OpenCode에서는 `Ctrl+E` 또는 `Ctrl+X` 다음 `E`로 Sublime Text를 엽니다. 이미 실행 중인 OpenCode에는 적용되지 않으므로 새 터미널에서 다시 실행합니다. WezTerm이 없다면 적용 대기 상태로 보고합니다.
5. Obsidian 스킬의 CLI 기능을 쓰려면 Windows Obsidian CLI가 별도로 설치되어야 합니다. `obsidian version`으로 확인합니다. `session-handoff` 스킬을 실행하려면 Windows Python 3.10 이상, Git 인증, OpenCode V2 관리형 로컬 서비스가 필요합니다. 환경 복원만으로 보관 대화를 자동으로 가져오지 않습니다.
6. `opencode service status`, `opencode api get /api/info`로 Windows 서비스를 확인하고, 전역 스킬·DCP·Codex 플러그인 로딩 및 백로그 조회를 점검합니다. 이 저장소에서 MCP는 복원하거나 검증하지 않습니다. 다른 서비스와 기본 포트가 충돌할 때만 `opencode service set port <사용 가능한 포트>`로 Windows 서비스 포트를 별도 지정합니다. 인증이 필요하면 해당 컴퓨터에서 `/connect`로 로그인합니다. 검증용 세션·백로그 항목은 남기지 않습니다.

## 동기화와 관리

- 다른 컴퓨터의 최신 설정을 가져오거나 이 컴퓨터의 설정을 커밋·푸시할 때는 전역 `environment-sync` 스킬을 사용합니다. 예: "설정 가져와 줘", "설정 커밋해서 올려 줘". 이 스킬은 모든 MCP 서버 설정을 제외하고, 저장소의 공유 설정과 각 기기의 실행 파일 경로·글꼴·설치 상태를 구분합니다. 원격 병합 후 실제 WezTerm/mise/프로필에 적용할 부분을 확인합니다. 기기별 경로를 자동으로 안전하게 찾을 수 없으면 추측하지 않고 적용 대기 상태를 알립니다. 추적하는 활성 설정 파일에 기기별 값을 넣으면 로컬 Git 변경이 남으며, 원격 변경과 충돌할 수 있습니다.
- 실제 OpenCode 전역 설정 파일을 Git으로 직접 추적합니다. 변경 시 `cli.json`, `opencode.jsonc`의 MCP 이외 항목, `dcp.jsonc`, 래퍼 소스와 패키지 의존성을 함께 확인하고, 복원 절차가 달라지면 README를 갱신합니다. 실제 WezTerm 설정을 바꿨다면 `shared/wezterm.lua`에도 공유할 내용을 반영하고, 원격에서 변경을 가져오면 실제 WezTerm 설정에도 적용합니다. 실제 mise 전역 설정·PowerShell 프로필의 공유할 부분을 바꾸면 `shared/`의 복원용 사본과 동기화합니다.
- 이전 설치가 남아 있다면 새 mise 실행 파일과 설정 경로를 검증한 다음 예전 **실행 파일만** 개별 삭제합니다. `opencode uninstall`은 설정·세션 데이터를 함께 삭제할 수 있으므로 이전 설치 정리에 사용하지 않습니다. 현재 실행 중인 OpenCode와 공유 서비스는 안전하게 종료한 뒤 정리합니다.
- 변경 범위를 검토한 뒤 관련 파일만 커밋합니다. fetch 후 충돌과 기존 미커밋 작업을 보존하면서 병합하고 push합니다. 강제 푸시, `reset --hard`, 인증·서비스·DB·캐시·설치물 추가는 하지 않습니다.
- 백로그는 `skills/personal-backlog/SKILL.md`를 따릅니다. 다른 컴퓨터로 대화를 전달할 때만 `skills/session-handoff/SKILL.md`를 따르며, 원문을 원격 Git에 올리기 전 저장소의 공개 범위를 반드시 확인합니다. 대화 전송은 프로젝트 코드나 미커밋 파일을 옮기지 않습니다.
