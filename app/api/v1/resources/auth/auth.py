from fastapi import APIRouter, HTTPException, Depends
from app.api.v1.dependencies.container_instance import get_auth_service
from app.api.v1.models.requests.auth.auth_request import OtpRequest, OtpVerificationRequest, \
    OtpRequestModelResponse
from app.api.v1.models.responses.auth.auth_response import OtpVerificationModelResponse, \
    OtpVerificationSuccessModelResponse
from app.exceptions.hygge_exceptions import UnauthorizedError
from app.utils.logger import logger

auth_router = APIRouter(tags=["Authorization"])


@auth_router.post("/user", response_model=OtpRequestModelResponse)
async def request_otp(req_body: OtpRequest,
                      auth_service=Depends(get_auth_service)):
    try:
        body = auth_service.request_otp(req_body, req_body.country_code)
        return OtpRequestModelResponse(**body)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=403, detail=str(e))


@auth_router.post('/{state_token}', response_model=OtpVerificationSuccessModelResponse)
async def verify_otp(
        state_token: str,
        req_body: OtpVerificationRequest,
        auth_service=Depends(get_auth_service)):
    body = auth_service.verify_otp(req_body, state_token)
    if body['status'] == 'OTP_RESTRICTED' or body['status'] == 'OTP_FAILED':
        return OtpVerificationModelResponse(**body)
    if body and body['status'] == 'SUCCESS':
        return OtpVerificationSuccessModelResponse(**body)
    raise UnauthorizedError()
