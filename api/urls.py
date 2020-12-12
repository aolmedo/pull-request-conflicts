from django.urls import path
from api.views import PullRequestsDatasets

urlpatterns = [
    path('pull-request-datasets', PullRequestsDatasets.as_view(), name='api_pull_request_datasets'),
]