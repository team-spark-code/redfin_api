"""
데이터 로더 유틸리티
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from pymongo.collection import Collection

logger = logging.getLogger(__name__)


def load_jsonl_file(file_path: Path) -> List[Dict[str, Any]]:
    """JSONL 파일에서 데이터 로드"""
    try:
        if not file_path.exists():
            logger.warning(f"파일이 존재하지 않음: {file_path}")
            return []
        
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    if line.strip():
                        item = json.loads(line.strip())
                        data.append(item)
                except json.JSONDecodeError as e:
                    logger.warning(f"라인 {line_num} JSON 파싱 오류: {e}")
                    continue
        
        logger.info(f"파일에서 {len(data)}개 항목 로드: {file_path}")
        return data
        
    except Exception as e:
        logger.error(f"파일 데이터 로드 오류: {e}")
        return []


def load_mongo_data(
    uri: str, 
    database: str, 
    collection: str,
    filter_query: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """MongoDB에서 데이터 로드"""
    try:
        client = MongoClient(uri)
        db = client[database]
        col = db[collection]
        
        filter_query = filter_query or {}
        cursor = col.find(filter_query)
        data = list(cursor)
        
        logger.info(f"MongoDB에서 {len(data)}개 항목 로드: {database}.{collection}")
        
        client.close()
        return data
        
    except Exception as e:
        logger.error(f"MongoDB 데이터 로드 오류: {e}")
        return []


def save_jsonl_file(data: List[Dict[str, Any]], file_path: Path) -> bool:
    """데이터를 JSONL 파일로 저장"""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        logger.info(f"{len(data)}개 항목을 파일에 저장: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"파일 저장 오류: {e}")
        return False


def validate_data_structure(data: List[Dict[str, Any]], required_fields: List[str]) -> List[Dict[str, Any]]:
    """데이터 구조 검증 및 필수 필드 확인"""
    valid_data = []
    invalid_count = 0
    
    for item in data:
        if all(field in item for field in required_fields):
            valid_data.append(item)
        else:
            invalid_count += 1
            logger.debug(f"필수 필드 누락된 항목: {item.get('id', 'unknown')}")
    
    if invalid_count > 0:
        logger.warning(f"{invalid_count}개 항목이 필수 필드를 누락")
    
    logger.info(f"데이터 검증 완료: {len(valid_data)}개 유효, {invalid_count}개 무효")
    return valid_data
