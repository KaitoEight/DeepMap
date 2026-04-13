import os
import torch
import torch.nn as nn
from torchvision import transforms as T
from PIL import Image
import requests
from io import BytesIO

# Import the model class
from human_perception_place_pulse.Model_01 import Net

# Assuming models are downloaded to ./human-perception-place-pulse/model
MODEL_DIR = "./human-perception-place-pulse/model"

perception = ['safety', 'lively', 'wealthy', 'beautiful', 'boring', 'depressing']
model_dict = {
    'safety': 'safety.pth',
    'lively': 'lively.pth',
    'wealthy': 'wealthy.pth',
    'beautiful': 'beautiful.pth',
    'boring': 'boring.pth',
    'depressing': 'depressing.pth',
}

transform = T.Compose([
    T.Resize((384, 384)),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

# Load all models
models = {}
for p in perception:
    model_path = os.path.join(MODEL_DIR, model_dict[p])
    if os.path.exists(model_path):
        model = torch.load(model_path, map_location=device)
        model.to(device)
        model.eval()
        models[p] = model
    else:
        print(f"Model for {p} not found at {model_path}")

def predict_scores(img):
    scores = {}
    img_tensor = transform(img).unsqueeze(0).to(device)
    
    for p, model in models.items():
        with torch.no_grad():
            pred = model(img_tensor)
            softmax = nn.Softmax(dim=1)
            score = softmax(pred)[0][1].item() * 10  # Scale to 0-10
            scores[p] = round(score, 2)
    
    return scores

def calculate_hot_score(scores):
    # Hot score: average of positive scores minus average of negative scores
    positive = (scores['safety'] + scores['lively'] + scores['wealthy'] + scores['beautiful']) / 4
    negative = (scores['boring'] + scores['depressing']) / 2
    return round(positive - negative, 2)

def get_street_view_image(lat, lon, api_key=None):
    # Placeholder: In real implementation, use Google Street View API
    # For now, return None or a default image
    if api_key:
        url = f"https://maps.googleapis.com/maps/api/streetview?size=400x400&location={lat},{lon}&key={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content)).convert("RGB")
    return None

def get_hot_score_for_poi(lat, lon, api_key=None):
    img = get_street_view_image(lat, lon, api_key)
    if img:
        scores = predict_scores(img)
        return calculate_hot_score(scores)
    else:
        # Fallback to type-based score
        return 5.0
