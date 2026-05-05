"""Custom error handlers with logging"""

import logging
from django.shortcuts import render
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def page_not_found(request, exception=None):
    """Handle 404 errors with logging"""
    logger.warning(f"404 Not Found: {request.path} - User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}")
    
    if request.accepts('application/json'):
        return JsonResponse({
            'error': 'Not Found',
            'status': 404,
            'message': 'The requested resource could not be found.'
        }, status=404)
    
    return render(request, '404.html', status=404)


def server_error(request):
    """Handle 500 errors with logging and error reference"""
    import uuid
    error_ref = str(uuid.uuid4())[:8].upper()
    
    logger.error(
        f"500 Server Error [Ref: {error_ref}]: {request.path}",
        exc_info=True,
        extra={
            'status_code': 500,
            'request_path': request.path,
            'user_id': request.user.id if request.user.is_authenticated else 'Anonymous',
            'error_reference': error_ref,
        }
    )
    
    if request.accepts('application/json'):
        return JsonResponse({
            'error': 'Internal Server Error',
            'status': 500,
            'message': 'An unexpected error occurred.',
            'reference': error_ref
        }, status=500)
    
    return render(request, '500.html', {'error_ref': error_ref}, status=500)


def bad_request(request, exception=None):
    """Handle 400 errors with logging"""
    logger.warning(f"400 Bad Request: {request.path}")
    
    if request.accepts('application/json'):
        return JsonResponse({
            'error': 'Bad Request',
            'status': 400,
            'message': 'The request was invalid or malformed.'
        }, status=400)
    
    return render(request, '400.html', status=400)


def permission_denied(request, exception=None):
    """Handle 403 errors with logging"""
    logger.warning(
        f"403 Forbidden: {request.path} - User: {request.user.username if request.user.is_authenticated else 'Anonymous'}"
    )
    
    if request.accepts('application/json'):
        return JsonResponse({
            'error': 'Permission Denied',
            'status': 403,
            'message': 'You do not have permission to access this resource.'
        }, status=403)
    
    return render(request, '403.html', status=403)
