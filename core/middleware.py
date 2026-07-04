# core/middleware.py
import sys
import traceback
import json
from datetime import datetime
from django.http import JsonResponse
from django.conf import settings
import os

class ErrorLoggingMiddleware:
    """Middleware to log all errors and store them for the 500 page."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # Get full error details
            error_type = type(e).__name__
            error_message = str(e)
            error_traceback = traceback.format_exc()
            
            # Print to console with full details - IMMEDIATELY
            print("\n" + "="*80)
            print("🔴 DJANGO ERROR DETECTED - ADMIN DASHBOARD")
            print("="*80)
            print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📁 Error Type: {error_type}")
            print(f"📝 Error Message: {error_message}")
            print(f"📍 URL: {request.path}")
            print(f"👤 User: {request.user.username if request.user.is_authenticated else 'Anonymous'}")
            print("-"*80)
            print("🔍 Full Traceback:")
            print(error_traceback)
            print("="*80 + "\n")
            
            # Also log to file
            log_file = settings.BASE_DIR / 'error_logs.txt'
            try:
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n{'='*80}\n")
                    f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"URL: {request.path}\n")
                    f.write(f"User: {request.user.username if request.user.is_authenticated else 'Anonymous'}\n")
                    f.write(f"Error: {error_type}: {error_message}\n")
                    f.write(f"{'-'*80}\n")
                    f.write(error_traceback)
                    f.write(f"\n{'='*80}\n")
            except:
                pass
            
            # For API requests, return JSON error
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': error_message,
                    'type': error_type,
                    'path': request.path
                }, status=500)
            
            # Re-raise the exception for Django to handle
            raise
