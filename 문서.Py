import pandas as pd

# API 명세 데이터
api_data = [
    # 기본 연결
    ["기본 연결 확인", "GET", "/", "없음", "200 OK", "API 서버 연결 상태 확인"],

    # 이미지
    ["메인 이미지 가져오기", "GET", "/image/main", "없음", "200 OK", "메인 이미지 반환"],
    ["이미지 생성", "POST", "/image", "url, type(main|sub)", "200 OK", "새 이미지 추가"],

    # 회원가입
    ["회원가입", "POST", "/signup", "name, email, age, gender", "200 OK / 400 Bad Request", "사용자 회원가입 처리"],

    # 질문
    ["특정 질문 가져오기", "GET", "/questions/<int:question_sqe>", "없음", "200 OK / 404 Not Found", "특정 질문과 선택지 반환"],
    ["질문 개수 확인", "GET", "/questions/count", "없음", "200 OK", "전체 질문 수 반환"],
    ["질문 생성", "POST", "/question", "title, is_active, sqe, image_id", "200 OK", "새 질문 추가"],

    # 선택지
    ["선택지 생성", "POST", "/choice", "content, is_active, sqe, question_id", "200 OK", "새 선택지 추가"],

    # 답변
    ["답변 제출", "POST", "/submit", "[{user_id, choice_id}, ...]", "200 OK", "사용자 답변 저장"],

    # 통계
    ["선택지별 답변 통계", "GET", "/stats/answer_rate_by_choice", "없음", "200 OK", "선택지별 비율 통계"],
    ["질문별 답변 통계", "GET", "/stats/answer_count_by_question", "없음", "200 OK", "질문별 답변 통계"],
]

# DataFrame 생성
df = pd.DataFrame(api_data, columns=["기능", "메서드", "엔드포인트", "요청 파라미터", "응답 상태 코드", "설명"])

# CSV 저장
df.to_csv("프로젝트_API_명세서.csv", index=False, encoding="utf-8-sig")
print("✅ '프로젝트_API_명세서.csv' 파일이 생성되었습니다.")