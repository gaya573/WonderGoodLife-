"""
Excel Import API Router
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from app.application.use_cases import ExcelImportService
from ...dependencies import get_excel_import_service
from ...schemas import ImportResultResponse

router = APIRouter(prefix="/api/excel", tags=["excel"])


@router.get("/health")
def health_check():
    """헬스체크"""
    return {"status": "ok"}


@router.post("/import", response_model=ImportResultResponse)
async def import_excel(
    file: UploadFile = File(...),
    service: ExcelImportService = Depends(get_excel_import_service)
):
    """엑셀 파일 업로드 및 데이터 import"""
    
    # 파일 검증
    if not file.filename:
        raise HTTPException(status_code=400, detail="파일이 없습니다")
    
    if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        raise HTTPException(status_code=400, detail="엑셀 파일만 업로드 가능합니다 (.xlsx, .xls)")
    
    try:
        # 파일 읽기
        contents = await file.read()
        
        # 엑셀 import 실행
        result = await service.import_excel(contents)
        
        return ImportResultResponse(**result.__dict__)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"파일 처리 실패: {str(e)}"
        )