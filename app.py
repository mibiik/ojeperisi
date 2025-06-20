import os
import google.generativeai as genai
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from PIL import Image
import io

# .env dosyasındaki değişkenleri yükle
load_dotenv()

app = Flask(__name__, static_folder='../public', static_url_path='')
CORS(app)

# Google Gemini API'ını yapılandır
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY bulunamadı. Lütfen .env dosyasını kontrol edin.")
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"API Yapılandırma Hatası: {e}")
    # Uygulamanın çökmemesi için bir varsayılan davranış belirleyebilirsiniz.
    # Örneğin, API anahtarı olmadan çalışmayı engelleyebilirsiniz.


# Gemini Pro Vision modelini hazırla (Güncel model ile değiştirildi)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/')
def index():
    return send_from_directory('../', 'index.html')

@app.route('/analyze', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({'error': 'Resim dosyası bulunamadı.'}), 400

    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'Dosya seçilmedi.'}), 400

    try:
        # Gelen dosyayı bir PIL Image nesnesine çevir
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))

        # Gemini API'ına gönderilecek prompt (Renk Uzmanı Perisi Versiyonu)
        prompt = """
        Sen bir "Oje Renk Perisi"sin. Sevimli, meraklı ve renkler konusunda uzmansın. Görevin, sana gönderilen görsellerdeki oje renklerini tanımlamak.

        İlk olarak, görselin bir oje, sürülmüş bir tırnak, oje şişesi veya bir renk örneği içerip içermediğini kontrol et.

        EĞER GÖRSEL ALAKASIZSA (örneğin bir araba, bir hayvan, bir manzara resmi gibi), oje rengi analizi YAPMA. Bunun yerine, SADECE şu formatta bir JSON nesnesi döndür:
        {
          "error": "irrelevant_image",
          "message": "Ayy, bu resimde oje göremedim sanki! Ben en güzel renkleri ojeli tırnaklardan veya oje şişelerinden bulabiliyorum. Bana öyle bir resim yükler misin? 💅💖"
        }

        EĞER GÖRSEL UYGUNSA (oje, tırnak veya renk örneği içeriyorsa), görseldeki ana oje rengini, özellikle tırnakların üzerindeki renge odaklanarak analiz et. Ardından, SADECE şu formatta bir JSON nesnesi döndür:
        {
          "colorName": "Bu renk için bulduğun şiirsel ve Türkçe bir isim (örneğin 'Pudra Pembesi', 'Gece Yarısı Mavisi').",
          "hexCode": "Rengin HEX kodu (örneğin '#FFB6C1').",
          "aiComment": "Rengin kendisi hakkında nesnel ve sevimli bir yorum yap. Kişisel iltifat yerine rengin tonunu, canlılığını veya yarattığı hissi anlat (örneğin 'Bu, içinde hafif ışıltılar barındıran sıcak bir pembe tonu.', 'Canlı ve enerjik bir mercan rengi, tam bir yaz enerjisi!', 'Derin ve asil bir bordo, çok şık duruyor.')."
        }

        Lütfen başka hiçbir açıklama veya metin ekleme. Sadece istenen formatta JSON çıktısı ver.
        """
        
        # Daha tutarlı sonuçlar için generation_config ayarı
        generation_config = genai.types.GenerationConfig(temperature=0.2)

        # Modeli çalıştır ve yanıtı al
        response = model.generate_content(
            [prompt, image],
            generation_config=generation_config
        )
        
        # Yanıtın metin kısmındaki JSON'ı temizle ve parse et
        # Bazen model JSON'ı markdown kod bloğu içine koyabilir
        cleaned_response_text = response.text.strip().replace('```json', '').replace('```', '').strip()
        
        import json
        result_json = json.loads(cleaned_response_text)

        # AI'dan gelen bir hata mesajı olup olmadığını kontrol et
        if 'error' in result_json and result_json['error'] == 'irrelevant_image':
            return jsonify(result_json), 400 # 400 Bad Request durumuyla gönder

        return jsonify(result_json)

    except Exception as e:
        print(f"Hata oluştu: {e}")
        return jsonify({'error': f'Görsel analiz edilirken bir sunucu hatası oluştu: {str(e)}'}), 500

if __name__ == '__main__':
    # Gunicorn olmadan, sadece yerel geliştirme için çalıştırırken kullanılacak.
    # Render gibi servisler kendi portlarını atar ve uygulamayı gunicorn ile başlatır.
    app.run(debug=True, port=5001) 