LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s -> %(levelname)s -> %(module)s -> %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': 'app.log',
            'level': 'DEBUG'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        },
        'app.database': {
            'level': 'DEBUG',
        },
        'app.service': {
            'level': 'INFO'
        },
        'app.service.CaseRepository':{
            'level': 'DEBUG'
        },
        '__main__': {
            'level': 'DEBUG'
        }
    }
}
