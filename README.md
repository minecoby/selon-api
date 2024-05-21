
<div align="center">
<img src="https://i.ibb.co/ccwB1q7/UNTOC.jpg" width="80" alt=""/>
</div>

# <div align="center">selon-api</div>

> 🐹루피와 친구들🐹의 프로젝트입니다

개발기간: 2024. 05. ~

## 🛠️참여자

<table>  
<td align="center">
<a href="https://github.com/minecoby">
<img src="https://avatars.githubusercontent.com/u/127065808?v=4" width="80" alt=""/>
<br />
<sub><b>minecoby</b></sub>
</a>
<br />
</td>

<tr>
<td align="center">
<a href="https://github.com/2-z-won">
<img src="https://avatars.githubusercontent.com/u/148948672?v=4" width="80" alt=""/>
<br />
<sub><b>2-z-won</b></sub>
</a>
<br />
</td>
</table>

## 프로젝트 소개

selon-api는 사용자 관리 및 공지사항 관리 기능을 제공하는 API입니다. 이 프로젝트는 FastAPI와 React Native 프레임워크를 기반으로 하며, 사용자 등록, 로그인, 공지사항 생성 및 조회, 모바일 애플리케이션 기능을 포함하고 있습니다.

## 📦 기술 스택

#### Environment
<p>
  <img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white"> 
  <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white">
  <img src="https://img.shields.io/badge/Google%20Cloud%20Platform-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white">
  <img src="https://img.shields.io/badge/VSCode-0078d7?style=for-the-badge&logo=visual-studio-code&logoColor=white">
</p>

#### Backend Development
<p>
  <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"/> 
  <img src="https://img.shields.io/badge/fastapi-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/uvicorn-2C3E50?style=for-the-badge&logo=uvicorn&logoColor=white"/>
  <img src="https://img.shields.io/badge/sqlalchemy-CA4245?style=for-the-badge&logo=sqlalchemy&logoColor=white"/>
  <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=MySQL&logoColor=white"/>
  <img src="https://img.shields.io/badge/passlib-009688?style=for-the-badge&logo=passlib&logoColor=white"/>
</p>

#### Frontend Development
<p>
  <img src="https://img.shields.io/badge/React_Native-61DAFB?style=for-the-badge&logo=react&logoColor=white"/>
  <img src="https://img.shields.io/badge/Expo-000020?style=for-the-badge&logo=expo&logoColor=white"/>
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white"/>
  <img src="https://img.shields.io/badge/Jest-C21325?style=for-the-badge&logo=jest&logoColor=white"/>
</p>

## 📂 아키텍쳐

### 디렉토리 구조

```plaintext
selon-api/
├── backend/
│   ├── README.md
│   ├── __pycache__/
│   ├── database.py
│   ├── github_pull.py
│   ├── main.py
│   ├── notices.py
│   ├── requirements.txt
│   ├── test.db
│   └── users.py
└── frontend/
    └── SelonApiApp/
        ├── App.js
        ├── App.tsx
        ├── Gemfile
        ├── Gemfile.lock
        ├── README.md
        ├── __tests__/
        ├── android/
        ├── app.json
        ├── babel.config.js
        ├── index.js
        ├── ios/
        ├── jest.config.js
        ├── metro.config.js
        ├── package-lock.json
        ├── package.json
        ├── src/
        ├── tsconfig.json
        └── vendor/
```

### 파일 설명

- `backend/main.py`: FastAPI 애플리케이션의 main 코드입니다. 사용자 및 공지사항 라우터를 포함하고 있으며, CORS 설정이 포함되어 있습니다.
- `backend/database.py`: 데이터베이스 설정 및 초기화를 담당합니다.
- `backend/github_pull.py`: GitHub 웹훅을 처리하는 기능을 포함하고 있습니다.
- `backend/notices.py`: 공지사항 관련 API를 정의하고 있습니다.
- `backend/users.py`: 사용자 관련 API를 정의하고 있으며, 비밀번호 해시화 및 사용자 인증 기능을 포함하고 있습니다.
- `backend/requirements.txt`: 프로젝트에 필요한 모든 버전을 관리합니다.
- `backend/test.db`: SQLite 데이터베이스 파일입니다.
- `frontend/SelonApiApp/`: React Native 애플리케이션의 코드가 포함된 폴더입니다.

### 주요 기능

- **사용자 관리**
  - 사용자 등록
  - 사용자 로그인
  - 사용자 정보 수정
<br></br>
- **공지사항 관리**
  - 공지사항 생성
  - 공지사항 조회

### 설치 및 실행

1. 저장소를 클론합니다.
   ```bash
   git clone https://github.com/your-repo/selon-api.git
   cd selon-api
   ```

2. 백엔드 필요한 패키지를 설치합니다.
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. 애플리케이션을 실행합니다.
   ```bash
   uvicorn main:app --reload
   ```

4. 브라우저에서 다음 URL을 엽니다.
   ```plaintext
   http://localhost:8000/docs
   ```

5. 프론트엔드 애플리케이션을 설치하고 실행합니다.
   ```bash
   cd ../frontend/SelonApiApp
   npm install
   npx react-native run-ios
   ```

### 사용 예시

- 사용자 등록
  ```json
  POST /users/
  {
    "username": "example",
    "password": "password123"
  }
  ```

- 사용자 로그인
  ```json
  POST /users/login
  {
    "username": "example",
    "password": "password123"
  }
  ```

### 기여 방법

1. 이 저장소를 포크합니다.
2. 새로운 브랜치를 만듭니다.
   ```bash
   git checkout -b feature-branch
   ```
3. 변경 사항을 커밋합니다.
   ```bash
   git commit -m "커밋 메시지 입력"
   ```
4. 브랜치에 푸시합니다.
   ```bash
   git push origin feature-branch
   ```
5. 풀 리퀘스트를 생성합니다.

---

이 프로젝트에 대한 기여는 언제나 환영합니다! 버그 신고, 기능 제안, 풀 리퀘스트 등을 통해 프로젝트를 개선하는데 참여해 주세요.
