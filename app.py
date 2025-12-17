from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from flask_cors import CORS
import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import hashlib
import hmac
import secrets
import urllib.request
from pathlib import Path
from datetime import datetime
import re
import string
import random
import csv

APP_NAME = "SecureVault"
VERSION_URL = "https://raw.githubusercontent.com/MushhDev/db/main/version.txt"

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app)

DATA_DIR = "data"
ENCRYPTED_DIR = "encrypted"
USERS_FILE = f"{DATA_DIR}/users.json"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ENCRYPTED_DIR, exist_ok=True)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def hash_password(password):
    salt = secrets.token_hex(16)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return salt + pwdhash.hex()

def verify_password(stored_password, provided_password):
    salt = stored_password[:32]
    stored_hash = stored_password[32:]
    pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt.encode(), 100000)
    return pwdhash.hex() == stored_hash

def is_logged_in():
    return session.get('logged_in', False)

def generate_password(length=16, include_uppercase=True, include_lowercase=True, include_numbers=True, include_special=True):
    chars = ""
    if include_lowercase:
        chars += string.ascii_lowercase
    if include_uppercase:
        chars += string.ascii_uppercase
    if include_numbers:
        chars += string.digits
    if include_special:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not chars:
        chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def check_password_strength(password):
    score = 0
    feedback = []
    
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Mínimo 8 caracteres")
    
    if len(password) >= 12:
        score += 1
    
    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append("Agregar letras minúsculas")
    
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("Agregar letras mayúsculas")
    
    if re.search(r'[0-9]', password):
        score += 1
    else:
        feedback.append("Agregar números")
    
    if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        score += 1
    else:
        feedback.append("Agregar caracteres especiales")
    
    if len(password) >= 16:
        score += 1
    
    strength_levels = ["Muy Débil", "Débil", "Regular", "Buena", "Fuerte", "Muy Fuerte", "Excelente"]
    strength = strength_levels[min(score, len(strength_levels) - 1)]
    
    return {
        "score": score,
        "max_score": 7,
        "strength": strength,
        "feedback": feedback,
        "percentage": int((score / 7) * 100)
    }

def get_current_version():
    try:
        version_file = Path("version.txt")
        if version_file.exists():
            with open(version_file, "r") as f:
                return f.read().strip()
    except:
        pass
    return "1.0.0"

def check_updates():
    try:
        with urllib.request.urlopen(VERSION_URL, timeout=5) as response:
            latest_version = response.read().decode().strip()
            current_version = get_current_version()
            return {
                "current": current_version,
                "latest": latest_version,
                "update_available": latest_version != current_version
            }
    except:
        return {
            "current": get_current_version(),
            "latest": get_current_version(),
            "update_available": False
        }

