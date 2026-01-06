import streamlit as st
import google.generativeai as genai
import datetime

# ==========================================
# 1. 설정 및 API 키
# ==========================================
# 대표님의 API 키
API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=API_KEY)

# 👉 여기서 모델명을 3.0으로 확정했습니다.
MODEL_NAME = 'gemini-3-pro-preview'

# ==========================================
# 2. 마케팅 제안 생성 함수
# ==========================================
def get_marketing_suggestion():
    today = datetime.datetime.now()
    date_str = today.strftime("%Y년 %m월 %d일")
    weekday = today.strftime("%A") 
    days = {'Monday':'월', 'Tuesday':'화', 'Wednesday':'수', 'Thursday':'목', 'Friday':'금', 'Saturday':'토', 'Sunday':'일'}
    weekday_kr = days.get(weekday, weekday)

    model = genai.GenerativeModel(MODEL_NAME)
    
    prompt = f"""
    당신은 아레나 수영복 매장의 유능한 마케팅 팀장입니다.
    오늘 날짜({date_str}, {weekday_kr}요일)와 현재 시즌을 고려해서,
    사장님에게 실행 가능한 마케팅 아이디어 3가지를 정중하고 열정적으로 제안해주세요.
    매장은 구로역 NC백화점에 있으며, 최근 주변 수영장 리모델링 오픈 이슈가 있습니다.
    """
    
    return model.generate_content(prompt).text

# ==========================================
# 3. 화면 디자인 (Streamlit)
# ==========================================
st.set_page_config(page_title="아레나 AI 마케터 (Gemini 3.0)", page_icon="🏊‍♀️", layout="wide")

# 사이드바: 내 API 키로 사용 가능한 모델 확인하기 (디버깅용)
with st.sidebar:
    st.header("🔧 모델 연결 상태 확인")
    if st.button("내 사용 가능 모델 조회"):
        try:
            st.write("🔎 조회 중...")
            models = genai.list_models()
            found = False
            for m in models:
                if 'generateContent' in m.supported_generation_methods:
                    st.code(m.name) # 사용 가능한 모델 이름 출력
                    if MODEL_NAME in m.name:
                        found = True
            
            st.divider()
            if found:
                st.success(f"✅ {MODEL_NAME} 연결 성공!")
            else:
                st.error(f"⚠️ {MODEL_NAME}를 찾을 수 없습니다. 위 목록에 있는 이름을 복사해서 코드의 MODEL_NAME을 수정해주세요.")
        except Exception as e:
            st.error(f"연결 실패: {e}")

# 메인 화면
st.title(f"🏊‍♀️ 아레나 AI 마케터 (v3.0)")
st.caption(f"현재 연결된 모델: {MODEL_NAME}")

st.divider()

# --- [섹션 1: 오늘의 추천 전략] ---
st.subheader("📢 오늘의 마케팅 전략 추천")

if 'suggestion' not in st.session_state:
    st.session_state['suggestion'] = None

if st.button("💡 오늘의 마케팅 아이디어 받기"):
    with st.spinner(f"{MODEL_NAME}이(가) 트렌드를 분석 중입니다..."):
        try:
            st.session_state['suggestion'] = get_marketing_suggestion()
        except Exception as e:
            st.error(f"에러 발생: {e}")
            st.warning("왼쪽 사이드바의 '내 사용 가능 모델 조회'를 눌러서 모델명이 정확한지 확인해보세요.")

if st.session_state['suggestion']:
    st.info(st.session_state['suggestion'])

st.divider()

# --- [섹션 2: 홍보글 자동 작성] ---
st.subheader("✍️ 홍보글 작성하기")

col1, col2 = st.columns(2)
with col1:
    target = st.selectbox("타겟 고객", ["수영 초보/강습생", "수영 고수/매니아", "호캉스/여행객", "선물용 구매"])
with col2:
    platform = st.selectbox("업로드 플랫폼", ["인스타그램 (감성+짧게)", "네이버 블로그 (정보+길게)", "당근마켓 (친근하게)"])

product_info = st.text_area(
    "상품 특징",
    height=100,
    placeholder="예: 비 오는 날엔 역시 쨍한 네온 컬러! 탄탄이 소재라 튼튼함."
)

if st.button("✨ 홍보글 생성하기", type="primary"):
    if not product_info:
        st.warning("상품 특징을 입력해주세요!")
    else:
        with st.spinner("글 쓰는 중..."):
            try:
                # 글쓰기 모델 설정
                writer_model = genai.GenerativeModel(MODEL_NAME)
                
                prompt = f"""
                역할: 아레나 NC구로점 온라인 마케터
                상품 및 상황: {product_info}
                타겟: {target}
                플랫폼: {platform}
                
                위 조건에 맞춰 매력적인 홍보글을 작성해주세요.
                """
                response = writer_model.generate_content(prompt)
                st.success("작성 완료!")
                st.markdown(response.text)
            except Exception as e:

                st.error(f"오류가 발생했습니다: {e}")
