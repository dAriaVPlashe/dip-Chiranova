from django.urls import path
from .views import (login_view,
                    MyPasswordResetView,
                    MyPasswordResetDone,
                    MyPasswordResetConfirmView,
                    MyPasswordResetCompleteView,
                    User_list,
                    Change_permission)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', login_view, name='login'),
    path('password_reset/', MyPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', MyPasswordResetDone.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', MyPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', MyPasswordResetCompleteView.as_view(), name='password_reset_complete'),

]