class EncryptionManager:
    @staticmethod
    def derive_key(password, salt, iterations=100000):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        return kdf.derive(password.encode())

    @staticmethod
    def encrypt_level1(data, password):
        return base64.b64encode(data.encode()).decode()

    @staticmethod
    def decrypt_level1(data, password):
        return base64.b64decode(data.encode()).decode()

    @staticmethod
    def encrypt_level2(data, password):
        salt = secrets.token_bytes(16)
        key = hashlib.sha256((password + salt.hex()).encode()).digest()[:16]
        cipher = Cipher(algorithms.AES(key), modes.CBC(salt), backend=default_backend())
        encryptor = cipher.encryptor()
        padded_data = data.encode() + b'\0' * (16 - len(data.encode()) % 16)
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(salt + encrypted).decode()

    @staticmethod
    def decrypt_level2(data, password):
        decoded = base64.b64decode(data.encode())
        salt = decoded[:16]
        encrypted = decoded[16:]
        key = hashlib.sha256((password + salt.hex()).encode()).digest()[:16]
        cipher = Cipher(algorithms.AES(key), modes.CBC(salt), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encrypted) + decryptor.finalize()
        return decrypted.rstrip(b'\0').decode()

    @staticmethod
    def encrypt_level3(data, password):
        salt = secrets.token_bytes(16)
        key = hashlib.sha256((password + salt.hex()).encode()).digest()
        cipher = Cipher(algorithms.AES(key), modes.CBC(salt), backend=default_backend())
        encryptor = cipher.encryptor()
        padded_data = data.encode() + b'\0' * (16 - len(data.encode()) % 16)
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(salt + encrypted).decode()

    @staticmethod
    def decrypt_level3(data, password):
        decoded = base64.b64decode(data.encode())
        salt = decoded[:16]
        encrypted = decoded[16:]
        key = hashlib.sha256((password + salt.hex()).encode()).digest()
        cipher = Cipher(algorithms.AES(key), modes.CBC(salt), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encrypted) + decryptor.finalize()
        return decrypted.rstrip(b'\0').decode()

    @staticmethod
    def encrypt_level4(data, password):
        salt = secrets.token_bytes(16)
        key = EncryptionManager.derive_key(password, salt, 100000)
        cipher = Cipher(algorithms.AES(key), modes.CBC(salt), backend=default_backend())
        encryptor = cipher.encryptor()
        padded_data = data.encode() + b'\0' * (16 - len(data.encode()) % 16)
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(salt + encrypted).decode()

    @staticmethod
    def decrypt_level4(data, password):
        decoded = base64.b64decode(data.encode())
        salt = decoded[:16]
        encrypted = decoded[16:]
        key = EncryptionManager.derive_key(password, salt, 100000)
        cipher = Cipher(algorithms.AES(key), modes.CBC(salt), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encrypted) + decryptor.finalize()
        return decrypted.rstrip(b'\0').decode()

    @staticmethod
    def encrypt_level5(data, password):
        salt = secrets.token_bytes(16)
        key = EncryptionManager.derive_key(password, salt, 200000)
        cipher = Cipher(algorithms.AES(key), modes.CBC(salt), backend=default_backend())
        encryptor = cipher.encryptor()
        padded_data = data.encode() + b'\0' * (16 - len(data.encode()) % 16)
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        hmac_key = hashlib.sha256((password + salt.hex() + "hmac").encode()).digest()
        hmac_tag = hmac.new(hmac_key, encrypted, hashlib.sha256).digest()
        combined = salt + encrypted + hmac_tag
        return base64.b64encode(combined).decode()

    @staticmethod
    def decrypt_level5(data, password):
        decoded = base64.b64decode(data.encode())
        salt = decoded[:16]
        encrypted = decoded[16:-32]
        hmac_tag = decoded[-32:]
        hmac_key = hashlib.sha256((password + salt.hex() + "hmac").encode()).digest()
        expected_hmac = hmac.new(hmac_key, encrypted, hashlib.sha256).digest()
        if not hmac.compare_digest(hmac_tag, expected_hmac):
            raise ValueError("HMAC verification failed")
        key = EncryptionManager.derive_key(password, salt, 200000)
        cipher = Cipher(algorithms.AES(key), modes.CBC(salt), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encrypted) + decryptor.finalize()
        return decrypted.rstrip(b'\0').decode()

    @staticmethod
    def encrypt(data, password, level):
        methods = {
            1: EncryptionManager.encrypt_level1,
            2: EncryptionManager.encrypt_level2,
            3: EncryptionManager.encrypt_level3,
            4: EncryptionManager.encrypt_level4,
            5: EncryptionManager.encrypt_level5
        }
        return methods[level](data, password)

    @staticmethod
    def decrypt(data, password, level):
        methods = {
            1: EncryptionManager.decrypt_level1,
            2: EncryptionManager.decrypt_level2,
            3: EncryptionManager.decrypt_level3,
            4: EncryptionManager.decrypt_level4,
            5: EncryptionManager.decrypt_level5
        }
        return methods[level](data, password)

