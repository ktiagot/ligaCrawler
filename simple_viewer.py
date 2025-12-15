import json
import os
import glob
from datetime import datetime
import webbrowser

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

def generate_html():
    """Gera arquivo HTML estático"""
    all_data = load_all_data()
    
    # Pega apenas os dados mais recentes de cada produto
    latest_data = {}
    for item in all_data:
        name = item['name']
        if name not in latest_data or item['scraped_at'] > latest_data[name]['scraped_at']:
            latest_data[name] = item
    
    products = list(latest_data.values())
    products.sort(key=lambda x: x['name'])
    
    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Liga SWU - Monitor de Preços</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .products { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        .product { background: #fff; border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .product img { width: 100%; max-width: 150px; height: auto; border-radius: 4px; }
        .product h3 { margin: 10px 0; font-size: 14px; }
        .price { font-size: 18px; font-weight: bold; color: #e74c3c; }

        .search { margin-bottom: 20px; }
        .search input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Liga SWU - Monitor de Preços</h1>
            <p>Total de produtos: """ + str(len(products)) + """</p>
            <p>Última atualização: """ + datetime.now().strftime('%d/%m/%Y %H:%M:%S') + """</p>
            <div class="search">
                <input type="text" id="searchInput" placeholder="Buscar produtos..." onkeyup="filterProducts()">
            </div>
        </div>

        <div class="products" id="productsContainer">"""
    
    for product in products:
        html += f"""
            <div class="product" data-name="{product['name'].lower()}">
                <img src="{product['image']}" alt="{product['name']}" onerror="this.style.display='none'">
                <h3>{product['name']}</h3>
                <div class="price">R$ {product['price']}</div>

                <a href="{product['link']}" target="_blank" style="display: block; margin-top: 10px; color: #3498db;">Ver no site</a>
            </div>"""
    
    html += """
        </div>
    </div>

    <script>
        function filterProducts() {
            const input = document.getElementById('searchInput');
            const filter = input.value.toLowerCase();
            const products = document.querySelectorAll('.product');
            
            products.forEach(product => {
                const name = product.getAttribute('data-name');
                if (name.includes(filter)) {
                    product.style.display = 'block';
                } else {
                    product.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>"""
    
    with open('produtos.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("Arquivo produtos.html gerado com sucesso!")
    return 'produtos.html'

if __name__ == '__main__':
    html_file = generate_html()
    webbrowser.open(f'file://{os.path.abspath(html_file)}')