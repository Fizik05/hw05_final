
from django.conf import settings
from django.conf.urls import handler403, handler404, handler500
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

handler404 = "core.views.page_not_found"  # noqa
handler403 = "core.views.csrf_token"  # noqa
handler500 = "core.views.server_error"  # noqa

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("posts.urls", namespace="posts")),
    path("auth/", include("users.urls", namespace="users")),
    path("auth/", include("django.contrib.auth.urls")),
    path("about/", include("about.urls", namespace="about")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATICFILES_DIRS
    )
    import debug_toolbar

    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
