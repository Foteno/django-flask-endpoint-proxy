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

sam_predictor_url = 'http://localhost:5000/post-point-sam'
mask_url = 'http://localhost:5000/get-mask'
choose_mask_url = 'http://localhost:5000/choose-mask'

@api_view(['POST'])
def post_picture(request):
    serializer = ImageSerializer(data=request.data)
    print(request.data)
    
    if serializer.is_valid():
        serializer.save()
        with open(serializer.data['image'][1:], 'rb') as f:
            image_bytes = f.read()
            # image = cv2.inpaint(image_bytes, 3, 3);
            print(f.name)
            image = cv2.imread(f.name)
            cv2.imshow('image',image_resize(image, width=400))
            cv2.waitKey()
            cv2.destroyAllWindows()
            print(get_prediction(image_bytes=image_bytes))
        return Response(get_prediction(image_bytes=image_bytes)[1], status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
def post_point_sam(request):
    coord_x = 'coord_x'
    coord_y = 'coord_y'
    coord_x_value = request.query_params.get(coord_x)
    coord_y_value = request.query_params.get(coord_y)

    image_path = None
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
    mask_file_value = request.query_params.get(mask_file)
    dilate_size = request.query_params.get(dilate_param)

    params = {mask_file: mask_file_value, dilate_param: dilate_size}
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