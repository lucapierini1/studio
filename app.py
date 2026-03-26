from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import os
import uuid

app = Flask(__name__)

# Cartella temporanea per i file scaricati
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'Nessun URL fornito'}), 400
    
    try:
        # Genera un ID unico per il file
        file_id = str(uuid.uuid4())
        output_filename = f"{file_id}.mp3"
        output_path = os.path.join(DOWNLOAD_FOLDER, output_filename)
        
        # Configurazione yt-dlp per estrarre audio di alta qualità
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',  # Qualità molto buona (320 kbps)
            }],
            'outtmpl': output_path.replace('.mp3', ''),
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'audio')
        
        # Pulisci il titolo per usarlo come nome file
        safe_title = "".join([c for c in title if c.isalnum() or c in ' -_']).strip()[:50]
        new_filename = f"{safe_title}_{file_id}.mp3"
        new_path = os.path.join(DOWNLOAD_FOLDER, new_filename)
        
        # Rinomina il file
        if os.path.exists(output_path):
            os.rename(output_path, new_path)
        
        return jsonify({
            'success': True,
            'filename': new_filename,
            'title': title
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({'error': 'File non trovato'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
