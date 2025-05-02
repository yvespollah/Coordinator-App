from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ManagerViewSet, WorkflowViewSet, TaskViewSet, SystemHealthView

router = DefaultRouter()
router.register(r'managers', ManagerViewSet, basename='manager')
router.register(r'workflows', WorkflowViewSet, basename='workflow')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('system-health/', SystemHealthView.as_view(), name='system-health'),
]
urlpatterns += router.urls