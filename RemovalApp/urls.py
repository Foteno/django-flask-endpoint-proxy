from django.urls import path
from RemovalApp.views import post_picture, post_point_sam, get_mask, choose_mask

urlpatterns = [
    path('post-picture', post_picture),
    path('post-point-sam', post_point_sam),
    path('get-mask', get_mask),
    path('choose-mask', choose_mask)
]