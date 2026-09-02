from pdf_generator import generate_pdf
import traceback

try:
    print('Starting...')
    res = generate_pdf(r'C:\Users\hi\Documents\Images2PDF\Content', r'C:\Users\hi\Documents\Images2PDF\Content\Report.pdf')
    print('Result:', res)
except Exception as e:
    print('Error!')
    traceback.print_exc()
