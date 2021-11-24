from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('home', views.home, name="home"),
    path('', views.findbus, name="findbus"),
    # path('findbus', views.findbus, name="findbus"),
    path('bookings/<int:pk>', views.bookings, name="bookings"),
    path('cancellings/<int:pk>', views.cancellings, name="cancellings"),
    path('payment/<int:pk>', views.payment, name="payment"),
    path('seebookings', views.seebookings, name="seebookings"),
    path('seeallbookings', views.seeallbookings, name="seeallbookings"),
    path('seeoldbookings', views.seeoldbookings, name="seeoldbookings"),
    path('seealloldbookings', views.seealloldbookings, name="seealloldbookings"),
    path('signup', views.signup, name="signup"),
    path('user_detail', views.user_detail, name="user_detail"),
    path('signin', views.signin, name="signin"),
    path('success', views.success, name="success"),
    path('signout', views.signout, name="signout"),
    # path('addbus',views.addbus,name='addbus'),
    
    path('handlerequest', views.handlerequest, name='handlerequest'),
    path('bus/all_bookings', views.bus_registration, name='registration'),
    path('bus/<int:pk>/', views.bus_detail, name='bus_detail'),
    path('bus/new/', views.bus_new, name='bus_new'),
    path('bus_bookings', views.bus_bookings, name='bus_bookings'),
    path('bus_bookings1', views.bus_bookings1, name='bus_bookings1'),
    path('bus/<int:pk>/edit/', views.bus_edit, name='bus_edit'),

    path('printticket/<int:pk>/', views.printticket, name='printticket'),

     path('reset_password/',
     auth_views.PasswordResetView.as_view(template_name="myapp/password_reset.html"),
     name="reset_password"),

    path('reset_password_sent/', 
        auth_views.PasswordResetDoneView.as_view(template_name="myapp/password_reset_sent.html"), 
        name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
     auth_views.PasswordResetConfirmView.as_view(template_name="myapp/password_reset_form.html"), 
     name="password_reset_confirm"),

    path('reset_password_complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name="myapp/password_reset_done.html"), 
        name="password_reset_complete"),


]

