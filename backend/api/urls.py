from rest_framework.routers import DefaultRouter
from .views import ManagerViewSet, WorkflowViewSet, TaskViewSet, MachineViewSet, AvailabilityViewSet

router = DefaultRouter()
router.register(r'managers', ManagerViewSet)
router.register(r'workflows', WorkflowViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'machines', MachineViewSet)
router.register(r'availabilities', AvailabilityViewSet)

urlpatterns = router.urls
