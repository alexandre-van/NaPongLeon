
def process_image(img_content):
    from PIL import Image
    import io

    img = Image.open(io.BytesIO(img_content))

    # Resize 500x500
    img.thumbnail((500, 500))

    # For transparent imgs
    if img.mode != 'RGB':
        img = img.convert('RGB')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    return buffer