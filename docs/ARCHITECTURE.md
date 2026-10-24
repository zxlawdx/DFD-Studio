# DFD Studio architecture

DFD Studio intentionally uses the reduced Vela application structure.

```text
Vela / UI
   |
api.py / bridge.py / views
   |
application/diagram_service.py
   |
domain/diagram.py + domain/ports.py
   |
infrastructure/persistence/project_repository.py
```

## Composition root

`config/wsgi.py` creates the Vela runtime. `apps/dfd/app.py` owns application construction and the explicit app metadata.

The current Vela release still requires API decorator modules to be imported for registration. This is isolated in `register_presentation()` rather than being an unexplained top-level import in `wsgi.py`.

## Compatibility imports

`model.py`, `apps/dfd/services/diagram_service.py`, and `apps/dfd/repositories/project_repository.py` remain as shims so old imports and the exporter continue to work. New code should use `domain/`, `application/`, and `infrastructure/`.

## Boundaries

- Domain imports no Vela/Bottle/WebView.
- Application coordinates use cases and depends on domain contracts.
- Infrastructure owns filesystem persistence.
- Presentation validates input and delegates.

The project deliberately does not add CQRS, DI containers or empty layer directories.
