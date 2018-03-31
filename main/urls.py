from django.conf.urls import url

from . import views

urlpatterns = [
        url(r'link/$', views.LinkView.as_view()),
        ]
