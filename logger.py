import datetime

def log_message(message: str, severity: int, error = None):
    """Prints a string with a standard timestamp and severity
    indicator attached. Severity levels are as follow:
    1 - Critical: Indicates an irrecoverable exception
    2 - Error: Indicates a recoverable exception
    3 - Warning: Indicates a potential problem
    4 - Informative: Indicates a normal message
    Optionally it'll also take an exception and print it"""
    match severity:
        case 1: sev_text = 'CRIT'
        case 2: sev_text = 'ERR '
        case 3: sev_text = 'WARN'
        case 4: sev_text = 'INFO'
        case _: raise ValueError(f'Unknown severity level {severity}')
    if error:
        print(f'{datetime.datetime.now().isoformat}: [{sev_text}] {message} {str(error.__class__)}: {str(error)}')
    else:
        print(f'{datetime.datetime.now().isoformat}: [{sev_text}] {message}')
