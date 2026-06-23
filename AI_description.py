import os
import requests
import json
import base64

def _load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())

_load_env()

def encode_image(image_path):
    """
    Function to encode image to base64 for sending to AI API.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_prompt_for_image(image_path):
    """
    Function to get the correct prompt depending on the image passed as argument.
    """
    # Get just the filename (e.g., "heat_map_0.png")
    filename = os.path.basename(image_path)
    
    if "heat_map" in filename:
        return "Analyze this heatmap. Provide a 3-sentence maximum response covering: 1. Location of highest intensity, 2. Shape, and 3. Classification (Point, Scratch, or Deformation). No intro or outro."
    elif "outlined_image" in filename:
        return "First, check if there is a visible red outline highlighting a specific area. If no red outline is present, state 'No outline detected' and describe the image as nominal. If a red outline exists: 1. Describe its precise location, 2. What it surrounds, and 3. The likely defect nature. Keep the total response under 3 sentences. No intro/outro."
    else:
        return "Perform a surface inspection of this image. Provide a 3-sentence maximum response: 1. State if the object appears nominal or if a defect is visible, 2. Describe the location and appearance of any irregularities, 3. Conclude with a primary classification. No intro or outro."
    
def make_description(image_path):
    """
    Function that writes a description for the image provided.
    """
    base64_image = encode_image(image_path)

    prompt = get_prompt_for_image(image_path)

    return requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json",
    },
    data=json.dumps({
        "model": "nvidia/nemotron-nano-12b-v2-vl:free",
        "messages": [
        {
            "role": "user",
            "content": [
            {
                "type": "text",
                "text": prompt
            },
            {
                "type": "image_url",
                "image_url": {
                # Use the Data URI format: data:<mime_type>;base64,<data>
                "url": f"data:image/png;base64,{base64_image}"
                }
            }
            ]
        }
        ]
    }),
    timeout=90
    )