from flask import Flask, render_template_string, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Mapa za začasne datoteke
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Preveri sliko
        if 'image' not in request.files:
            return "Napaka: Ni naložene slike."
        
        file = request.files['image']
        if file.filename == '' or not allowed_file(file.filename):
            return "Napaka: Neveljavna datoteka (dovoljeno: PNG, JPG, GIF)."
        
        # Shrani začasno
        filename = secure_filename(file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(image_path) 
        
        # Pridobi tekst
        top_text = request.form.get('top_text', '').upper()
        bottom_text = request.form.get('bottom_text', '').upper()
        text_size = request.form.get('text_size', '')
        if text_size:
            text_size=int(text_size)
        else:
            text_size=-1
        
        # Generiraj meme
        meme_image = generate_meme(image_path, top_text, bottom_text, text_size)
        
        # Pošlji kot odziv
        return send_file(meme_image, mimetype='image/png', as_attachment=False)
    
    # HTML obrazec
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="sl">
    <head>
        <meta charset="UTF-8">
        <title>Meme Generator</title>
    </head>
    <body>
        <h1>Ustvari meme</h1>
        <form method="post" enctype="multipart/form-data">
            <label for="image">Naloži sliko:</label><br>
            <input type="file" id="image" name="image" accept="image/*" required><br><br>
                                              
            <label for="top_text">Zgornji tekst:</label><br>
            <input type="text" id="top_text" name="top_text"><br>
            
                                  
            <label for="bottom_text">Spodnji tekst:</label><br>
            <input type="text" id="bottom_text" name="bottom_text"><br><br>
                                  
            <label for="text_size">Velikost pisave:</label><br>
            <input type="number" id="text_size" name="text_size"><br><br>
            
            <input type="submit" value="Generiraj meme">
        </form>
    </body>
    </html>
    ''')

def generate_meme(image_path, top_text, bottom_text, font_size=-1):
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    width, height = img.size
    if  font_size<0:
        font_size = max(20, int(width / 15))
        if top_text and len(top_text) > 20:
            font_size = int(font_size * 0.8)
        if bottom_text and len(bottom_text) > 20:
            font_size = int(font_size * 0.8)
    

    # Naloži pisavo (uporabi Impact če na voljo, sicer Arial ali default)
    font_path = "impact.ttf" if os.path.exists("impact.ttf") else None
    try:
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    
    # Funkcija za risanje teksta z debelejšimi obrisi
    def draw_text_with_outline(text, x, y, outline_width=3,fill="white", outline_fill="black"):
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_fill)
        draw.text((x, y), text, font=font, fill=fill)
    
    # Zgornji tekst
    if top_text:
        text_width = draw.textlength(top_text, font=font)
        x = (width - text_width) / 2 #na sredino x koordinate slike
        y = 10 #10 pikslovc od vrha
        draw_text_with_outline(top_text, x, y, int(font_size/60))
    
    # Spodnji tekst
    if bottom_text:
        text_width = draw.textlength(bottom_text, font=font)
        x = (width - text_width) / 2
        y = height - font_size - 10
        draw_text_with_outline(bottom_text, x, y, int(font_size/60))
    
    # Shrani v pomnilnik
    meme_io = io.BytesIO()
    img.save(meme_io, 'PNG')
    meme_io.seek(0)
    
    # Čiščenje
    os.remove(image_path)
    
    return meme_io

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)