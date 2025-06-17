from django.urls import path
from .views import (
    RecordListView,
    RecordDetailView,
    RecordCreateView,
    RecordUpdateView,
	DecryptPasswordView,
	generate_password_view,
	UserMessageCreateView,
	UserMessageListView,
	UserMessageDetailView,
    RecordDeleteView,
    RecordDeleteMessage,
    UserMessageUpdateView,
    RecordCreatePsView,
	Delete_response,
    serch_record,

	feedback_create,
	feedback_detail,
	feedback_list,
	feedback_edit,
	feedback_delete,



)
from . import views
urlpatterns = [
	path('', views.home, name='blog-home'),
	path('home/', RecordListView.as_view(), name='p_home'),
	path('record-results/',  serch_record, name='record-results'),
	path('about/', views.about, name='blog-about'),
	path('record/<int:pk>/', RecordDetailView.as_view(), name='record-detail'),
	path('record/new/', RecordCreateView.as_view(), name='record-create'),
	path('record/new-pass/', RecordCreatePsView.as_view(), name='record-pas-create'),
	path('decrypt_password/<int:record_id>/', DecryptPasswordView.as_view(), name='decrypt_password'),
	path('record/<pk>/decrypt-password/', DecryptPasswordView.as_view(), name='decrypt-password'),
	path('record/<int:pk>/update/', RecordUpdateView.as_view(), name='record-update'),
	path('record/<int:pk>/delete/', RecordDeleteView.as_view(), name='record-delete'),
	path('generate-password/', generate_password_view, name='generate-password'),
	path('messages/create/', UserMessageCreateView.as_view(), name='user_message_create'),
	path('messages/', UserMessageListView.as_view(), name='user_message_list'),
	path('messages/<int:message_id>/delete/', RecordDeleteMessage.as_view(), name='record-delete-Message'),
	path('messages/<int:message_id>/', UserMessageDetailView.as_view(), name='user_message_detail'),
	path('messages/<int:message_id>/update/', UserMessageUpdateView.as_view(), name='message-update'),
	path('response/delete/<int:response_id>/', Delete_response, name='delete-response'),
	path('feedback/add/', feedback_create, name='feedback_create'),
	path('feedback/<int:feedback_id>/', feedback_detail, name='user_feedback_detail'),
	path('feedbacks/', feedback_list, name='feedback_list'),
	path('feedback/edit/<int:feedback_id>/', feedback_edit, name='feedback_edit'),
	path('feedback/delete/<int:feedback_id>/', feedback_delete, name='feedback_delete'),


]