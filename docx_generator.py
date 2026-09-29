import os
import json
from docx import Document
from docx.shared import Inches, Mm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image

def get_page_dimensions(size_str):
    # Returns (width, height) in Mm
    if size_str.upper() == 'LETTER':
        return Mm(215.9), Mm(279.4)
    # A4
    return Mm(210.0), Mm(297.0)

def set_page_size(document, width, height):
    for section in document.sections:
        section.page_width = width
        section.page_height = height
        # Set margins to something reasonable to emulate PDF
        section.top_margin = Mm(15)
        section.bottom_margin = Mm(15)
        section.left_margin = Mm(15)
        section.right_margin = Mm(15)

def draw_section_page(document, title, settings):
    sec_settings = settings.get('section_pages', {})
    if sec_settings.get('enabled', True):
        document.add_page_break()
        # Add some empty paragraphs to push the title down
        for _ in range(10):
            document.add_paragraph()
            
        p = document.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(title)
        run.bold = True
        run.font.size = Pt(sec_settings.get('font_size', 48))
        document.add_page_break()

def draw_image_grid(document, images_list, grid_settings, settings, progress_callback, current_progress_count, total_images):
    cols = grid_settings.get('columns', 2)
    rows = grid_settings.get('rows', 2)
    
    img_settings = settings.get('images', {})
    show_title = img_settings.get('show_title', True)
    title_font_size = img_settings.get('title_font_size', 12)

    images_per_page = cols * rows
    
    # Calculate cell width in inches based on A4 width minus margins (approx 7.5 inches usable)
    section = document.sections[0]
    usable_width = section.page_width.inches - section.left_margin.inches - section.right_margin.inches
    cell_width_inches = (usable_width / cols) * 0.95 # slight reduction to prevent overflowing

    for i in range(0, len(images_list), images_per_page):
        if i > 0:
            document.add_page_break()
            
        chunk = images_list[i:i+images_per_page]
        
        # Word Tables need exact row counts.
        # If we have less than a full page, we still create the full table structure to maintain layout.
        table = document.add_table(rows=rows, cols=cols)
        table.autofit = False
        
        for c in table.columns:
            c.width = Inches(cell_width_inches)
            
        for j, img_data in enumerate(chunk):
            col = j % cols
            row = j // cols
            
            cell = table.cell(row, col)
            cell.width = Inches(cell_width_inches)
            
            try:
                # To prevent memory issues with huge images in Word, resize first
                img = Image.open(img_data['path'])
                
                # A quick downscale to standard screen resolution
                img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
                
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                    
                # Save to a temporary file
                temp_path = img_data['path'] + ".tmp.jpg"
                img.save(temp_path, "JPEG", quality=85)
                
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run()
                run.add_picture(temp_path, width=Inches(cell_width_inches * 0.9))
                
                if show_title:
                    p_title = cell.add_paragraph()
                    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    title_text = f"{img_data['category']}: {img_data['name']}"
                    title_run = p_title.add_run(title_text)
                    title_run.font.size = Pt(title_font_size)
                    
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
            except Exception as e:
                pass
            
            current_progress_count += 1
            if progress_callback and total_images > 0:
                progress_callback(int((current_progress_count / total_images) * 100))
                
    return current_progress_count

def generate_docx(source_dir, output_path, settings_path="settings.json", progress_callback=None):
    with open(settings_path, 'r') as f:
        settings = json.load(f)

    document = Document()
    page_w, page_h = get_page_dimensions(settings.get('page_size', 'A4'))
    set_page_size(document, page_w, page_h)
    
    # Draw Title Page
    if settings.get('title_page', {}).get('enabled', True):
        # Push down
        for _ in range(8):
            document.add_paragraph()
            
        title_settings = settings['title_page']
        
        p = document.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = p.add_run(title_settings.get('title_text', 'I&I Content Report'))
        title_run.bold = True
        title_run.font.size = Pt(title_settings.get('title_font_size', 36))
        
        p2 = document.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sub_run = p2.add_run(title_settings.get('subtitle_text', 'Images & Posters'))
        sub_run.font.size = Pt(title_settings.get('subtitle_font_size', 18))
        
    posters = []
    videos = []
    
    for root, dirs, files in os.walk(source_dir):
        # Ignore the 'Videos' directory so we don't accidentally grab random images inside it
        dirs[:] = [d for d in dirs if d.lower() != 'videos']
        
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')) and not file.endswith('.tmp.jpg'):
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
        draw_section_page(document, "POSTERS", settings)
        grid_settings = settings.get('posters_grid', {'columns': 2, 'rows': 2, 'spacing': 20})
        current_progress = draw_image_grid(document, posters, grid_settings, settings, progress_callback, current_progress, total_images)

    # Process Videos
    if videos:
        draw_section_page(document, "VIDEOS", settings)
        grid_settings = settings.get('videos_grid', {'columns': 2, 'rows': 3, 'spacing': 20})
        current_progress = draw_image_grid(document, videos, grid_settings, settings, progress_callback, current_progress, total_images)

    # Draw End Page
    if settings.get('end_page', {}).get('enabled', True):
        document.add_page_break()
        for _ in range(12):
            document.add_paragraph()
            
        end_settings = settings.get('end_page', {})
        p = document.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(end_settings.get('text', 'End of Report'))
        run.italic = True
        run.font.size = Pt(end_settings.get('font_size', 24))
        
    document.save(output_path)
    if progress_callback:
        progress_callback(100)
    return True