@app.route('/')
def index():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login')
def login():
    if is_logged_in():
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register')
def register():
    if is_logged_in():
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/api/version', methods=['GET'])
def get_version():
    return jsonify(check_updates())

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "")
    
    if not username or not password:
        return jsonify({"success": False, "error": "Usuario y contraseña requeridos"}), 400
    
    if len(password) < 8:
        return jsonify({"success": False, "error": "La contraseña debe tener al menos 8 caracteres"}), 400
    
    users = load_users()
    if username in users:
        return jsonify({"success": False, "error": "El usuario ya existe"}), 400
    
    users[username] = {
        "password": hash_password(password),
        "created": datetime.now().isoformat()
    }
    save_users(users)
    
    session['logged_in'] = True
    session['username'] = username
    
    return jsonify({"success": True})

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "")
    
    if not username or not password:
        return jsonify({"success": False, "error": "Usuario y contraseña requeridos"}), 400
    
    users = load_users()
    if username not in users:
        return jsonify({"success": False, "error": "Usuario o contraseña incorrectos"}), 401
    
    if not verify_password(users[username]["password"], password):
        return jsonify({"success": False, "error": "Usuario o contraseña incorrectos"}), 401
    
    session['logged_in'] = True
    session['username'] = username
    
    return jsonify({"success": True})

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"success": True})

@app.route('/api/auth/status', methods=['GET'])
def api_auth_status():
    return jsonify({
        "logged_in": is_logged_in(),
        "username": session.get('username', '')
    })

@app.route('/api/password/generate', methods=['POST'])
def api_generate_password():
    data = request.json or {}
    length = int(data.get("length", 16))
    include_uppercase = data.get("include_uppercase", True)
    include_lowercase = data.get("include_lowercase", True)
    include_numbers = data.get("include_numbers", True)
    include_special = data.get("include_special", True)
    
    password = generate_password(length, include_uppercase, include_lowercase, include_numbers, include_special)
    strength = check_password_strength(password)
    
    return jsonify({
        "success": True,
        "password": password,
        "strength": strength
    })

@app.route('/api/password/check', methods=['POST'])
def api_check_password():
    data = request.json
    password = data.get("password", "")
    strength = check_password_strength(password)
    return jsonify({"success": True, "strength": strength})

@app.route('/api/items', methods=['GET'])
def get_items():
    if not is_logged_in():
        return jsonify({"error": "No autorizado"}), 401
    
    search = request.args.get("search", "").lower()
    category = request.args.get("category", "")
    item_type = request.args.get("type", "")
    encrypted_only = request.args.get("encrypted_only", "false") == "true"
    
    items = []
    if os.path.exists(f"{DATA_DIR}/items.json"):
        with open(f"{DATA_DIR}/items.json", "r", encoding="utf-8") as f:
            items = json.load(f)
    
    filtered_items = items
    if search:
        filtered_items = [item for item in filtered_items if search in item.get("name", "").lower() or search in item.get("content", "").lower()]
    if category:
        filtered_items = [item for item in filtered_items if item.get("category", "") == category]
    if item_type:
        filtered_items = [item for item in filtered_items if item.get("type", "") == item_type]
    if encrypted_only:
        filtered_items = [item for item in filtered_items if item.get("encrypted", False)]
    
    return jsonify(filtered_items)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    if not is_logged_in():
        return jsonify({"error": "No autorizado"}), 401
    
    items = []
    if os.path.exists(f"{DATA_DIR}/items.json"):
        with open(f"{DATA_DIR}/items.json", "r", encoding="utf-8") as f:
            items = json.load(f)
    
    stats = {
        "total_items": len(items),
        "encrypted_items": len([i for i in items if i.get("encrypted", False)]),
        "text_items": len([i for i in items if i.get("type") == "text"]),
        "password_items": len([i for i in items if i.get("type") == "password"]),
        "file_items": len([i for i in items if i.get("type") == "file"]),
        "note_items": len([i for i in items if i.get("type") == "note"]),
        "by_level": {
            "1": len([i for i in items if i.get("level") == 1]),
            "2": len([i for i in items if i.get("level") == 2]),
            "3": len([i for i in items if i.get("level") == 3]),
            "4": len([i for i in items if i.get("level") == 4]),
            "5": len([i for i in items if i.get("level") == 5])
        },
        "categories": {}
    }
    
    for item in items:
        cat = item.get("category", "Sin categoría")
        stats["categories"][cat] = stats["categories"].get(cat, 0) + 1
    
    return jsonify(stats)

