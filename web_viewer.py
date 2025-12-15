from flask import Flask, render_template, jsonify
import json
import os
import glob
from datetime import datetime
import pandas as pd

app = Flask(__name__)

def load_all_data():
    """Carrega todos os arquivos JSON da pasta data"""
    data_files = glob.glob('data/liga_precos_*.json')
    all_data = []
    
    for file_path in sorted(data_files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                timestamp = os.path.basename(file_path).replace('liga_precos_', '').replace('.json', '')
                
                for marca, products in data.items():
                    for product in products:
                        product['marca'] = marca
                        product['file_timestamp'] = timestamp
                        all_data.append(product)
        except Exception as e:
            print(f"Erro ao carregar {file_path}: {e}")
    
    return all_data

def get_price_history():
    """Gera histórico de preços por produto"""
    all_data = load_all_data()
    history = {}
    for item in all_data:
        name = item['name']
        if name not in history:
            history[name] = []
        # Corrige o formato do preço para float
        preco_str = str(item['price']) if item['price'] else '0'
        preco_str = preco_str.replace('.', '').replace(',', '.')
        try:
            preco_float = float(preco_str)
        except Exception:
            preco_float = 0
        # Só adiciona se o preço for maior que zero
        if preco_float > 0:
            history[name].append({
                'date': item['scraped_at'],
                'price': preco_float,
                'marca': item['marca']
            })
    # Remove produtos sem histórico de preço
    history = {k: v for k, v in history.items() if v}
    # Ordena por data
    for name in history:
        history[name] = sorted(history[name], key=lambda x: x['date'])
    return history

@app.route('/')
def index():
    """Página principal com lista de produtos"""
    all_data = load_all_data()
    
    # Pega apenas os dados mais recentes de cada produto
    latest_data = {}
    for item in all_data:
        name = item['name']
        if name not in latest_data or item['scraped_at'] > latest_data[name]['scraped_at']:
            latest_data[name] = item
    
    products = list(latest_data.values())
    products.sort(key=lambda x: x['name'])
    
    return render_template('index.html', products=products)

@app.route('/history/<product_name>')
def product_history(product_name):
    """Histórico de preços de um produto específico"""
    history = get_price_history()
    product_history = history.get(product_name, [])
    
    return jsonify(product_history)

@app.route('/api/products')
def api_products():
    """API com todos os produtos"""
    all_data = load_all_data()
    return jsonify(all_data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)