from django.contrib.auth.views import LogoutView
from django.urls import path
from clients.views import ClientListView, ClientCreateView, Client_cardDetailView, NewsletterListView, ClientUpdateView, \
    ClientDeleteView, NewsletterCreateView, Newsletter_cardDetailView, LogListView, UserLoginView, RegisterView, \
    ProfileView, ConfirmView, user_gen_password, NewsletterDeleteView, TaskToggleView, ClientBlockView
from clients.apps import ClientsConfig

app_name = ClientsConfig.name

urlpatterns = [
    path('home/', ClientListView.as_view(), name='home'),
    path("client_create/", ClientCreateView.as_view(), name="client_create"),
    path("client_detail/<int:pk>/", Client_cardDetailView.as_view(), name="client_detail"),
    path("client_update/<int:pk>/", ClientUpdateView.as_view(), name="client_update"),
    path("client_delete/<int:pk>/", ClientDeleteView.as_view(), name="client_delete"),
    path("client_block/<int:pk>/", ClientBlockView.as_view(), name="client_block"),
    path("newsletter_view/", NewsletterListView.as_view(), name="newsletter_view"),
    path("newsletter_detail/<int:pk>/", Newsletter_cardDetailView.as_view(), name="newsletter_detail"),
    path("newsletter_create/", NewsletterCreateView.as_view(), name="newsletter_create"),
    path("newsletter_delete/<int:pk>/", NewsletterDeleteView.as_view(), name="newsletter_delete"),
    path("log_view/", LogListView.as_view(), name="log_view"),

    path('', UserLoginView.as_view(template_name='clients/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('confirm/', ConfirmView.as_view(), name='confirm'),
    path('login/genpassword/', user_gen_password, name='genpassword'),


    path('task/<int:pk>/toggle/', TaskToggleView.as_view(), name='toggle_task'),
]
