from apscheduler.schedulers.background import BackgroundScheduler
from database import SessionLocal
from crud import atualizar_cache

def iniciar_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: atualizar_cache(SessionLocal()),
        'interval',
        hours=24,
        id='atualizacao_diaria'
    )
    scheduler.start()
    print("Scheduler iniciado. Atualização automática a cada 24 horas.")