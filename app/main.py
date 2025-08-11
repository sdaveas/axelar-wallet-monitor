from health import start_health_check_service
from monitor import monitor_loop

import threading

if __name__ == "__main__":
    threading.Thread(target=start_health_check_service, daemon=True).start()
    monitor_loop()