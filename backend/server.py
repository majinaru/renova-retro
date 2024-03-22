from flask import Flask, request, jsonify, send_from_directory
import os
from flask_cors import CORS
import subprocess
import logging

app = Flask(__name__)
CORS(app, origins=["http://localhost:4200"])

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/process-image', methods=['POST'])
def upload_image():
    file = request.files['image']
    if file:
        filename = "uploaded_image.jpg"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Salva a imagem original temporariamente
        file.save(file_path)
        logging.info(f'Imagem salva em: {file_path}')

        # Chama o script de processamento de imagem
        process_path = os.path.join(app.config['UPLOAD_FOLDER'], 'image_processing.py')
        result = subprocess.run(['python', process_path, file_path], check=True)
        logging.info(f'Script de processamento executado: {result}')

        processed_image_filename = 'voronoi_diagram.png'
        processed_image_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_image_filename)
        
        # Verifica se a imagem processada existe
        if os.path.exists(processed_image_path):
            url = f'/uploads/{processed_image_filename}'
            logging.info(f'Enviando URL da imagem processada: {url}')
            return jsonify({"processedImageUrl": url})
        else:
            logging.error("Imagem processada não encontrada.")
            return jsonify(error="Image processing failed."), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)
