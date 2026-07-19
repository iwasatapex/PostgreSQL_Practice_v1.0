try:
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new('RGB', (128, 128), color='#667eea')
    draw = ImageDraw.Draw(img)
    draw.text((64, 50), "SQL", fill='white', anchor="mm")
    draw.text((64, 80), "📚", fill='white', anchor="mm")
    img.save('icon.png')
    print("✅ Icon created: icon.png")
except:
    print("ℹ️  PIL not installed. You can add a custom icon.png")
