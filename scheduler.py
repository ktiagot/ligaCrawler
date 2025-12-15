import schedule
import time
from liga_scraper import main as run_scraper
from datetime import datetime

def job():
    """Executa o scraper e registra o horário"""
    print(f"\n{'='*50}")
    print(f"Executando scraper em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{'='*50}")
    
    try:
        run_scraper()
        print("Scraper executado com sucesso!")
    except Exception as e:
        print(f"Erro ao executar scraper: {e}")

# Agenda para executar a cada 6 horas
schedule.every(6).hours.do(job)

print("Agendador iniciado. O scraper será executado diariamente às 9:00")
print("Pressione Ctrl+C para parar")

# Executa uma vez imediatamente para teste
print("Executando primeira vez para teste...")
job()

# Loop principal do agendador
try:
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verifica a cada minuto
except KeyboardInterrupt:
    print("\nAgendador interrompido pelo usuário")