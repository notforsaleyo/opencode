# 개요
opencode 설정할거 겁나 많아서 다른 컴퓨터에서 작업하는게 엄두가 안남.

그래서 저장소 만들어서 포터블하게 해보려고.

아래부터는 기계가 쓴 내용이니 사실상 안읽어도 됨. (그냥 저장소 링크 주고 README 읽고 알아서 하라 하면 된다.)

# Windows 네이티브 OpenCode 환경

Windows에서 직접 실행하는 **OpenCode V2 TUI**와 WezTerm의 개인 환경 저장소입니다. OpenCode 데스크톱 앱이나 별도 런타임 관리자를 전제로 하지 않습니다. 활성 전역 설정 폴더(`opencode debug paths config`) 자체가 이 Git 작업 폴더여야 합니다. 현재 컴퓨터에서는 `C:\Users\rkdtj\.config\opencode`입니다.

`cli.json`과 `opencode.jsonc`는 OpenCode가 **실제로 읽는 설정**이며 Git으로 추적합니다. `dcp.jsonc`, 전역 `AGENTS.md`, `skills/`, `backlog/`, Codex 사용량 플러그인 래퍼도 추적합니다. `shared/wezterm.lua`는 실제 `%USERPROFILE%\.wezterm.lua`와 동기화할 Windows WezTerm 설정본입니다. 대화의 임시 전달은 `skills/session-handoff/`가 담당합니다.

**추적하지 않는 항목:** 모델/GitHub 인증, `service.json`, 세션 DB, 로그, 캐시, 실행 파일, `node_modules/`, Python 가상 환경 및 기타 설치물. `opencode.jsonc`와 `cli.json`에 자격 증명을 직접 적지 마세요. 이 저장소에 비밀 정보나 대화 원문을 커밋하기 전에 공개 범위를 확인해야 합니다. `handoff/`에 보관한 원본 대화를 원격에 푸시하면 Git 이력에도 남습니다.

## 다른 Windows 컴퓨터에서 복원

Windows용 OpenCode V2 CLI(데스크톱 앱 아님), Git, Node.js를 설치하고 PowerShell에서 `opencode --version`과 `opencode debug paths`로 실행 파일·설정 위치를 확인합니다. Windows용 독립 실행 파일도 사용할 수 있습니다. OpenCode 모델 로그인과 GitHub 인증은 각 컴퓨터에서 따로 수행합니다. WezTerm 자체와 `CodexMono EA` 글꼴도 필요한 경우 별도로 설치합니다.

> https://github.com/notforsaleyo/opencode.git 저장소를 받아 README의 Windows 네이티브 환경 복원 지침을 적용해 주세요. 기존 로컬 설정을 보존하고 실제 전역 설정 폴더를 Git 작업 폴더로 만들어 주세요.

에이전트용 절차:

1. 이 저장소의 `AGENTS.md`, Git 상태, 원격, 대상 컴퓨터의 `opencode debug paths config` 결과를 확인합니다. 설정 폴더가 비어 있으면 그 자리에 clone합니다. 파일이 이미 있으면 저장소 밖에 백업해 차이를 검토·병합하고 **활성 설정 폴더 자체**가 이 Git 작업 폴더가 되게 합니다. 기존 인증·서비스 파일·세션을 덮어쓰거나 DB를 복사하지 않습니다. 미커밋 변경을 강제로 버리지 않습니다.
2. 실제 `cli.json`, `opencode.jsonc`, `dcp.jsonc`를 검토해 Windows 사용자 프로필·프로젝트 경로가 다른 경우 조정합니다. `cli.json`은 TUI 전용이고 `opencode.jsonc`는 서비스·프로젝트 전역 설정입니다. 공유 파일에서 별도 복사할 필요는 없습니다. OpenCode 2.0.17 이상이 `session.verbosity: "low"`를 지원하며, 현재 기준 버전은 2.0.18입니다.
3. `opencode.jsonc`의 DCP `@tarquinen/opencode-dcp@3.2.0`가 로드되는지 확인합니다. Codex 사용량 플러그인은 `custom-plugins/codex-usage-tui/`에서 `npm install --prefix <해당 폴더> --no-package-lock`로 의존성을 설치합니다. 설치된 패키지의 `opencode2-plugin` 경로가 `opencode.jsonc`의 서버 플러그인 참조와 일치해야 하고, `cli.json`의 TUI 래퍼 경로도 이 컴퓨터의 실제 경로로 맞춥니다. `node_modules/`는 Git에 추가하지 않습니다. 래퍼는 `/codex-usage` 명령을 유지하면서 자동 사용량 알림은 끕니다.
4. `shared/wezterm.lua`를 실제 `%USERPROFILE%\.wezterm.lua`에 적용합니다. 기존 설정이 다르면 백업 후 필요한 부분을 병합합니다. PowerShell 설치 경로와 글꼴을 확인하고, 적용 후 WezTerm 설정 로딩과 단축키를 확인합니다. WezTerm이 없다면 적용 대기 상태로 보고합니다.
5. Obsidian 스킬의 CLI 기능을 쓰려면 Windows Obsidian CLI가 별도로 설치되어야 합니다. `obsidian version`으로 확인합니다. `session-handoff` 스킬을 실행하려면 Windows Python 3.10 이상, Git 인증, OpenCode V2 관리형 로컬 서비스가 필요합니다. 환경 복원만으로 보관 대화를 자동으로 가져오지 않습니다.
6. `opencode service status`, `opencode api get /api/info`로 Windows 서비스를 확인하고, 전역 스킬·DCP·Codex 플러그인 로딩 및 백로그 조회를 점검합니다. 다른 서비스와 기본 포트가 충돌할 때만 `opencode service set port <사용 가능한 포트>`로 Windows 서비스 포트를 별도 지정합니다. 인증이 필요하면 해당 컴퓨터에서 `/connect`로 로그인합니다. 검증용 세션·백로그 항목은 남기지 않습니다.

## 동기화와 관리

- 실제 전역 설정 파일을 Git으로 직접 추적합니다. 변경 시 `cli.json`, `opencode.jsonc`, `dcp.jsonc`, 래퍼 소스와 패키지 의존성을 함께 확인하고, 복원 절차가 달라지면 README를 갱신합니다. 실제 WezTerm 설정을 바꿨다면 `shared/wezterm.lua`에도 공유할 내용을 반영하고, 원격에서 변경을 가져오면 실제 WezTerm 설정에도 적용합니다.
- 변경 범위를 검토한 뒤 관련 파일만 커밋합니다. fetch 후 충돌과 기존 미커밋 작업을 보존하면서 병합하고 push합니다. 강제 푸시, `reset --hard`, 인증·서비스·DB·캐시·설치물 추가는 하지 않습니다.
- 백로그는 `skills/personal-backlog/SKILL.md`를 따릅니다. 다른 컴퓨터로 대화를 전달할 때만 `skills/session-handoff/SKILL.md`를 따르며, 원문을 원격 Git에 올리기 전 저장소의 공개 범위를 반드시 확인합니다. 대화 전송은 프로젝트 코드나 미커밋 파일을 옮기지 않습니다.
