from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ManagerViewSet, WorkflowViewSet, TaskViewSet

router = DefaultRouter()
router.register(r'managers', ManagerViewSet, basename='manager')
router.register(r'workflows', WorkflowViewSet, basename='workflow')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = router.urls