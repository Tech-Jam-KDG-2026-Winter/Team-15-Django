from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from apps.condition_manager.models import ConditionLog, ExerciseMenu, Tag
from .forms import UserUpdateForm, ExerciseMenuForm, TagForm

User = get_user_model()

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = 'management/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # KEY METRICS
        context['total_users'] = User.objects.count()
        context['total_logs'] = ConditionLog.objects.count()
        context['total_exercises'] = ExerciseMenu.objects.count()
        
        # Recent data for graphs/tables
        last_30_days = timezone.now() - timedelta(days=30)
        context['new_users_30d'] = User.objects.filter(date_joined__gte=last_30_days).count()
        
        # Recent logs
        context['recent_logs'] = ConditionLog.objects.select_related('user').order_by('-created_at')[:5]

        return context

# --- User Management ---
class UserListView(StaffRequiredMixin, ListView):
    model = User
    template_name = 'management/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    ordering = ['-date_joined']

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(username__icontains=query) | queryset.filter(email__icontains=query)
        return queryset

class UserDetailView(StaffRequiredMixin, UpdateView):
    model = User
    template_name = 'management/user_detail.html'
    form_class = UserUpdateForm
    context_object_name = 'target_user'
    success_url = reverse_lazy('management:user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ユーザーの行動履歴などを表示する場合に備えて
        context['recent_logs'] = ConditionLog.objects.filter(user=self.object).order_by('-created_at')[:10]
        return context

# --- Exercise Menu Management ---
class ExerciseListView(StaffRequiredMixin, ListView):
    model = ExerciseMenu
    template_name = 'management/exercise_list.html'
    context_object_name = 'exercises'
    paginate_by = 20
    ordering = ['id']

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset

class ExerciseCreateView(StaffRequiredMixin, CreateView):
    model = ExerciseMenu
    form_class = ExerciseMenuForm
    template_name = 'management/exercise_form.html'
    success_url = reverse_lazy('management:exercise_list')

class ExerciseUpdateView(StaffRequiredMixin, UpdateView):
    model = ExerciseMenu
    form_class = ExerciseMenuForm
    template_name = 'management/exercise_form.html'
    success_url = reverse_lazy('management:exercise_list')

class ExerciseDeleteView(StaffRequiredMixin, DeleteView):
    model = ExerciseMenu
    template_name = 'management/exercise_confirm_delete.html'
    success_url = reverse_lazy('management:exercise_list')

# --- Tag Management ---
class TagListView(StaffRequiredMixin, ListView):
    model = Tag
    template_name = 'management/tag_list.html'
    context_object_name = 'tags'
    paginate_by = 20

class TagCreateView(StaffRequiredMixin, CreateView):
    model = Tag
    form_class = TagForm
    template_name = 'management/tag_form.html'
    success_url = reverse_lazy('management:tag_list')

class TagUpdateView(StaffRequiredMixin, UpdateView):
    model = Tag
    form_class = TagForm
    template_name = 'management/tag_form.html'
    success_url = reverse_lazy('management:tag_list')

class TagDeleteView(StaffRequiredMixin, DeleteView):
    model = Tag
    template_name = 'management/tag_confirm_delete.html'
    success_url = reverse_lazy('management:tag_list')
