import cv2
import numpy as np
import pytesseract
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import re

class VisiOCR:
    @staticmethod
    def preprocess_image(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        processed_image = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 4)
        return processed_image

    @staticmethod
    def extract_info(image):
        processed_image = VisiOCR.preprocess_image(image)
        text = pytesseract.image_to_string(processed_image)
        print("Extracted Text:")
        print(text)
        name, birth_date = VisiOCR.parse_text(text) 
        return name, birth_date

    @staticmethod
    def parse_text(text):
        name = None
        birth_date = None
        
        # Extract Name from PAN card 
        name_match_pan = re.search(r'([A-Z]+[\s]+[A-Z]+[\s]+[A-Z]+[\s]+[A-z]+[\s])', text)
        # Extract Name from Aadhaar card 
        name_match_aadhaar = re.search(r'([A-Z][a-zA-Z\s]+[A-Z][a-zA-Z\s]+[A-Z][a-zA-Z]+)', text)
        if name_match_pan:
            name = name_match_pan.group(1).strip()
        elif name_match_aadhaar:
            name = name_match_aadhaar.group(0).strip()
            
        dob_match_pan = re.search(r'(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
        if dob_match_pan:
            birth_date = dob_match_pan.group(0).strip()

        dob_match_aadhaar = re.search(r'(\d{2}/\d{2}/\d{4})', text)
        if dob_match_aadhaar:
            birth_date = dob_match_aadhaar.group(1).strip()
        
        return name, birth_date
        
    @staticmethod
    def process_image(image):
        name, birth_date = VisiOCR.extract_info(image)

        if birth_date is None:
            return name, None, None 
        
        try:
            birth_date = datetime.strptime(birth_date, "%d/%m/%Y")
            age = (datetime.now() - birth_date).days // 365
        except (ValueError, TypeError):
            birth_date = None
            age = None

        return name, birth_date.strftime('%d/%m/%Y') if birth_date else None, age

    @staticmethod
    def generate_visiting_pass(name, birth_date, age):
        # Create a new image for the visiting pass
        visiting_pass = Image.new('RGB', (600, 400), (255, 255, 255))
        draw = ImageDraw.Draw(visiting_pass)

        # Add text to the visiting pass
        font = ImageFont.truetype('arial.ttf', size=30)
        draw.text((50, 50), f"Name: {name}", font=font, fill=(0, 0, 0))
        draw.text((50, 100), f"Date of Birth: {birth_date}", font=font, fill=(0, 0, 0))
        draw.text((50, 150), f"Age: {age}", font=font, fill=(0, 0, 0))

        # Save the visiting pass as an image file
        visiting_pass.save('visiting_pass.png')

        return 'visiting_pass.png'

class VisitorManagementSystem:
    @staticmethod
    @csrf_exempt  
    def upload_image(request):
        if request.method == 'POST' and 'image' in request.FILES:
            uploaded_file = request.FILES['image']
            image = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), -1)
            name, birth_date, age = VisiOCR.process_image(image)
            if birth_date is None and name is None:
                return render(request, 'home.html', {'error_message': "Image quality is too poor. Please try again."})
            visiting_pass_image = VisiOCR.generate_visiting_pass(name, birth_date, age)
            return render(request, 'home.html', {'name': name, 'birth_date': birth_date, 'age': age, 'visiting_pass_image': visiting_pass_image})  
        return render(request, 'home.html')

    @staticmethod
    @csrf_exempt 
    def capture_image(request):
        if request.method == 'POST':
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            name, birth_date, age = VisiOCR.process_image(frame)
            if birth_date is None and name is None:
                return render(request, 'home.html', {'error_message': "Image quality is too poor. Please try again."})
            visiting_pass_image = VisiOCR.generate_visiting_pass(name, birth_date, age)
            return render(request, 'home.html', {'name': name, 'birth_date': birth_date,'age': age, 'visiting_pass_image': visiting_pass_image})
        return render(request, 'home.html')

def home(request):
    return render(request, 'home.html')