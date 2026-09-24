from vela.urls import path
from apps.dfd.views.workspace import workspace_view

urlpatterns = [path('/', workspace_view)]

def register_routes(router):
    router.add('/', workspace_view, name='dfd_workspace', title='DFD Studio',
               icon='◈', layout='blank', show_in_sidebar=False)
