import requests
from bs4 import BeautifulSoup
import time
import random
import json
from datetime import datetime
import csv
import os

class LigaScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(self.headers)
        
        # URLs das marcas
        self.urls = {
            'marca_79': 'https://www.ligaswu.com.br/?view=cards%2Fsearch&card=marca%3D79+searchprod%3D1&tipo=1',
            'marca_2': 'https://www.ligaswu.com.br/?view=cards%2Fsearch&card=marca%3D2+searchprod%3D1&tipo=1',
            'marca_4': 'https://www.ligaswu.com.br/?view=cards%2Fsearch&card=marca%3D4+searchprod%3D1&tipo=1',
            'marca_9': 'https://www.ligaswu.com.br/?view=cards%2Fsearch&card=marca%3D9+searchprod%3D1&tipo=1',
            'marca_11': 'https://www.ligaswu.com.br/?view=cards%2Fsearch&card=marca%3D11+searchprod%3D1&tipo=1'
        }
        
    def random_delay(self, min_seconds=1, max_seconds=3):
        """Adiciona delay aleatório entre requisições"""
        time.sleep(random.uniform(min_seconds, max_seconds))
        
    def get_page(self, url, retries=3):
        """Faz requisição com retry e tratamento de erro"""
        for attempt in range(retries):
            try:
                self.random_delay()
                # Headers sem compressão
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
                response = requests.get(url, timeout=10, headers=headers)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                print(f"Erro na tentativa {attempt + 1}: {e}")
                if attempt == retries - 1:
                    return None
                time.sleep(5)
        return None
    
    def debug_html(self, html_content, filename="debug.html"):
        """Salva HTML para debug"""
        os.makedirs('data', exist_ok=True)
        filename = f"data/{filename}"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML salvo em {filename} para análise")
    
    def extract_products(self, html_content):
        """Extrai informações dos produtos da página"""
        soup = BeautifulSoup(html_content, 'html.parser')
        products = []
        
        # Debug: salva HTML atual
        self.debug_html(html_content)
        
        # Tenta vários seletores para encontrar produtos
        selectors = [
            'div.categoria div.card',
            '.categoria .card', 
            'div.card',
            '.card'
        ]
        
        product_cards = []
        for selector in selectors:
            cards = soup.select(selector)
            if cards:
                # Filtra apenas cards que têm título de produto
                valid_cards = []
                for card in cards:
                    if card.select_one('h5.card-title a') or card.select_one('.card-title'):
                        valid_cards.append(card)
                
                if valid_cards:
                    product_cards = valid_cards
                    print(f"Encontrados {len(product_cards)} produtos com seletor: {selector}")
                    break
        
        if not product_cards:
            print("Nenhum produto encontrado. Verificando estrutura...")
            # Debug: mostra algumas classes encontradas
            all_divs = soup.find_all('div', class_=True)
            classes = set()
            for div in all_divs[:20]:
                classes.update(div.get('class', []))
            print(f"Classes encontradas: {sorted(list(classes))[:10]}")
            
        for card in product_cards:
            try:
                product = self.parse_product_card(card)
                if product:
                    products.append(product)
            except Exception as e:
                print(f"Erro ao processar produto: {e}")
                continue
                
        return products
    
    def parse_product_card(self, card):
        """Extrai dados de um card de produto"""
        import re
        
        # Nome do produto - busca no h5.card-title
        name_element = card.select_one('h5.card-title a')
        if not name_element:
            return None
        name = name_element.get_text(strip=True)
        
        # Preço - busca na classe .smallest-price
        price = None
        price_element = card.select_one('.smallest-price')
        if price_element:
            price_text = price_element.get_text(strip=True)
            # Remove R$ e espaços, extrai apenas números
            price_match = re.search(r'([\d,\.]+)', price_text.replace('R$', '').strip())
            if price_match:
                price = price_match.group(1).replace(',', '.')
        
        # Link do produto
        link = None
        link_element = card.select_one('h5.card-title a')
        if link_element:
            link = link_element.get('href')
            if link and not link.startswith('http'):
                link = 'https://www.ligaswu.com.br' + link
        
        # Imagem do produto
        img = None
        img_element = card.select_one('img.lazy')
        if img_element:
            img = img_element.get('data-src') or img_element.get('src')
            if img and img.startswith('//'):
                img = 'https:' + img
            elif img and not img.startswith('http'):
                img = 'https://www.ligaswu.com.br' + img
        
        return {
            'name': name,
            'price': price,
            'link': link,
            'image': img,
            'scraped_at': datetime.now().isoformat()
        }
    
    def scrape_marca(self, marca_key):
        """Scraping de uma marca específica com paginação"""
        base_url = self.urls[marca_key]
        print(f"Fazendo scraping da {marca_key}...")
        
        all_products = []
        page = 0
        
        while True:
            # Adiciona parâmetro de página
            url = f"{base_url}&page={page}" if page > 0 else base_url
            
            response = self.get_page(url)
            if not response:
                print(f"Falha ao acessar {marca_key} página {page}")
                break
                
            products = self.extract_products(response.text)
            
            if not products:
                print(f"Nenhum produto encontrado na página {page}, finalizando")
                break
                
            all_products.extend(products)
            print(f"Página {page}: {len(products)} produtos (total: {len(all_products)})")
            
            # Verifica se há botão "Exibir mais" ou próxima página
            soup = BeautifulSoup(response.text, 'html.parser')
            next_button = soup.select_one('#exibir_mais_cards input, .exibir-mais')
            
            if not next_button or len(products) < 40:
                print(f"Fim da paginação detectado")
                break
                
            page += 1
            
            # Limite de segurança
            if page > 10:
                print("Limite de páginas atingido")
                break
        
        print(f"Total encontrado para {marca_key}: {len(all_products)} produtos")
        return all_products
    
    def scrape_all(self):
        """Faz scraping de todas as marcas"""
        all_products = {}
        
        for marca_key in self.urls.keys():
            products = self.scrape_marca(marca_key)
            all_products[marca_key] = products
            
        return all_products
    
    def save_to_json(self, data, filename=None):
        """Salva dados em JSON"""
        os.makedirs('data', exist_ok=True)
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/liga_precos_{timestamp}.json"
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Dados salvos em {filename}")
        
    def save_to_csv(self, data, filename=None):
        """Salva dados em CSV"""
        os.makedirs('data', exist_ok=True)
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/liga_precos_{timestamp}.csv"
            
        all_products = []
        for marca, products in data.items():
            for product in products:
                product['marca'] = marca
                all_products.append(product)
                
        if all_products:
            fieldnames = ['marca', 'name', 'price', 'link', 'image', 'scraped_at']
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_products)
            print(f"Dados salvos em {filename}")

def main():
    scraper = LigaScraper()
    
    print("Iniciando scraping do Liga SWU...")
    data = scraper.scrape_all()
    
    # Salva em ambos os formatos
    scraper.save_to_json(data)
    scraper.save_to_csv(data)
    
    # Mostra resumo
    total_products = sum(len(products) for products in data.values())
    print(f"\nResumo:")
    print(f"Total de produtos encontrados: {total_products}")
    for marca, products in data.items():
        print(f"  {marca}: {len(products)} produtos")

if __name__ == "__main__":
    main()