from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import ImageSerializer
from Removal.settings import get_prediction
import ipdb
import cv2
import requests
from PIL import Image
from io import BytesIO
from requests_toolbelt.multipart.encoder import MultipartEncoder
from enum import Enum

sam_predictor_url = 'http://localhost:5000/post-point-sam'
mask_url = 'http://localhost:5000/get-mask'
choose_mask_url_lama = 'http://localhost:5000/choose-mask'
choose_mask_url_gan = 'http://localhost:5001/choose-mask'
choose_mask_url_opencv = 'http://localhost:5002/choose-mask'

class InpaintingAlgorithm(Enum):
    LAMA = 'lama'
    TELEA = 'telea'
    NS = 'ns'
    GAN = 'gan'

@api_view(['POST'])
def post_point_sam(request):
    coord_x = 'coord_x'
    coord_y = 'coord_y'
    coord_x_value = request.query_params.get(coord_x)
    coord_y_value = request.query_params.get(coord_y)

    serializer = ImageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        image_path = '.' + serializer.data['image']

    with open(image_path, 'rb') as f:
        image_file = f.read()

    files = {'image': ('filename.jpg', image_file, 'image/jpeg')}
    params = {coord_x: coord_x_value, coord_y: coord_y_value}

    response = requests.post(sam_predictor_url, params=params, files=files)
    response_json = response.json()
    return Response({'masks': response_json['masks']}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_mask(request):
    mask_file = 'mask_file'
    mask_file_value = request.query_params.get(mask_file)

    params = {mask_file: mask_file_value}
    response_mask = requests.get(mask_url, params=params)

    response = Response(content_type='image/jpeg')
    response.content = response_mask.content

    return response

@api_view(['GET'])
def choose_mask(request):
    mask_file = 'mask_file'
    dilate_param = 'dilate'
    alg_param = 'inpainting'

    mask_file_value = request.query_params.get(mask_file)
    dilate_size = request.query_params.get(dilate_param)
    alg = request.query_params.get(alg_param)
    params = {mask_file: mask_file_value, dilate_param: dilate_size}

    alg = InpaintingAlgorithm(alg)
    if (alg == InpaintingAlgorithm.LAMA):
        choose_mask_url = choose_mask_url_lama
    elif (alg == InpaintingAlgorithm.GAN):
        choose_mask_url = choose_mask_url_gan
    elif (alg == InpaintingAlgorithm.TELEA):
        choose_mask_url = choose_mask_url_opencv

    response_image = requests.get(choose_mask_url, params=params)
    response = Response(content_type='image/jpeg')
    response.content = response_image.content
    
    return response

def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    
    dim = None
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))
    resized = cv2.resize(image, dim, interpolation = inter)
    return resized