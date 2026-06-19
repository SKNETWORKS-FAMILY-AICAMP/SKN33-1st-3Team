# SKN33-1ST-3TEAM 실행 가이드

이 문서는 프로젝트를 처음 클론한 사람이 로컬 환경에서 DB를 준비하고 Streamlit 앱을 실행하는 순서를 정리한 문서입니다.

## 1. 프로젝트 클론

```powershell
git clone https://github.com/Gitcatho/SKN33-1ST-3TEAM.git
cd SKN33-1ST-3TEAM
```

## 2. 가상환경 생성 및 패키지 설치

일반 Python 가상환경을 사용할 경우:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Conda 환경을 사용할 경우:

```powershell
conda create -n recallcar python=3.10
conda activate recallcar
pip install -r requirements.txt
```

## 3. `.env` 파일 생성

프로젝트 루트 폴더에 `.env` 파일을 만들고 아래 내용을 작성합니다.

```env
DB_USER=skn_ai
DB_PASSWORD=본인이_정한_DB비밀번호
DB_HOST=localhost
DB_PORT=3306
DB_NAME=recallcardb

NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
```

`NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`는 뉴스 크롤링을 새로 실행할 때만 필요합니다. 앱 실행만 할 경우 비워둬도 됩니다.

## 4. MySQL DB와 계정 생성

MySQL에 root 계정으로 접속합니다.

```powershell
mysql -u root -p
```

접속 후 아래 SQL을 실행합니다. `본인이_정한_DB비밀번호`는 `.env`의 `DB_PASSWORD`와 반드시 같아야 합니다.

```sql
CREATE DATABASE recallcardb;
CREATE USER 'skn_ai'@'%' IDENTIFIED BY '본인이_정한_DB비밀번호';
GRANT ALL PRIVILEGES ON recallcardb.* TO 'skn_ai'@'%';
FLUSH PRIVILEGES;
```

이미 `skn_ai` 계정이 존재한다면 비밀번호만 맞춰도 됩니다.

```sql
ALTER USER 'skn_ai'@'%' IDENTIFIED BY '본인이_정한_DB비밀번호';
FLUSH PRIVILEGES;
```

## 5. 테이블 생성

PowerShell에서 프로젝트 루트 기준으로 실행합니다.

```powershell
mysql -u skn_ai -p recallcardb < db\recallcardb_script.sql
```

비밀번호 입력이 나오면 `.env`에 작성한 `DB_PASSWORD`를 입력합니다.

## 6. CSV 데이터 삽입

```powershell
python db\insert_data.py
```

성공하면 `region`, `manufacturer`, `car`, `recall`, `faq`, `news`, `service_center` 등의 테이블에 데이터가 들어갑니다.

## 7. Streamlit 앱 실행

```powershell
streamlit run app.py
```

브라우저에서 보통 아래 주소로 접속됩니다.

```text
http://localhost:8501
```


확인할 것:

- `.env`의 `DB_PASSWORD`와 MySQL의 `skn_ai` 계정 비밀번호가 같은지 확인합니다.
- MySQL에서 아래 SQL을 다시 실행해 비밀번호와 권한을 맞춥니다.

```sql
ALTER USER 'skn_ai'@'%' IDENTIFIED BY '본인이_정한_DB비밀번호';
GRANT ALL PRIVILEGES ON recallcardb.* TO 'skn_ai'@'%';
FLUSH PRIVILEGES;
```