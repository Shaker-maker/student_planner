"""
Custom middleware for security and cache control.
Prevents browser caching of authenticated pages to prevent security issues 
when user goes back/forward after logout.
"""
from django.utils.deprecation import MiddlewareMixin


class NoCacheMiddleware(MiddlewareMixin):
    """
    Adds cache control headers to prevent browsers from caching sensitive pages.
    This prevents users from seeing cached pages after logout using browser back/forward buttons.
    
    Security Impact:
    - Prevents viewing cached authenticated pages after logout
    - Prevents access to admin panel via browser history
    - Ensures fresh page loads for security-sensitive views
    """
    
    def process_response(self, request, response):
        """
        Add cache control headers to all responses.
        """
        # Add cache control headers to disable caching
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response
