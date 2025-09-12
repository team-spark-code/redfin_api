import sys
import os
import asyncio

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.article_service import article_service


async def test_fetch_all_articles():
    """전체 기사 조회 테스트"""
    try:
        print("테스트 시작...")
        result = await article_service.get_all_articles()
        
        print(f"결과 타입: {type(result)}")
        print(f"총 기사 수: {result.total}")
        print(f"아이템 수: {len(result.items)}")
        
        assert result is not None
        assert hasattr(result, 'total')
        assert hasattr(result, 'items')
        assert result.total >= 0
        assert len(result.items) >= 0
        
        print("✅ 테스트 성공!")
        
        # 첫 번째 기사 정보 출력 (있다면)
        if result.items:
            first_article = result.items[0]
            print(f"첫 번째 기사: {first_article.title}")
            print(f"카테고리: {first_article.category}")
            print(f"태그: {first_article.tags}")
        
        return result
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_fetch_all_articles())