"""API endpoints for user authentication using OTP."""

from fastapi import APIRouter, HTTPException, Depends

from app.api.v1.dependencies.container_instance import get_auth_service
from app.api.v1.models.requests.auth.auth_request import (
    OtpRequest, OtpVerificationRequest, OtpRequestModelResponse
)
from app.api.v1.models.responses.auth.auth_response import (
    OtpVerificationModelResponse, OtpVerificationSuccessModelResponse
)
from app.domain.interfaces.i_auth_service import IAuthService
from app.exceptions.hygge_exceptions import UnauthorizedError
from app.utils.logger import logger

auth_router = APIRouter(tags=["Authorization"])


@auth_router.post("/user", response_model=OtpRequestModelResponse)
async def request_otp(
    req_body: OtpRequest,
    auth_service: IAuthService = Depends(get_auth_service)
) -> OtpRequestModelResponse:
    """
    Request an OTP (One-Time Password) for phone number verification.

    Args:
        req_body: Request body containing phone number and country code.
        auth_service: Injected authentication service instance.

    Returns:
        Response indicating the status of the OTP request.

    Raises:
        HTTPException: If an error occurs during OTP request processing.
    """
    try:
        body = auth_service.request_otp(req_body, req_body.country_code)
        return OtpRequestModelResponse(**body)
    except Exception as e:
        logger.exception("Error requesting OTP: %s", e)
        raise HTTPException(status_code=403, detail=str(e)) from e


@auth_router.post(
    '/{state_token}',
    response_model=OtpVerificationSuccessModelResponse,
    responses={401: {"model": OtpVerificationModelResponse}}
)
async def verify_otp(
    state_token: str,
    req_body: OtpVerificationRequest,
    auth_service: IAuthService = Depends(get_auth_service)
) -> OtpVerificationSuccessModelResponse | OtpVerificationModelResponse:
    """
    Verify the provided OTP against the state token.

    Args:
        state_token: The state token received during the OTP request.
        req_body: Request body containing the OTP.
        auth_service: Injected authentication service instance.

    Returns:
        Success response with tokens if verification is successful,
        otherwise a response indicating failure or restriction.

    Raises:
        UnauthorizedError: If verification fails unexpectedly.
    """
    body = auth_service.verify_otp(req_body, state_token)
    if body['status'] in ('OTP_RESTRICTED', 'OTP_FAILED'):
        return OtpVerificationModelResponse(**body)
    if body and body['status'] == 'SUCCESS':
        return OtpVerificationSuccessModelResponse(**body)
    # Should not happen if service logic is correct, but raise error if it does
    logger.error("Unexpected OTP verification status: %s", body.get('status'))
    raise UnauthorizedError()
