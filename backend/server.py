from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/process-image', methods=['POST'])
def upload_image():
    file = request.files['image']
    if file:
        filename = "processed_image"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Salva a imagem original temporariamente
        temp_path = file_path + "_temp"
        file.save(temp_path)

        # Abre a imagem original e redimensiona
        with Image.open(temp_path) as img:
            # Converte para RGB se a imagem for RGBA (contém canal alfa)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            img.thumbnail((800, 800))  # Redimensiona a imagem
            img.save(file_path, "JPEG")  # Salva a imagem redimensionada

        # Remove a imagem original temporária
        os.remove(temp_path)

        return jsonify(processedImageUrl=f'/uploads/{filename}')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
