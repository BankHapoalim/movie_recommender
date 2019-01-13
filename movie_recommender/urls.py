from . import views

from django.conf.urls import url, include

urlpatterns = [
    url(r'^addData$', views.AddData.as_view()),
    url(r'^predictInterests$', views.PredictInterests.as_view()),

]


