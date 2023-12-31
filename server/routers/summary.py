from typing import Any

from fastapi import APIRouter, Depends

from server.core.dependencies import get_cache
from server.models.dto.summary import SummaryResponseDto

router = APIRouter()


@router.get("/summary", response_model=SummaryResponseDto)
def get_summary(cache: dict[Any, Any] = Depends(get_cache)):
    return SummaryResponseDto(response_json_str=cache.get("summary_json_str", "{}"))
