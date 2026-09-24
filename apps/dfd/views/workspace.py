from vela.template_engine.engine import render_template

def workspace_view(params: dict) -> str:
    return render_template('apps/dfd/templates/dfd/index.html',
                           context={'app_name': 'DFD Studio'}, router=params['router'])
