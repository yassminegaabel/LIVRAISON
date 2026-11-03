import logging
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("app")


class AppError(Exception):
    """Erreur métier : les services la lèvent, le gestionnaire la transforme en réponse HTTP."""

    status_code = 400
    code = "bad_request"
    default_message = "Requête invalide"

    def __init__(self, message: str | None = None, *, details: Any = None) -> None:
        self.message = message or self.default_message
        self.details = details
        super().__init__(self.message)


class UnauthorizedError(AppError):
    status_code = 401
    code = "unauthorized"
    default_message = "Non authentifié"


class ForbiddenError(AppError):
    status_code = 403
    code = "forbidden"
    default_message = "Accès refusé"


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"
    default_message = "Ressource introuvable"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"
    default_message = "Conflit avec l'état actuel de la ressource"


_HTTP_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    409: "conflict",
    422: "validation_error",
    429: "too_many_requests",
}

_DEFAULT_MESSAGES = {
    400: "Requête invalide",
    401: "Non authentifié",
    403: "Accès refusé",
    404: "Ressource introuvable",
    405: "Méthode non autorisée",
    409: "Conflit avec l'état actuel de la ressource",
    429: "Trop de requêtes",
}


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: Any = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """Format unique de toutes les erreurs : {"error": {"code", "message", "details"?}}."""
    body: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=body, headers=headers)


def _http_phrase(status_code: int) -> str:
    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return ""


def _field_name(loc: tuple) -> str:
    parts = [str(part) for part in loc]
    if parts and parts[0] in {"body", "query", "path", "header", "cookie"}:
        source, *rest = parts
        return ".".join(rest) if rest else source
    return ".".join(parts)


def _clean_message(message: str) -> str:
    return message.removeprefix("Value error, ")


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return error_response(exc.status_code, exc.code, exc.message, exc.details)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else ""
    if not detail or detail == _http_phrase(exc.status_code):
        detail = _DEFAULT_MESSAGES.get(exc.status_code, "Erreur")
    code = _HTTP_CODES.get(exc.status_code, "http_error")
    return error_response(exc.status_code, code, detail, headers=exc.headers)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # On n'inclut jamais la valeur reçue ("input") : elle pourrait contenir un mot de passe.
    details = [
        {"field": _field_name(error["loc"]), "message": _clean_message(error["msg"])}
        for error in exc.errors()
    ]
    return error_response(422, "validation_error", "Données invalides", details)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Le détail technique va dans les journaux du serveur, jamais dans la réponse au client.
    logger.exception("Erreur non gérée sur %s %s", request.method, request.url.path)
    return error_response(500, "internal_error", "Erreur interne du serveur")


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
