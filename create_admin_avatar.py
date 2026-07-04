import os
from PIL import Image, ImageDraw, ImageFont
from django.contrib.auth.models import User
from core.models import TeacherProfile

# Create a simple colored square with initials
def create_placeholder_image(user, size=150):
    img = Image.new('RGB', (size, size), color=(37, 99, 235))
    d = ImageDraw.Draw(img)
    text = user.get_full_name()[:1].upper() if user.get_full_name() else user.username[:1].upper()
    
    try:
        font = ImageFont.truetype("arial.ttf", size//2)
    except:
        font = ImageFont.load_default()
    
    # Get text size and center it
    text_bbox = d.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    position = ((size - text_width) // 2, (size - text_height) // 2 - 10)
    d.text(position, text, fill=(255, 255, 255), font=font)
    
    # Save the image
    filename = f"media/profile_pics/admin_{user.id}.png"
    img.save(filename)
    return filename

print("Creating profile picture for admin...")
try:
    admin = User.objects.get(username='admin')
    profile = TeacherProfile.objects.get(user=admin)
    
    # Create image
    img_path = create_placeholder_image(admin)
    print(f"? Created image at: {img_path}")
    
    # Update profile
    from django.core.files import File
    with open(img_path, 'rb') as f:
        profile.profile_picture.save(f"admin_{admin.id}.png", File(f), save=True)
    print("? Profile picture updated for admin")
except User.DoesNotExist:
    print("?? Admin user not found")
except TeacherProfile.DoesNotExist:
    print("?? Teacher profile not found for admin")
except Exception as e:
    print(f"Error: {e}")