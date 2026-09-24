# Histórico de versões

## v0.0.2 — correção de compatibilidade Linux (em preparação)

- Renderização por software habilitada por padrão no Linux para contornar falhas GLX.
- Aceleração de hardware disponível opcionalmente com `DFD_HARDWARE_ACCELERATION=1`.
- Pacote Linux em ZIP com executável e arquivos necessários, como no Windows.
- Diagnóstico de inicialização gráfica em CI utilizando Xvfb.

## v0.0.1 — versão experimental

- Editor DFD com Vela Framework, JSON, SVG e HTML.
- Modelo de atividade do módulo 01.
- Compilação Windows Qt5 e Linux x86_64 PyQt6/QtWebEngine.
- Automação de releases por tag v* com verificações SHA-256.
