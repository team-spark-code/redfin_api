"""
Article CRUD API 사용 예제
"""
import asyncio
import httpx
from datetime import datetime


async def test_article_crud():
    """Article CRUD API 테스트"""
    base_url = "http://localhost:8000/api/v1/articles"
    
    async with httpx.AsyncClient() as client:
        print("=== Article CRUD API 테스트 ===\n")
        
        # 1. 새 기사 생성
        print("1. 새 기사 생성")
        article_data = {
            "News ID": "TEST001",
            "Title": "샘플 기사 제목",
            "Summary": "이것은 테스트용 기사 요약입니다. MongoDB와 FastAPI를 사용한 CRUD 작업을 테스트합니다.",
            "URL": "https://example.com/test-article",
            "keywords": "['테스트', 'MongoDB', 'FastAPI', 'CRUD']",
            "category": "Technology",
            "body": "이것은 테스트용 기사 본문입니다. MongoDB와 FastAPI를 사용한 CRUD 작업을 테스트합니다. 실제 데이터베이스에 저장되는 내용입니다.",
            "published_at": "2024-01-01 00:00:00",
            "tags": ["policy/Technology", "topic/Testing", "geo/KR"]
        }
        
        response = await client.post(f"{base_url}/", json=article_data)
        if response.status_code == 201:
            article = response.json()
            article_id = article["id"]
            print(f"✅ 기사 생성 성공: ID = {article_id}")
            print(f"   제목: {article['Title']}")
            print(f"   뉴스 ID: {article['News ID']}")
        else:
            print(f"❌ 기사 생성 실패: {response.status_code} - {response.text}")
            return
        
        print()
        
        # 2. 기사 조회
        print("2. 기사 조회")
        response = await client.get(f"{base_url}/{article_id}")
        if response.status_code == 200:
            article = response.json()
            print(f"✅ 기사 조회 성공")
            print(f"   제목: {article['Title']}")
            print(f"   뉴스 ID: {article['News ID']}")
            print(f"   카테고리: {article['category']}")
            print(f"   태그: {article['tags']}")
        else:
            print(f"❌ 기사 조회 실패: {response.status_code} - {response.text}")
        
        print()
        
        # 3. 기사 목록 조회
        print("3. 기사 목록 조회")
        response = await client.get(f"{base_url}/?page=1&size=5")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 기사 목록 조회 성공")
            print(f"   전체 개수: {result['total']}")
            print(f"   현재 페이지: {result['page']}")
            print(f"   페이지 크기: {result['size']}")
            print(f"   기사 개수: {len(result['items'])}")
        else:
            print(f"❌ 기사 목록 조회 실패: {response.status_code} - {response.text}")
        
        print()
        
        # 4. 기사 업데이트
        print("4. 기사 업데이트")
        update_data = {
            "Title": "수정된 기사 제목",
            "Summary": "수정된 기사 요약입니다.",
            "body": "수정된 기사 본문입니다.",
            "tags": ["policy/Technology", "topic/Testing", "geo/KR", "업데이트"]
        }
        
        response = await client.put(f"{base_url}/{article_id}", json=update_data)
        if response.status_code == 200:
            article = response.json()
            print(f"✅ 기사 업데이트 성공")
            print(f"   수정된 제목: {article['Title']}")
            print(f"   수정된 요약: {article['Summary']}")
            print(f"   수정된 태그: {article['tags']}")
        else:
            print(f"❌ 기사 업데이트 실패: {response.status_code} - {response.text}")
        
        print()
        
        # 5. 기사 개수 조회
        print("5. 기사 개수 조회")
        response = await client.get(f"{base_url}/stats/count")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 기사 개수 조회 성공: {result['total_count']}개")
        else:
            print(f"❌ 기사 개수 조회 실패: {response.status_code} - {response.text}")
        
        print()
        
        # 6. 헬스체크
        print("6. 헬스체크")
        response = await client.get(f"{base_url}/health/check")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 헬스체크 성공")
            print(f"   상태: {result['status']}")
            print(f"   데이터베이스: {result['database']}")
            print(f"   전체 기사 수: {result['total_articles']}")
        else:
            print(f"❌ 헬스체크 실패: {response.status_code} - {response.text}")
        
        print()
        
        # 7. 기사 삭제
        print("7. 기사 삭제")
        response = await client.delete(f"{base_url}/{article_id}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 기사 삭제 성공: {result['message']}")
        else:
            print(f"❌ 기사 삭제 실패: {response.status_code} - {response.text}")
        
        print("\n=== 테스트 완료 ===")


if __name__ == "__main__":
    print("Article CRUD API 테스트를 시작합니다...")
    print("서버가 http://localhost:8000 에서 실행 중인지 확인하세요.")
    print()
    
    try:
        asyncio.run(test_article_crud())
    except Exception as e:
        print(f"테스트 실행 중 오류 발생: {e}")
        print("서버가 실행 중인지 확인하고 다시 시도하세요.")
