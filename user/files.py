import time
from django.core.files.storage import FileSystemStorage

def upload(cheque_image, file_name):
    try:
        print(f'1 {cheque_image}')
        fs = FileSystemStorage()
        print(f'3 {fs}')

        filename = fs.save(f"C:\\Users\\viraj\\Projects\\ocd-sample\\static\\images\\{file_name}", cheque_image)
        print(f'5 {filename}')
        uploaded_file_url = fs.url(filename)
        print(f'6 {uploaded_file_url}')
        return True
    except Exception as e:
        return False