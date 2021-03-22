from django.core.exceptions import PermissionDenied
import functools


def login_required_return_denied(func):
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        else:
            raise PermissionDenied()
    return wrapper
