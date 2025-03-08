import os
import pathlib as pth

import torch
import torchvision
import torchvision.transforms as transforms
from PIL import Image

from cat_or_roll.classifier.abc import Classifier, ClassifierError, ClassifierPrediction


class CatVsBunClassifier(Classifier):
    def __init__(self, model_location: pth.Path, device=None) -> None:
        self.__device = device if device else torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.__model = torchvision.models.resnet50(pretrained=False)
        self.__model.fc = torch.nn.Sequential(
            torch.nn.Linear(self.__model.fc.in_features, 512),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.5),
            torch.nn.Linear(512, 2)
        )
        
        if not os.path.exists(model_location):
            raise ClassifierError(f"Model file {model_location} not found.")
        
        self.__model.load_state_dict(torch.load(model_location, map_location=self.__device))
        self.__model = self.__model.to(self.__device)
        self.__model.eval()
        
        self.__transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        self.__classes = ["Cat", "Roll"]

    def classify(self, image_location: pth.Path) -> ClassifierPrediction:
        if not os.path.exists(image_location):
            raise ClassifierError(f"Image file {image_location} not found.")
        
        try:
            image = Image.open(image_location).convert("RGB")
        except Exception as error:
            raise ClassifierError(f"Failed to open image file {image_location}.") from error
        
        image_tensor = self.__transform(image).unsqueeze(0).to(self.__device)
        
        with torch.no_grad():
            outputs = self.__model(image_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
            class_name = self.__classes[predicted.item()]
            
        return ClassifierPrediction(label=class_name, confidence=confidence.item())