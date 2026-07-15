import time
from typing import Callable
from logger_core import log

# En Fase 3 usamos un Dispatcher nativo que en Fase 5 se convertirá en Celery + Redis
# Esto garantiza que el sistema funcione AHORA sin fricción y 100% gratuito.

class WorkerDispatcher:
    def __init__(self):
        self.tasks = {}

    def register_task(self, task_name: str, func: Callable):
        self.tasks[task_name] = func
        log.info(f"Tarea registrada en Worker: {task_name}")

    def dispatch(self, task_name: str, *args, **kwargs):
        if task_name not in self.tasks:
            log.error(f"Intento de dispatch a tarea no registrada: {task_name}")
            return False
        
        # Simulación de encolamiento (Acá irá la inyección de Celery en Fase 5)
        log.info(f"Dispatch asíncrono disparado: {task_name}")
        try:
            # En modo "standalone" se ejecuta directo. 
            # En producción se enviará a background tasks o thread_pool
            result = self.tasks[task_name](*args, **kwargs)
            log.info(f"Tarea completada: {task_name}")
            return result
        except Exception as e:
            log.error(f"Fallo en ejecución de Tarea {task_name}: {e}")
            return None

# Instancia global del worker
worker = WorkerDispatcher()

# -- REGISTRO DE ROBOTS ACTUALES --
# Aquí migraremos la lógica de robot_gestion_llamadas.py y robot_productividad.py

def robot_sincronizacion_maestra_ejemplo():
    log.info("[ROBOT] Iniciando sincronización...")
    time.sleep(2)
    log.info("[ROBOT] Sincronización Finalizada.")
    return True

worker.register_task("sync_maestra", robot_sincronizacion_maestra_ejemplo)

if __name__ == "__main__":
    log.info("Iniciando Worker Daemon...")
    worker.dispatch("sync_maestra")
