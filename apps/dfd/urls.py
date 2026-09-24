from vela.urls import path
from apps.dfd.views.workspace import workspace_view
urlpatterns = [path('/', workspace_view)]
