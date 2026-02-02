from django.urls import path
from .views import upload_csv, get_summary, get_equipment_list, get_dataset_history, generate_pdf_report
from .auth_views import login, register, logout, user_info

urlpatterns = [
    path("upload/", upload_csv, name="upload_csv"),
    path("summary/", get_summary, name="get_summary"),
    path("equipment/", get_equipment_list, name="equipment_list"),
    path("datasets/", get_dataset_history, name="dataset_history"),
    path("report/pdf/", generate_pdf_report, name="generate_pdf_report"),
    # Authentication endpoints
    path("auth/login/", login, name="login"),
    path("auth/register/", register, name="register"),
    path("auth/logout/", logout, name="logout"),
    path("auth/user/", user_info, name="user_info"),
]
