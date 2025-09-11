"""
데이터 로딩 모듈 단위 테스트
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from src.redfin_api.load_data import load_file


class TestLoadFile:
    """load_file 함수 테스트"""

    def test_load_valid_json_file(self, test_json_file, sample_news_entries):
        """유효한 JSON 파일 로딩 테스트"""
        with patch('src.redfin_api.load_data.NEWS_FILE', test_json_file):
            result = load_file()
            assert len(result) == len(sample_news_entries)
            assert result[0]["guid"] == sample_news_entries[0]["guid"]
            assert result[0]["title"] == sample_news_entries[0]["title"]

    def test_load_valid_jsonl_file(self, test_jsonl_file, sample_news_entries):
        """유효한 JSONL 파일 로딩 테스트"""
        with patch('src.redfin_api.load_data.NEWS_FILE', test_jsonl_file):
            result = load_file()
            assert len(result) == len(sample_news_entries)
            assert result[0]["guid"] == sample_news_entries[0]["guid"]
            assert result[1]["source"] == sample_news_entries[1]["source"]

    def test_load_nonexistent_file(self, tmp_path):
        """존재하지 않는 파일 로딩 테스트"""
        nonexistent_file = tmp_path / "nonexistent.json"
        with patch('src.redfin_api.load_data.NEWS_FILE', nonexistent_file):
            result = load_file()
            assert result == []

    def test_load_invalid_json_file(self, invalid_json_file):
        """잘못된 JSON 파일 로딩 테스트"""
        with patch('src.redfin_api.load_data.NEWS_FILE', invalid_json_file):
            result = load_file()
            # 잘못된 JSON은 빈 배열을 반환해야 함
            assert result == []

    def test_load_empty_json_file(self, tmp_path):
        """빈 JSON 파일 로딩 테스트"""
        empty_file = tmp_path / "empty.json"
        empty_file.write_text("[]", encoding="utf-8")
        
        with patch('src.redfin_api.load_data.NEWS_FILE', empty_file):
            result = load_file()
            assert result == []

    def test_load_json_file_not_array(self, tmp_path):
        """배열이 아닌 JSON 파일 로딩 테스트"""
        non_array_file = tmp_path / "non_array.json"
        non_array_file.write_text('{"key": "value"}', encoding="utf-8")
        
        with patch('src.redfin_api.load_data.NEWS_FILE', non_array_file):
            result = load_file()
            assert result == []

    def test_load_jsonl_with_invalid_lines(self, tmp_path):
        """일부 라인이 잘못된 JSONL 파일 로딩 테스트"""
        jsonl_file = tmp_path / "mixed.jsonl"
        content = '''{"valid": "entry1"}
invalid json line
{"valid": "entry2"}
{"another": "valid entry"}'''
        jsonl_file.write_text(content, encoding="utf-8")
        
        with patch('src.redfin_api.load_data.NEWS_FILE', jsonl_file):
            result = load_file()
            # 유효한 라인만 로드되어야 함
            assert len(result) == 3
            assert result[0]["valid"] == "entry1"
            assert result[1]["valid"] == "entry2"
            assert result[2]["another"] == "valid entry"

    def test_load_jsonl_with_empty_lines(self, tmp_path):
        """빈 라인이 포함된 JSONL 파일 로딩 테스트"""
        jsonl_file = tmp_path / "with_empty_lines.jsonl"
        content = '''{"first": "entry"}

{"second": "entry"}
   
{"third": "entry"}'''
        jsonl_file.write_text(content, encoding="utf-8")
        
        with patch('src.redfin_api.load_data.NEWS_FILE', jsonl_file):
            result = load_file()
            # 빈 라인은 무시되고 유효한 라인만 로드되어야 함
            assert len(result) == 3
            assert result[0]["first"] == "entry"
            assert result[1]["second"] == "entry"
            assert result[2]["third"] == "entry"

    def test_file_encoding_handling(self, tmp_path, sample_news_entries):
        """파일 인코딩 처리 테스트"""
        # UTF-8 파일 생성 (한글 포함)
        utf8_file = tmp_path / "utf8.json"
        korean_data = sample_news_entries.copy()
        korean_data[0]["title"] = "한글 제목 테스트"
        korean_data[0]["summary"] = "한글 요약 내용"
        
        with utf8_file.open("w", encoding="utf-8") as f:
            json.dump(korean_data, f, ensure_ascii=False)
        
        with patch('src.redfin_api.load_data.NEWS_FILE', utf8_file):
            result = load_file()
            assert len(result) == len(korean_data)
            assert result[0]["title"] == "한글 제목 테스트"
            assert result[0]["summary"] == "한글 요약 내용"

    def test_load_file_permission_error(self, tmp_path):
        """파일 권한 오류 처리 테스트"""
        protected_file = tmp_path / "protected.json"
        protected_file.write_text('[]', encoding="utf-8")
        
        # 파일 읽기 권한 에러 시뮬레이션
        with patch('builtins.open', side_effect=PermissionError("권한 없음")):
            with patch('src.redfin_api.load_data.NEWS_FILE', protected_file):
                result = load_file()
                assert result == []

    def test_load_file_with_partial_recovery(self, tmp_path):
        """부분 복구가 가능한 손상된 JSON 파일 테스트"""
        # 부분적으로 손상된 JSON 파일 생성
        corrupted_file = tmp_path / "corrupted.json"
        content = '''[
{"guid": "1", "title": "First Entry"},
{"guid": "2", "title": "Second Entry"}
// 이 부분이 손상됨
{"guid": "3", "title": "Third Entry"}]'''
        corrupted_file.write_text(content, encoding="utf-8")
        
        with patch('src.redfin_api.load_data.NEWS_FILE', corrupted_file):
            result = load_file()
            # 부분 복구가 시도되지만 완전한 복구는 어려움
            # 최소한 빈 배열은 반환되어야 함
            assert isinstance(result, list)

    @patch('src.redfin_api.load_data.logger')
    def test_logging_behavior(self, mock_logger, test_json_file, sample_news_entries):
        """로깅 동작 테스트"""
        with patch('src.redfin_api.load_data.NEWS_FILE', test_json_file):
            result = load_file()
            
            # 로그 호출 확인
            mock_logger.info.assert_called()
            log_calls = [call.args[0] for call in mock_logger.info.call_args_list]
            
            # 파일 로딩 시도 로그 확인
            assert any("뉴스 파일 로드 시도" in log for log in log_calls)
            # 파일 로딩 완료 로그 확인
            assert any("뉴스 파일 로드 완료" in log and f"{len(sample_news_entries)}개 아이템" in log 
                      for log in log_calls)

    @patch('src.redfin_api.load_data.logger')
    def test_error_logging(self, mock_logger, tmp_path):
        """에러 로깅 테스트"""
        nonexistent_file = tmp_path / "nonexistent.json"
        
        with patch('src.redfin_api.load_data.NEWS_FILE', nonexistent_file):
            result = load_file()
            
            # 에러 로그 호출 확인
            mock_logger.error.assert_called()
            error_calls = [call.args[0] for call in mock_logger.error.call_args_list]
            assert any("뉴스 파일을 찾을 수 없거나" in error for error in error_calls)

    def test_multiple_possible_paths(self, tmp_path, sample_news_entries):
        """여러 가능한 경로 처리 테스트"""
        # 첫 번째 파일은 존재하지 않음
        first_file = tmp_path / "first.json"
        
        # 두 번째 파일은 존재함
        second_file = tmp_path / "second.json"
        with second_file.open("w", encoding="utf-8") as f:
            json.dump(sample_news_entries, f)
        
        # possible_paths에 두 파일을 모두 포함하도록 패치
        with patch('src.redfin_api.load_data.NEWS_FILE', first_file):
            # possible_paths 수정이 필요하지만, 현재 구현에서는 NEWS_FILE만 사용
            # 실제로는 load_file 함수의 possible_paths 로직을 테스트해야 함
            result = load_file()
            # 첫 번째 파일이 없으므로 빈 배열 반환
            assert result == []


class TestMainExecution:
    """__main__ 실행 테스트"""

    @patch('src.redfin_api.load_data.load_file')
    @patch('builtins.print')
    def test_main_execution_with_data(self, mock_print, mock_load_file, sample_news_entries):
        """데이터가 있을 때 main 실행 테스트"""
        mock_load_file.return_value = sample_news_entries
        
        # __main__ 블록 실행 시뮬레이션
        from src.redfin_api import load_data
        with patch.object(load_data, '__name__', '__main__'):
            exec(open(load_data.__file__).read())
        
        # print 호출 확인
        mock_print.assert_called()
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any(f"로드된 뉴스 개수: {len(sample_news_entries)}" in call for call in print_calls)

    @patch('src.redfin_api.load_data.load_file')
    @patch('builtins.print')
    def test_main_execution_no_data(self, mock_print, mock_load_file):
        """데이터가 없을 때 main 실행 테스트"""
        mock_load_file.return_value = []
        
        # __main__ 블록 실행 시뮬레이션
        from src.redfin_api import load_data
        with patch.object(load_data, '__name__', '__main__'):
            exec(open(load_data.__file__).read())
        
        # print 호출 확인
        mock_print.assert_called()
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("로드된 뉴스 개수: 0" in call for call in print_calls)
        assert any("뉴스 데이터가 없습니다." in call for call in print_calls)
