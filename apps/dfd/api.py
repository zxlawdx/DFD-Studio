"""REST do projeto. API somente em 127.0.0.1, não há acesso remoto configurado."""
from vela.api import api
from apps.dfd.services.diagram_service import DiagramService

service = DiagramService()

def payload(context):
    obj = (context or {}).get('json') or {}
    if not isinstance(obj, dict):
        raise ValueError('Payload JSON deve ser um objeto.')
    return obj

def result(fn):
    try:
        return {'ok': True, 'result': fn()}
    except (ValueError, KeyError, TypeError) as err:
        return {'ok': False, 'error': str(err)}
    except Exception:
        # Evita expor paths/tracebacks em respostas da API.
        return {'ok': False, 'error': 'Erro interno. Consulte o terminal para detalhes.'}

@api.get('/dfd/example')
def example(context=None):
    return result(service.example)

@api.get('/dfd/projects')
def projects(context=None):
    return result(service.list_projects)

@api.post('/dfd/projects/load')
def load(context=None):
    return result(lambda: service.load(payload(context)['name']))

@api.post('/dfd/projects/save')
def save(context=None):
    return result(lambda: service.save(payload(context)['name'], payload(context)['diagram']))

@api.post('/dfd/export')
def export(context=None):
    data = payload(context)
    return result(lambda: service.export(data.get('name','diagrama'),data['type'],data['diagram']))
