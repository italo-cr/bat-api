# Exemplo de API simples com Flask para receber dados do questionário BAT
# Execute este código em um servidor ou use serviços como Railway, Render, etc.

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Permite requisições do Colab

# Configuração do banco de dados SQLite
DATABASE = 'bat_responses.db'

def init_db():
    """Inicializa o banco de dados"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bat_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            participante_id TEXT,
            timestamp TEXT,
            respostas TEXT,
            scores TEXT,
            total_questoes INTEGER,
            versao_questionario TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/api/bat-responses', methods=['POST'])
def salvar_resposta():
    """Endpoint para salvar respostas do questionário BAT"""
    try:
        dados = request.get_json()
        
        # Validação básica
        if not dados:
            return jsonify({"erro": "Dados não fornecidos"}), 400
        
        # Extrai dados
        participante_id = dados.get('participante_id', 'anonimo')
        timestamp = dados.get('timestamp')
        respostas = dados.get('respostas', [])
        scores = dados.get('scores_por_categoria', {})
        total_questoes = dados.get('total_questoes', 0)
        versao = dados.get('versao_questionario', 'BAT-v1.0')
        
        # Salva no banco
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bat_responses 
            (participante_id, timestamp, respostas, scores, total_questoes, versao_questionario)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            participante_id,
            timestamp,
            json.dumps(respostas, ensure_ascii=False),
            json.dumps(scores, ensure_ascii=False),
            total_questoes,
            versao
        ))
        
        response_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            "sucesso": True,
            "mensagem": "Respostas salvas com sucesso",
            "id": response_id,
            "timestamp": datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({
            "erro": f"Erro interno do servidor: {str(e)}"
        }), 500

@app.route('/api/bat-responses', methods=['GET'])
def listar_respostas():
    """Lista todas as respostas (para análise)"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, participante_id, timestamp, scores, total_questoes, 
                   versao_questionario, created_at
            FROM bat_responses 
            ORDER BY created_at DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        respostas = []
        for row in results:
            respostas.append({
                "id": row[0],
                "participante_id": row[1],
                "timestamp": row[2],
                "scores": json.loads(row[3]),
                "total_questoes": row[4],
                "versao_questionario": row[5],
                "created_at": row[6]
            })
        
        return jsonify({
            "total": len(respostas),
            "respostas": respostas
        })
        
    except Exception as e:
        return jsonify({
            "erro": f"Erro ao buscar respostas: {str(e)}"
        }), 500

@app.route('/api/bat-responses/<int:response_id>', methods=['GET'])
def obter_resposta_detalhada(response_id):
    """Obtém uma resposta específica com todos os detalhes"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM bat_responses WHERE id = ?
        ''', (response_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return jsonify({"erro": "Resposta não encontrada"}), 404
        
        resposta_completa = {
            "id": result[0],
            "participante_id": result[1],
            "timestamp": result[2],
            "respostas": json.loads(result[3]),
            "scores": json.loads(result[4]),
            "total_questoes": result[5],
            "versao_questionario": result[6],
            "created_at": result[7]
        }
        
        return jsonify(resposta_completa)
        
    except Exception as e:
        return jsonify({
            "erro": f"Erro ao buscar resposta: {str(e)}"
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde da API"""
    return jsonify({
        "status": "ativo",
        "timestamp": datetime.now().isoformat(),
        "versao": "1.0"
    })

@app.route('/', methods=['GET'])
def index():
    """Página inicial da API"""
    return jsonify({
        "mensagem": "API do Questionário BAT",
        "endpoints": {
            "POST /api/bat-responses": "Salvar respostas",
            "GET /api/bat-responses": "Listar respostas",
            "GET /api/bat-responses/<id>": "Obter resposta específica",
            "GET /api/health": "Verificação de saúde"
        }
    })

if __name__ == '__main__':
    # Inicializa o banco de dados
    init_db()
    
    # Configurações para desenvolvimento/produção
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Iniciando API BAT na porta {port}")
    print("📍 Endpoints disponíveis:")
    print("  POST /api/bat-responses - Salvar respostas")
    print("  GET  /api/bat-responses - Listar respostas")
    print("  GET  /api/health - Status da API")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

# ===== INSTRUÇÕES DE DEPLOY =====
"""
🚀 COMO FAZER DEPLOY:

1. RAILWAY (Recomendado):
   - Vá em railway.app
   - Conecte seu GitHub
   - Faça deploy deste código
   - Use a URL gerada no Colab

2. RENDER:
   - Vá em render.com
   - Conecte GitHub
   - Deploy como Web Service
   - Use a URL gerada

3. HEROKU:
   - Instale heroku CLI
   - heroku create seu-app-bat
   - git push heroku main

4. GOOGLE CLOUD RUN:
   - Use o Dockerfile abaixo
   - Deploy no Cloud Run

DOCKERFILE:
```
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD gunicorn --bind 0.0.0.0:8080 app:app
```

REQUIREMENTS.TXT:
```
Flask==2.3.3
Flask-CORS==4.0.0
gunicorn==21.2.0
```
"""
