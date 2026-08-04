-- ontology_users / ontology_jobs 더미 데이터 5건.
-- 이메일 도메인은 RFC 2606 이 예약한 example.com 을 쓴다 (실존 주소와 충돌 방지).
-- embedding 은 여기서 채우지 않는다 — scripts/backfill_users_jobs_embedding.py 담당.

INSERT INTO ontology_users (id, name, email, age) VALUES
    (1, '김민준', 'minjun.kim@example.com', 32),
    (2, '이서연', 'seoyeon.lee@example.com', 28),
    (3, '박도윤', 'doyoon.park@example.com', 41),
    (4, '최지우', 'jiwoo.choi@example.com', 26),
    (5, '정하은', 'haeun.jung@example.com', 35);

INSERT INTO ontology_jobs (id, title, company, userid) VALUES
    (1, '백엔드 개발자', '카카오', 1),
    (2, '데이터 분석가', '네이버', 2),
    (3, '프로덕트 매니저', '쿠팡', 3),
    (4, '프론트엔드 개발자', '토스', 4),
    (5, '머신러닝 엔지니어', '라인', 5);

-- id 를 명시 삽입했으므로 시퀀스를 마지막 값에 맞춘다.
-- 그러지 않으면 이후 INSERT 가 PK 충돌을 일으킨다.
SELECT setval('ontology_users_id_seq', 5, true);
SELECT setval('ontology_jobs_id_seq', 5, true);
