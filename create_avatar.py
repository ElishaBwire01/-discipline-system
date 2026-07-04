from PIL import Image, ImageDraw, ImageFont
import os

# Create media directory if needed
os.makedirs('media/profile_pics', exist_ok=True)

# Create a simple avatar
size = 150
img = Image.new('RGB', (size, size), color=(37, 99, 235))  # Blue background
draw = ImageDraw.Draw(img)

# Draw a circle
draw.ellipse([5, 5, size-5, size-5], fill=(37, 99, 235), outline=(255, 255, 255), width=3)

# Add text "A" for Admin
try:
    font = ImageFont.truetype("arial.ttf", 80)
except:
    font = ImageFont.load_default()

# Get text position
text = "A"
text_bbox = draw.textbbox((0, 0), text, font=font)
text_width = text_bbox[2] - text_bbox[0]
text_height = text_bbox[3] - text_bbox[1]
position = ((size - text_width) // 2, (size - text_height) // 2 - 10)

# Draw text
draw.text(position, text, fill=(255, 255, 255), font=font)

# Save the image
img.save('media/profile_pics/admin_default.png')
print("? Default admin avatar created: media/profile_pics/admin_default.png")
print("?? To use this image, upload it from your profile page.")