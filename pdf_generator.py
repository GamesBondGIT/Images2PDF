import os
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, LETTER
from PIL import Image

def get_page_size(size_str):
    if size_str.upper() == 'LETTER':
        return LETTER
    return A4

def draw_section_page(c, title, settings, width, height):
    sec_settings = settings.get('section_pages', {})
    if sec_settings.get('enabled', True):
        c.setFont(sec_settings.get('font', 'Helvetica-Bold'), sec_settings.get('font_size', 48))
        c.drawCentredString(width / 2.0, height / 2.0, title)
        c.showPage()

def draw_image_grid(c, images_list, grid_settings, settings, width, height, margin, progress_callback, current_progress_count, total_images):
    cols = grid_settings.get('columns', 2)
    rows = grid_settings.get('rows', 2)
    spacing = grid_settings.get('spacing', 20)
    
    img_settings = settings.get('images', {})
    show_title = img_settings.get('show_title', True)
    title_font = img_settings.get('title_font', 'Helvetica')
    title_font_size = img_settings.get('title_font_size', 12)
    title_spacing = img_settings.get('title_spacing', 15)

    images_per_page = cols * rows
    usable_width = width - (2 * margin) - (spacing * (cols - 1))
    usable_height = height - (2 * margin) - (spacing * (rows - 1))
    cell_w = usable_width / cols
    cell_h = usable_height / rows

    for i in range(0, len(images_list), images_per_page):
        chunk = images_list[i:i+images_per_page]
        for j, img_data in enumerate(chunk):
            col = j % cols
            row = j // cols
            
            x = margin + (col * (cell_w + spacing))
            y_top = height - margin - (row * (cell_h + spacing))
            
            try:
                img = Image.open(img_data['path'])
                img_w, img_h = img.size
                
                available_img_h = cell_h
                if show_title:
                    available_img_h -= (title_font_size + title_spacing)
                
                aspect = img_w / float(img_h)
                draw_w = cell_w
                draw_h = cell_w / aspect
                
                if draw_h > available_img_h:
                    draw_h = available_img_h
                    draw_w = available_img_h * aspect
                
                # Center the combined block (image + title) vertically in the cell
                block_h = draw_h
                if show_title:
                    block_h += (title_font_size + title_spacing)
                
                empty_v_space = cell_h - block_h
                block_top = y_top - (empty_v_space / 2)
                
                target_w = int(draw_w * 3)
                target_h = int(draw_h * 3)
                if img_w > target_w or img_h > target_h:
                    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
                
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                    
                from reportlab.lib.utils import ImageReader
                img_reader = ImageReader(img)

                img_x = x + (cell_w - draw_w) / 2
                img_y = block_top - draw_h

                
                c.drawImage(img_reader, img_x, img_y, width=draw_w, height=draw_h, preserveAspectRatio=True, anchor='c')
                
                if show_title:
                    c.setFont(title_font, title_font_size)
                    title_text = f"{img_data['category']}: {img_data['name']}"
                    title_text = title_text.encode('latin-1', 'ignore').decode('latin-1')
                    title_x = x + (cell_w / 2)
                    title_y = img_y - title_spacing
                    c.drawCentredString(title_x, title_y, title_text)
                    
            except Exception as e:
                pass
            
            current_progress_count += 1
            if progress_callback and total_images > 0:
                progress_callback(int((current_progress_count / total_images) * 100))
        
        c.showPage()
    
    return current_progress_count

def generate_pdf(source_dir, output_path, settings_path="settings.json", progress_callback=None):
    with open(settings_path, 'r') as f:
        settings = json.load(f)

    page_size = get_page_size(settings.get('page_size', 'A4'))
    c = canvas.Canvas(output_path, pagesize=page_size)
    width, height = page_size
    margin = settings.get('margin', 50)
    
    # Draw Title Page
    if settings.get('title_page', {}).get('enabled', True):
        title_settings = settings['title_page']
        c.setFont(title_settings.get('font', 'Helvetica-Bold'), title_settings.get('title_font_size', 36))
        c.drawCentredString(width / 2.0, height / 2.0 + 50, title_settings.get('title_text', 'Image Gallery Report'))
        
        c.setFont(title_settings.get('font', 'Helvetica'), title_settings.get('subtitle_font_size', 18))
        c.drawCentredString(width / 2.0, height / 2.0, title_settings.get('subtitle_text', 'Generated automatically'))
        c.showPage()

    posters = []
    videos = []
    
    for root, dirs, files in os.walk(source_dir):
        folder_name = os.path.basename(root)
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                img_data = {
                    'path': os.path.join(root, file),
                    'name': os.path.splitext(file)[0]
                }
                if 'videothumbs' in root.lower():
                    img_data['category'] = 'Videos'
                    videos.append(img_data)
                else:
                    img_data['category'] = 'Posters'
                    posters.append(img_data)

    total_images = len(posters) + len(videos)
    if total_images == 0:
        return False

    current_progress = 0

    # Process Posters
    if posters:
        draw_section_page(c, "POSTERS", settings, width, height)
        grid_settings = settings.get('posters_grid', {'columns': 2, 'rows': 2, 'spacing': 20})
        current_progress = draw_image_grid(c, posters, grid_settings, settings, width, height, margin, progress_callback, current_progress, total_images)

    # Process Videos
    if videos:
        draw_section_page(c, "VIDEOS", settings, width, height)
        grid_settings = settings.get('videos_grid', {'columns': 2, 'rows': 3, 'spacing': 20})
        current_progress = draw_image_grid(c, videos, grid_settings, settings, width, height, margin, progress_callback, current_progress, total_images)

    # Draw End Page
    if settings.get('end_page', {}).get('enabled', True):
        end_settings = settings.get('end_page', {})
        c.setFont(end_settings.get('font', 'Helvetica-Oblique'), end_settings.get('font_size', 24))
        c.drawCentredString(width / 2.0, height / 2.0, end_settings.get('text', 'End of Report'))
        c.showPage()
        
    c.save()
    if progress_callback:
        progress_callback(100)
    return True
