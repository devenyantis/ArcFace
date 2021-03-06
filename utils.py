import numpy as np
import cv2
from torch.nn import functional as F
from PIL import Image
from torchvision import transforms
import torch

# transform_composed = transforms.Compose([
#     transforms.ToTensor(),
#     transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

transform_composed = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])])

def face_aligner(img, landmark=None, **kwargs):
    image_size = []
    str_image_size = kwargs.get('image_size', '')
    if len(str_image_size) > 0:
        image_size = [int(x) for x in str_image_size.split(',')]
        if len(image_size) == 1:
            image_size = [image_size[0], image_size[0]]
        assert len(image_size) == 2
        assert image_size[0] == 112
        assert image_size[0] == 112 or image_size[1] == 96
    if landmark is not None:
        assert len(image_size) == 2
        src = np.array([
            [30.2946, 51.6963],
            [65.5318, 51.5014],
            [48.0252, 71.7366],
            [33.5493, 92.3655],
            [62.7299, 92.2041]], dtype=np.float32)
        if image_size[1] == 112:
            src[:, 0] += 8.0
        dst = landmark.astype(np.float32)
        M = cv2.estimateAffinePartial2D(dst, src, method=cv2.LMEDS)
        M = M[0]

        assert len(image_size) == 2

        warped = cv2.warpAffine(img, M, (image_size[1], image_size[0]), borderValue=0.0)
        return warped

def get_embedding(model, image, tta, device):
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)
    elif isinstance(image, str):
        image = Image.open(str)

    if tta:
        mirror = transforms.functional.hflip(image)
        emb = model(transform_composed(image).to(device).unsqueeze(0))
        emb_mirror = model(transform_composed(mirror).to(device).unsqueeze(0))
        embedding = F.normalize(emb + emb_mirror)
    else:
        embedding = model(transform_composed(image).to(device).unsqueeze(0))

    # input_tensor = transform_composed(image).to(device)
    # input_tensor = torch.unsqueeze(input_tensor, 0)
    # embedding = model(input_tensor)

    return embedding
