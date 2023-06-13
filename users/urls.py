from django.urls import path
from .views import home, profile, RegisterView
from users import views

urlpatterns = [
    path('', home, name='users-home'),
    path('register/', RegisterView.as_view(), name='users-register'),
    path('profile/', profile, name='users-profile'),
    path('predict/', views.predict, name='users-predicts'),
    path('predict/predictEmotion/',views.predictEmotion,name='users-predict'),
]
