from typing import List, Dict, Any
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

NEWS_FILE = Path.cwd() / "extract_2025-08-26.jsonl"

def load_file() -> List[Dict[str, Any]]:
    """
    파일 백엔드에서 데이터 로드 (JSON 파싱 오류 발생 시 최대한 복구)
    """
    items: List[Dict[str, Any]] = []
    possible_paths = [NEWS_FILE]

    file_loaded = False
    for file_path in possible_paths:
        logger.info(f"NEWS_FILE: {file_path}")
        if file_path.exists():
            try:
                logger.info(f"뉴스 파일 로드 시도: {file_path}")
                with file_path.open("r", encoding="utf-8") as f:
                    if file_path.suffix == ".jsonl":
                        for line_num, line in enumerate(f, 1):
                            try:
                                if line.strip():
                                    items.append(json.loads(line.strip()))
                            except json.JSONDecodeError as e:
                                logger.warning(f"JSONL 파싱 오류 (라인 {line_num}): {e}")
                    else:
                        # JSON 파일: 배열 형태로 읽기, 파싱 오류 발생 시 라인별 복구 시도
                        try:
                            data = json.load(f)
                            if isinstance(data, list):
                                items = data
                            else:
                                logger.error(f"JSON 파일이 배열 형태가 아닙니다: {file_path}")
                                continue
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON 파싱 오류 ({file_path}): {e}")
                            # 라인별로 복구 시도
                            f.seek(0)
                            buffer = ""
                            for line_num, line in enumerate(f, 1):
                                buffer += line
                                try:
                                    # 배열 내 객체 단위로 파싱 시도
                                    if buffer.strip().endswith("},") or buffer.strip().endswith("}]"):
                                        # 마지막 쉼표 제거
                                        obj_str = buffer.rstrip(",\n").rstrip()
                                        if obj_str.endswith("}]"):
                                            obj_str = obj_str[:-2] + "}"
                                        item = json.loads(obj_str)
                                        items.append(item)
                                        buffer = ""
                                except Exception:
                                    continue
                            logger.warning(f"부분적으로 {len(items)}개 아이템만 복구됨")
                file_loaded = True
                logger.info(f"뉴스 파일 로드 완료: {file_path} ({len(items)}개 아이템)")
                break
            except Exception as e:
                logger.error(f"파일 읽기 오류 ({file_path}): {e}")

    if not file_loaded or not items:
        logger.error(f"뉴스 파일을 찾을 수 없거나 파싱에 실패했습니다. 시도한 경로들: {[str(p) for p in possible_paths]}")
    return items

if __name__ == "__main__":
    news_data = load_file()
    print(f"로드된 뉴스 개수: {len(news_data)}")
    if news_data:
        print(news_data[:1])
    else:
        print("뉴스 데이터가 없습니다.")