@app.route('/api/categories', methods=['GET'])
def get_categories():
    if not is_logged_in():
        return jsonify({"error": "No autorizado"}), 401
    
    items = []
    if os.path.exists(f"{DATA_DIR}/items.json"):
        with open(f"{DATA_DIR}/items.json", "r", encoding="utf-8") as f:
            items = json.load(f)
    
    categories = set()
    for item in items:
        cat = item.get("category", "")
        if cat:
            categories.add(cat)
    
    return jsonify(list(categories))

@app.route('/api/items', methods=['POST'])
def add_item():
    if not is_logged_in():
        return jsonify({"error": "No autorizado"}), 401
    
    data = request.json
    items = []
    if os.path.exists(f"{DATA_DIR}/items.json"):
        with open(f"{DATA_DIR}/items.json", "r", encoding="utf-8") as f:
            items = json.load(f)
    
    item = {
        "id": secrets.token_hex(16),
        "name": data.get("name", ""),
        "type": data.get("type", "text"),
        "content": data.get("content", ""),
        "category": data.get("category", ""),
        "tags": data.get("tags", []),
        "encrypted": False,
        "level": 0,
        "created": datetime.now().isoformat(),
        "modified": datetime.now().isoformat()
    }
    items.append(item)
    
    with open(f"{DATA_DIR}/items.json", "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    
    return jsonify({"success": True, "item": item})

@app.route('/api/items/<item_id>', methods=['PUT'])
def update_item(item_id):
    if not is_logged_in():
        return jsonify({"error": "No autorizado"}), 401
    
    data = request.json
    items = []
    if os.path.exists(f"{DATA_DIR}/items.json"):
        with open(f"{DATA_DIR}/items.json", "r", encoding="utf-8") as f:
            items = json.load(f)
    
    for item in items:
        if item["id"] == item_id:
            data["modified"] = datetime.now().isoformat()
            item.update(data)
            break
    
    with open(f"{DATA_DIR}/items.json", "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    
    return jsonify({"success": True})

@app.route('/api/items/<item_id>', methods=['GET'])
def get_item(item_id):
    if not is_logged_in():
        return jsonify({"error": "No autorizado"}), 401
    
    items = []
    if os.path.exists(f"{DATA_DIR}/items.json"):
        with open(f"{DATA_DIR}/items.json", "r", encoding="utf-8") as f:
            items = json.load(f)
    
    for item in items:
        if item["id"] == item_id:
            return jsonify(item)
    
    return jsonify({"error": "Item no encontrado"}), 404

@app.route('/api/items/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    if not is_logged_in():
        return jsonify({"error": "No autorizado"}), 401
    
    items = []
    if os.path.exists(f"{DATA_DIR}/items.json"):
        with open(f"{DATA_DIR}/items.json", "r", encoding="utf-8") as f:
            items = json.load(f)
    
    items = [item for item in items if item["id"] != item_id]
    
    with open(f"{DATA_DIR}/items.json", "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    
    return jsonify({"success": True})

@app.route('/api/encrypt', methods=['POST'])
def encrypt_item():
    if not is_logged_in():
        return jsonify({"error": "No autorizado"}), 401
    
    data = request.json
    item_id = data.get("item_id")
    password = data.get("password")
    level = int(data.get("level", 1))
    
    items = []
    if os.path.exists(f"{DATA_DIR}/items.json"):
        with open(f"{DATA_DIR}/items.json", "r", encoding="utf-8") as f:
            items = json.load(f)
    
    for item in items:
        if item["id"] == item_id:
            try:
                encrypted_content = EncryptionManager.encrypt(item["content"], password, level)
                item["content"] = encrypted_content
                item["encrypted"] = True
                item["level"] = level
                item["modified"] = datetime.now().isoformat()
                break
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 400
    
    with open(f"{DATA_DIR}/items.json", "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    
    return jsonify({"success": True})

@app.route('/api/decrypt', methods=['POST'])
def decrypt_item():
    if not is_logged_in():
        return jsonify({"error": "No autorizado"}), 401
    
    data = request.json
    item_id = data.get("item_id")
    password = data.get("password")
    
    items = []
    if os.path.exists(f"{DATA_DIR}/items.json"):
        with open(f"{DATA_DIR}/items.json", "r", encoding="utf-8") as f:
            items = json.load(f)
    
    for item in items:
        if item["id"] == item_id:
            try:
                decrypted_content = EncryptionManager.decrypt(item["content"], password, item["level"])
                item["content"] = decrypted_content
                item["encrypted"] = False
                item["level"] = 0
                item["modified"] = datetime.now().isoformat()
                break
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 400
    
    with open(f"{DATA_DIR}/items.json", "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    
    return jsonify({"success": True})

@app.route('/api/export', methods=['POST'])
def export_data():
    if not is_logged_in():
        return jsonify({"error": "No autorizado"}), 401
    
    data = request.json
    password = data.get("password")
    level = int(data.get("level", 5))
    format_type = data.get("format", "encript")
    
    items = []
    if os.path.exists(f"{DATA_DIR}/items.json"):
        with open(f"{DATA_DIR}/items.json", "r", encoding="utf-8") as f:
            items = json.load(f)
    
    if format_type == "encript":
        export_data = {
            "items": items,
            "version": get_current_version(),
            "exported_at": datetime.now().isoformat()
        }
        json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
        encrypted = EncryptionManager.encrypt(json_str, password, level)
        filename = f"{ENCRYPTED_DIR}/export_{secrets.token_hex(8)}.encript"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(encrypted)
        return send_file(filename, as_attachment=True, download_name="database.encript")
    elif format_type == "json":
        export_data = {
            "items": items,
            "version": get_current_version(),
            "exported_at": datetime.now().isoformat()
        }
        filename = f"{ENCRYPTED_DIR}/export_{secrets.token_hex(8)}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        return send_file(filename, as_attachment=True, download_name="database.json")
    elif format_type == "csv":
        import csv
        filename = f"{ENCRYPTED_DIR}/export_{secrets.token_hex(8)}.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Nombre", "Tipo", "Categoría", "Encriptado", "Nivel", "Creado", "Modificado"])
            for item in items:
                writer.writerow([
                    item.get("id", ""),
                    item.get("name", ""),
                    item.get("type", ""),
                    item.get("category", ""),
                    "Sí" if item.get("encrypted", False) else "No",
                    item.get("level", 0),
                    item.get("created", ""),
                    item.get("modified", "")
                ])
        return send_file(filename, as_attachment=True, download_name="database.csv")
    elif format_type == "txt":
        filename = f"{ENCRYPTED_DIR}/export_{secrets.token_hex(8)}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"SecureVault Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            for item in items:
                f.write(f"Nombre: {item.get('name', '')}\n")
                f.write(f"Tipo: {item.get('type', '')}\n")
                f.write(f"Categoría: {item.get('category', 'N/A')}\n")
                f.write(f"Encriptado: {'Sí' if item.get('encrypted', False) else 'No'}\n")
                if item.get('encrypted'):
                    f.write(f"Nivel: {item.get('level', 0)}\n")
                f.write(f"Contenido: {item.get('content', '')[:100]}...\n")
                f.write("-" * 60 + "\n\n")
        return send_file(filename, as_attachment=True, download_name="database.txt")
    
    return jsonify({"error": "Formato no válido"}), 400

@app.route('/api/import', methods=['POST'])
def import_data():
    if not is_logged_in():
        return jsonify({"error": "No autorizado"}), 401
    
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file provided"}), 400
    
    file = request.files['file']
    password = request.form.get("password")
    
    if file.filename == '':
        return jsonify({"success": False, "error": "No file selected"}), 400
    
    try:
        if file.filename.endswith('.encript'):
            encrypted_content = file.read().decode('utf-8')
            for level in range(5, 0, -1):
                try:
                    decrypted = EncryptionManager.decrypt(encrypted_content, password, level)
                    import_data = json.loads(decrypted)
                    items = import_data.get("items", [])
                    with open(f"{DATA_DIR}/items.json", "w", encoding="utf-8") as f:
                        json.dump(items, f, indent=2, ensure_ascii=False)
                    return jsonify({"success": True, "count": len(items)})
                except:
                    continue
            return jsonify({"success": False, "error": "Invalid password or file format"}), 400
        elif file.filename.endswith('.json'):
            import_data = json.loads(file.read().decode('utf-8'))
            items = import_data.get("items", [])
            with open(f"{DATA_DIR}/items.json", "w", encoding="utf-8") as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
            return jsonify({"success": True, "count": len(items)})
        else:
            return jsonify({"success": False, "error": "Formato de archivo no soportado"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if not is_logged_in():
        return jsonify({"error": "No autorizado"}), 401
    
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No file selected"}), 400
    
    file_content = file.read()
    file_b64 = base64.b64encode(file_content).decode()
    
    items = []
    if os.path.exists(f"{DATA_DIR}/items.json"):
        with open(f"{DATA_DIR}/items.json", "r", encoding="utf-8") as f:
            items = json.load(f)
    
    item = {
        "id": secrets.token_hex(16),
        "name": file.filename,
        "type": "file",
        "content": file_b64,
        "category": request.form.get("category", ""),
        "tags": [],
        "encrypted": False,
        "level": 0,
        "created": datetime.now().isoformat(),
        "modified": datetime.now().isoformat()
    }
    items.append(item)
    
    with open(f"{DATA_DIR}/items.json", "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    
    return jsonify({"success": True, "item": item})

@app.route('/api/download/<item_id>', methods=['GET'])
def download_file(item_id):
    if not is_logged_in():
        return jsonify({"error": "No autorizado"}), 401
    
    items = []
    if os.path.exists(f"{DATA_DIR}/items.json"):
        with open(f"{DATA_DIR}/items.json", "r", encoding="utf-8") as f:
            items = json.load(f)
    
    for item in items:
        if item["id"] == item_id:
            file_content = base64.b64decode(item["content"])
            filename = item["name"]
            
            temp_file = f"{ENCRYPTED_DIR}/temp_{secrets.token_hex(8)}"
            with open(temp_file, "wb") as f:
                f.write(file_content)
            
            return send_file(temp_file, as_attachment=True, download_name=filename)
    
    return jsonify({"success": False, "error": "File not found"}), 404

@app.route('/installer')
def installer():
    return render_template('installer.html')

@app.route('/api/install-path', methods=['GET'])
def get_install_path():
    install_path = Path.home() / "Documents" / APP_NAME
    return jsonify({"path": str(install_path)})

@app.route('/api/install', methods=['POST'])
def install():
    try:
        import shutil
        current_dir = Path(__file__).parent
        install_path = Path.home() / "Documents" / APP_NAME
        install_path.mkdir(parents=True, exist_ok=True)
        
        files_to_copy = ["app.py", "requirements.txt", "version.txt"]
        dirs_to_copy = ["templates"]
        
        for file_name in files_to_copy:
            src_file = current_dir / file_name
            if src_file.exists():
                dst_file = install_path / file_name
                shutil.copy2(src_file, dst_file)
        
        for dir_name in dirs_to_copy:
            src_dir = current_dir / dir_name
            if src_dir.exists() and src_dir.is_dir():
                dst_dir = install_path / dir_name
                if dst_dir.exists():
                    shutil.rmtree(dst_dir)
                shutil.copytree(src_dir, dst_dir)
        
        config_file = install_path / "config.json"
        config = {
            "installed": True,
            "version": get_current_version(),
            "install_path": str(install_path)
        }
        
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        return jsonify({"success": True, "path": str(install_path)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    config_file = Path("config.json")
    is_first_run = not config_file.exists()
    
    if is_first_run:
        print(f"\n{'='*60}")
        print(f"  Bienvenido a {APP_NAME} v{get_current_version()}")
        print(f"{'='*60}\n")
        print("Primera ejecución detectada.")
        print("Abre http://localhost:5000/installer en tu navegador para completar la instalación.\n")
    
    update_info = check_updates()
    if update_info["update_available"]:
        print(f"⚠ Actualización disponible: v{update_info['latest']}")
        print(f"  Versión actual: v{update_info['current']}\n")
    
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)

