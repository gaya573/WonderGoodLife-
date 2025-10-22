"""
Excel Parser 구현체 - Pandas 기반
실제 엑셀 구조에 맞게 수정된 파서
"""
from typing import List, Dict, Optional
import pandas as pd
from io import BytesIO
from ..application.ports import ExcelParser


class PandasExcelParser(ExcelParser):
    """Pandas를 사용한 엑셀 파서 - 실제 엑셀 구조에 맞게 수정"""
    
    async def parse(self, file_content: bytes) -> Dict[str, List[dict]]:
        """
        엑셀 파일을 파싱하여 브랜드별 딕셔너리 리스트로 반환
        
        실제 구조:
        - 차량명 | RowType | Model | Trim | BasePrice | OptionGroup | OptionName | Price
        
        예시 데이터:
        차량명: 2026 아반떼
        Model: 2026 아반떼 가솔린, 2026 아반떼 LPi, 2026 아반떼 LPi 장애인용
        Trim: 스마트, 모던, 인스퍼레이션, N라인
        OptionName: 컨비니언스, 하이패스, 현대 스마트센스 등
        
        반환: {
            "현대": [{"차량명": "2026 아반떼", "RowType": "TRIM", "Model": "2026 아반떼 가솔린", "Trim": "스마트", ...}, ...],
            ...
        }
        """
        try:
            print(f"[DEBUG] 엑셀 파일 파싱 시작")
            
            # 모든 시트 읽기
            excel_file = pd.ExcelFile(BytesIO(file_content))
            print(f"[DEBUG] 시트 목록: {excel_file.sheet_names}")
            print(f"[DEBUG] 총 시트 개수: {len(excel_file.sheet_names)}")
            brand_data = {}
            
            for sheet_name in excel_file.sheet_names:
                # 시트명이 브랜드명 (현대, 기아, 제네시스 등)
                brand_name = sheet_name.strip()
                print(f"[DEBUG] 시트 처리 중: '{brand_name}' (원본: '{sheet_name}')")
                
                # 시트 데이터 읽기
                df = pd.read_excel(BytesIO(file_content), sheet_name=sheet_name)
                print(f"[DEBUG] 시트 {brand_name} - 원본 데이터 행 수: {len(df)}")
                print(f"[DEBUG] 시트 {brand_name} - 원본 컬럼: {list(df.columns)}")
                
                # 첫 번째 행의 데이터 샘플 출력
                if not df.empty:
                    print(f"[DEBUG] 시트 {brand_name} - 첫 번째 행 데이터: {df.iloc[0].to_dict()}")
                    print(f"[DEBUG] 시트 {brand_name} - 두 번째 행 데이터: {df.iloc[1].to_dict() if len(df) > 1 else 'N/A'}")
                
                # 빈 시트 건너뛰기
                if df.empty:
                    print(f"[DEBUG] 시트 {brand_name} - 빈 시트이므로 건너뜀")
                    continue
                
                # 컬럼명 정규화 (실제 엑셀 구조에 맞게 수정)
                columns = df.columns.tolist()
                
                # 실제 구조: No | 차량명 | RowType | Model | Trim | BasePrice | OptionGroup | OptionName | Price
                expected_columns = ['No', '차량명', 'RowType', 'Model', 'Trim', 'BasePrice', 'OptionGroup', 'OptionName', 'Price']
                
                # 컬럼 수에 따라 유연하게 처리
                if len(columns) >= 9:
                    # 9개 이상인 경우: 첫 9개만 사용 (No 컬럼 포함)
                    print(f"[DEBUG] 9개 이상 컬럼 감지 - 원본: {columns[:9]}")
                    df = df.iloc[:, :9]
                    df.columns = expected_columns
                    print(f"[DEBUG] 매핑 후 컬럼: {list(df.columns)}")
                elif len(columns) == 8:
                    # 8개인 경우: No 컬럼이 없는 것으로 가정하고 첫 번째 컬럼을 차량명으로 처리
                    df.columns = ['차량명', 'RowType', 'Model', 'Trim', 'BasePrice', 'OptionGroup', 'OptionName', 'Price']
                else:
                    # 8개 미만인 경우: 부족한 컬럼을 None으로 채움
                    for i in range(len(columns), 8):
                        df[f'Column_{i}'] = None
                    df.columns = ['차량명', 'RowType', 'Model', 'Trim', 'BasePrice', 'OptionGroup', 'OptionName', 'Price']
                
                # NaN을 None으로 변환하고 딕셔너리 리스트로 변환
                records = []
                last_vehicle_name = None  # 이전 행의 차량명을 기억
                
                for idx, row in df.iterrows():
                    record = {}
                    for col in df.columns:
                        value = row[col]
                        if pd.isna(value):
                            record[col] = None
                        elif isinstance(value, (int, float)):
                            record[col] = value
                        else:
                            record[col] = str(value).strip() if value else None
                    
                    # 가격 관련 필드 디버그 로깅
                    if record.get('RowType') == 'TRIM':
                        print(f"[DEBUG] TRIM 행 {idx} - BasePrice 원본: {record.get('BasePrice')} (타입: {type(record.get('BasePrice'))})")
                    elif record.get('RowType') == 'OPTION':
                        print(f"[DEBUG] OPTION 행 {idx} - Price 원본: {record.get('Price')} (타입: {type(record.get('Price'))})")
                    
                    # 차량명 처리: 비어있으면 이전 행의 차량명 사용
                    vehicle_name = record.get('차량명')
                    
                    if vehicle_name and str(vehicle_name).strip():
                        # 차량명이 있으면 업데이트
                        last_vehicle_name = vehicle_name
                        print(f"[DEBUG] 차량명 업데이트: '{vehicle_name}'")
                    else:
                        # 차량명이 비어있으면 이전 행의 차량명 사용
                        if last_vehicle_name:
                            record['차량명'] = last_vehicle_name
                            print(f"[DEBUG] 이전 차량명 사용: '{last_vehicle_name}'")
                        else:
                            print(f"[DEBUG] 차량명이 없고 이전 차량명도 없어서 건너뜀")
                            continue
                    
                    # 유효한 행이면 추가
                    print(f"[DEBUG] 엑셀 파싱 - 행 추가: {record}")
                    records.append(record)
            
            # 브랜드별 데이터 저장 (빈 시트가 아닌 경우만)
                if records:
                    brand_data[brand_name] = records
                    print(f"[DEBUG] 브랜드 {brand_name}에 {len(records)}개 행 저장 완료")
                else:
                    print(f"[DEBUG] 브랜드 {brand_name}에 유효한 데이터가 없음")
            
            print(f"[DEBUG] 파싱 완료 - 총 브랜드 수: {len(brand_data)}")
            print(f"[DEBUG] 브랜드 목록: {list(brand_data.keys())}")
            
            # 각 브랜드별 레코드 수 출력
            for brand_name, records in brand_data.items():
                print(f"[DEBUG] 브랜드 '{brand_name}': {len(records)}개 레코드")
            
            return brand_data
            
        except Exception as e:
            raise ValueError(f"엑셀 파싱 실패: {str(e)}")
    
    def extract_vehicle_lines(self, brand_data: Dict[str, List[dict]]) -> Dict[str, List[str]]:
        """
        브랜드별 고유한 VehicleLine 목록 추출
        
        차량명에서 브랜드를 제외한 부분을 VehicleLine으로 사용
        예: "2026 아반떼" → "아반떼"
        
        Args:
            brand_data: parse() 메서드의 반환값
            
        Returns:
            {"현대": ["아반떼", "소나타", "그랜저"], "기아": ["모닝", "K3", "K5"], ...}
        """
        vehicle_lines_by_brand = {}
        
        for brand_name, records in brand_data.items():
            vehicle_lines = set()
            
            for record in records:
                vehicle_name = record.get('차량명')
                if vehicle_name and vehicle_name.strip():
                    # "2026 아반떼" → "아반떼" 추출
                    vehicle_line = self._extract_vehicle_line_name(vehicle_name)
                    if vehicle_line:
                        vehicle_lines.add(vehicle_line)
            
            vehicle_lines_by_brand[brand_name] = sorted(list(vehicle_lines))
        
        return vehicle_lines_by_brand
    
    def extract_models(self, brand_data: Dict[str, List[dict]]) -> Dict[str, Dict[str, List[str]]]:
        """
        브랜드별, VehicleLine별 고유한 Model 목록 추출
        
        Model 컬럼에서 실제 모델명 추출
        예: "2026 아반떼 가솔린" → "2026 아반떼 가솔린"
        
        Args:
            brand_data: parse() 메서드의 반환값
            
        Returns:
            {
                "현대": {
                    "아반떼": ["2026 아반떼 가솔린", "2026 아반떼 LPi", "2026 아반떼 LPi 장애인용"],
                    ...
                },
                ...
            }
        """
        models_by_brand_line = {}
        
        for brand_name, records in brand_data.items():
            brand_models = {}
            
            for record in records:
                vehicle_name = record.get('차량명')
                model = record.get('Model')
                
                if vehicle_name and vehicle_name.strip() and model and model.strip():
                    vehicle_line = self._extract_vehicle_line_name(vehicle_name)
                    if vehicle_line:
                        if vehicle_line not in brand_models:
                            brand_models[vehicle_line] = set()
                        brand_models[vehicle_line].add(model.strip())
            
            # set을 list로 변환하고 정렬
            for vehicle_line in brand_models:
                brand_models[vehicle_line] = sorted(list(brand_models[vehicle_line]))
            
            models_by_brand_line[brand_name] = brand_models
        
        return models_by_brand_line
    
    def extract_trims(self, brand_data: Dict[str, List[dict]]) -> Dict[str, Dict[str, Dict[str, List[str]]]]:
        """
        브랜드별, VehicleLine별, Model별 고유한 Trim 목록 추출
        
        Args:
            brand_data: parse() 메서드의 반환값
            
        Returns:
            {
                "현대": {
                    "아반떼": {
                        "2026 아반떼 가솔린": ["스마트", "모던", "인스퍼레이션", "N라인"],
                        "2026 아반떼 LPi": ["스마트", "모던", "인스퍼레이션"],
                        ...
                    }
                },
                ...
            }
        """
        trims_by_brand_line_model = {}
        
        for brand_name, records in brand_data.items():
            brand_trims = {}
            
            for record in records:
                if record.get('RowType') != 'TRIM':
                    continue
                    
                vehicle_name = record.get('차량명')
                model = record.get('Model')
                trim = record.get('Trim')
                
                if all([vehicle_name, model, trim]) and all([v and str(v).strip() for v in [vehicle_name, model, trim]]):
                    vehicle_line = self._extract_vehicle_line_name(vehicle_name)
                    if vehicle_line:
                        if vehicle_line not in brand_trims:
                            brand_trims[vehicle_line] = {}
                        if model not in brand_trims[vehicle_line]:
                            brand_trims[vehicle_line][model] = set()
                        brand_trims[vehicle_line][model].add(trim.strip())
            
            # set을 list로 변환하고 정렬
            for vehicle_line in brand_trims:
                for model in brand_trims[vehicle_line]:
                    brand_trims[vehicle_line][model] = sorted(list(brand_trims[vehicle_line][model]))
            
            trims_by_brand_line_model[brand_name] = brand_trims
        
        return trims_by_brand_line_model
    
    def extract_options(self, brand_data: Dict[str, List[dict]]) -> Dict[str, Dict[str, Dict[str, Dict[str, List[dict]]]]]:
        """
        브랜드별, VehicleLine별, Model별, Trim별 옵션 목록 추출
        
        Args:
            brand_data: parse() 메서드의 반환값
            
        Returns:
            {
                "현대": {
                    "아반떼": {
                        "2026 아반떼 가솔린": {
                            "스마트": [
                                {"name": "컨비니언스", "price": 380000},
                                {"name": "하이패스", "price": 200000},
                                ...
                            ],
                            ...
                        }
                    }
                },
                ...
            }
        """
        options_by_brand_line_model_trim = {}
        
        for brand_name, records in brand_data.items():
            brand_options = {}
            
            for record in records:
                if record.get('RowType') != 'OPTION':
                    continue
                
                vehicle_name = record.get('차량명')
                model = record.get('Model')
                trim = record.get('Trim')  # OPTION 행에서는 적용할 Trim
                option_group = record.get('OptionGroup')  # 옵션 그룹
                option_name = record.get('OptionName')
                price = record.get('Price')
                
                if all([vehicle_name, model, trim, option_name]) and all([v and str(v).strip() for v in [vehicle_name, model, trim, option_name]]):
                    vehicle_line = self._extract_vehicle_line_name(vehicle_name)
                    if vehicle_line:
                        if vehicle_line not in brand_options:
                            brand_options[vehicle_line] = {}
                        if model not in brand_options[vehicle_line]:
                            brand_options[vehicle_line][model] = {}
                        if trim not in brand_options[vehicle_line][model]:
                            brand_options[vehicle_line][model][trim] = []
                        
                        option_data = {
                            'name': option_name.strip(),
                            'group': option_group.strip() if option_group else '',
                            'price': self._parse_price(price) if price else 0
                        }
                        brand_options[vehicle_line][model][trim].append(option_data)
            
            options_by_brand_line_model_trim[brand_name] = brand_options
        
        return options_by_brand_line_model_trim
    
    @staticmethod
    def _extract_vehicle_line_name(vehicle_name: str) -> str:
        """
        차량명에서 VehicleLine 이름 추출
        예: "2026 아반떼" → "아반떼"
        """
        if not vehicle_name:
            return ""
        
        # 년도와 공백 제거 후 브랜드명 제거
        name = str(vehicle_name).strip()
        
        # 년도 패턴 제거 (예: "2026 ", "2025 ")
        import re
        name = re.sub(r'^\d{4}\s*', '', name)
        
        # 브랜드명 제거 (현대, 기아 등)
        brand_names = ['현대', '기아', '제네시스', '쉐보레', '르노삼성']
        for brand in brand_names:
            if name.startswith(brand):
                name = name[len(brand):].strip()
                break
        
        return name
    
    @staticmethod
    def _parse_price(value) -> Optional[int]:
        """가격 파싱 (쉼표 제거 및 다양한 형식 지원)"""
        print(f"[DEBUG] ExcelParser._parse_price 호출 - 원본 값: {value} (타입: {type(value)})")
        
        if value is None:
            print(f"[DEBUG] ExcelParser._parse_price - 값이 None")
            return 0
            
        if value == '' or value == ' ':
            print(f"[DEBUG] ExcelParser._parse_price - 값이 빈 문자열")
            return 0
            
        try:
            # 문자열로 변환
            price_str = str(value).strip()
            print(f"[DEBUG] ExcelParser._parse_price - 문자열 변환 후: '{price_str}'")
            
            # 빈 문자열 체크
            if not price_str or price_str == 'nan' or price_str.lower() == 'none':
                print(f"[DEBUG] ExcelParser._parse_price - 빈 문자열 또는 nan")
                return 0
            
            # 쉼표 제거
            price_str = price_str.replace(',', '').replace(' ', '')
            print(f"[DEBUG] ExcelParser._parse_price - 쉼표 제거 후: '{price_str}'")
            
            # 숫자로 변환
            if '.' in price_str:
                # 소수점이 있으면 float로 변환 후 int로 변환
                result = int(float(price_str))
            else:
                # 정수로 직접 변환
                result = int(price_str)
                
            print(f"[DEBUG] ExcelParser._parse_price - 최종 결과: {result}")
            return result
            
        except ValueError as e:
            print(f"[DEBUG] ExcelParser._parse_price - 숫자 변환 실패: {e}")
            return 0
        except Exception as e:
            print(f"[DEBUG] ExcelParser._parse_price - 예상치 못한 오류: {e}")
            return 0