from django.urls import path, include
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ManagerViewSet, WorkflowViewSet, TaskViewSet, SystemHealthView, 
    WorkflowStatusView, VolunteerStatusView, TaskPerformanceView,
    ResourceUtilizationView, CommunicationStatsView,
    ManagerRedisRegistrationView, ManagerRedisAuthView
)

router = DefaultRouter()
router.register(r'managers', ManagerViewSet, basename='manager')
router.register(r'workflows', WorkflowViewSet, basename='workflow')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('system-health/', SystemHealthView.as_view(), name='system-health'),
    path('analytics/workflows_by_status/', WorkflowStatusView.as_view(), name='workflows-by-status'),
    path('analytics/volunteers_by_status/', VolunteerStatusView.as_view(), name='volunteers-by-status'),
    path('analytics/task_performance/', TaskPerformanceView.as_view(), name='task-performance'),
    path('analytics/resource_utilization/', ResourceUtilizationView.as_view(), name='resource-utilization'),
    path('analytics/communication_stats/', CommunicationStatsView.as_view(), name='communication-stats'),
    path('auth/manager/register/', ManagerRedisRegistrationView.as_view(), name='manager-register'),
    path('auth/manager/login/', ManagerRedisAuthView.as_view(), name='manager-login'),
]
urlpatterns += router.urls