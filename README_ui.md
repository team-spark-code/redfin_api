### RedFin UI

### 환경 설정 & 실행 방법
```bash
# Install NVM
echo "Installing NVM..."
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
cat <<EOF >> ~/.bashrc
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
EOF
source ~/.bashrc

# Install Node.js
echo "Installing Node.js..."
nvm install 22.0.0
nvm alias default 22.0.0
nvm use 22.0.0

# Install pnpm
echo "Installing pnpm..."
corepack enable
corepack prepare pnpm@10 --activate

# Install shadcn/ui
# The 'shadcn-ui' package is deprecated. Please use the 'shadcn' package instead
pnpm dlx shadcn@latest init -d
pnpm dlx shadcn@latest add button card input select badge skeleton dropdown-menu


```


```bash
pnpm create next-app@latest redfin_ui --ts --eslint --app
# 초기 세팅 선택은 아래를 참고


pnpm add -D tailwindcss@^4 @tailwindcss/postcss postcss
pnpm add -E next@14.2.31 react@18.3.1 react-dom@18.3.1
pnpm add -D -E eslint-config-next@14.2.31 @types/react@18 @types/react-dom@18
pnpm approve-builds
```


```bash
user@DESKTOP-26275TR:~/workspace$ pnpm create next-app@latest redfin_ui --ts --eslint --app
.../198b261f659-1ddc                     |   +1 +
.../198b261f659-1ddc                     | Progress: resolved 1, reused 0, downloaded 1, added 1, done
✔ Would you like to use Tailwind CSS? … No / Yes
✔ Would you like your code inside a `src/` directory? … No / Yes
✔ Would you like to use Turbopack for `next dev`? … No / Yes
✔ Would you like to customize the import alias (`@/*` by default)? … No / Yes
Creating a new Next.js app in /home/user/workspace/redfin_ui.

Using pnpm.

Initializing project with template: app-tw 


Installing dependencies:
- react
- react-dom
- next

Installing devDependencies:
- typescript
- @types/node
- @types/react
- @types/react-dom
- @tailwindcss/postcss
- tailwindcss
- eslint
- eslint-config-next
- @eslint/eslintrc
```

### 버전 정책
---
- Node.js: 22 LTS 계열(예: 22.x)
- 패키지 매니저: pnpm 10.14.x (최신 10.x 계열)
- npm: 11.x(최신) — pnpm을 기본 사용, npm은 보조
- React: 18.3.1
- Next.js: 14.2.31 (React 18 + App Router 안정)
    - 사유: Next 15는 App Router에서 React 19(또는 canary) 중심. 
    - React 18을 강제하려면 Pages Router로 가야 하므로, 
    - React 18 + App Router 조합은 Next 14가 가장 단순·안정적입니다. 
    - 또한 14.x는 2025-07 최신 보안 패치 14.2.31이 배포되어 있습니다.
- Tailwind CSS: 4.1.x (v4 안정 릴리스)
- shadcn/ui: CLI 최신(@latest) 사용 (2025-02 레지스트리 스키마 업데이트 반영)

대안: Next 15를 쓰고 싶다면 Pages Router + React 18은 가능(호환 유지). 
단, App Router는 React 19 트랙이므로 본 문서의 “React 18 고정” 가정과 다릅니다.
