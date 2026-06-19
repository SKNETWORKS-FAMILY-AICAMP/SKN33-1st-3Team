# (root 관리자계정) 새로운 계정 user 생성

# - user
# - host: %는 모든 ip를 의미(아무데서나 접근 가능)
# - identified by 비밀번호 (대소문자 구분)
create user skn_ai@'%' identified by '1234';

# 비밀번호 변경
# alter user skn_ai@'%' identified by '<DB_PASSWORD>';

# 새로운 database(schema) 생성
create database recallcardb;


# skn_ai계정에게 recall 데이터베이스 사용권한을 부여
grant all privileges on recallcardb.* to skn_ai@'%';

# skn_ai계정 부여 권한 확인
show grants for skn_ai@'%';
