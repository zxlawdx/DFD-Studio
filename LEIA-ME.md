# DFD Studio — Vela Edition

Editor desktop visual de **Diagrama de Fluxo de Dados**, com Python (Vela Framework) e SVG/HTML/CSS/JS puros. Esta edição é a continuação do DFD Studio Tkinter e **abre os projetos `.dfd.json` do programa anterior sem conversão**.

## O que foi implementado

- Interface escura de identidade própria inspirada no layout de referência: azul profundo, ciano, verde, grade, biblioteca lateral, inspector de propriedades, camadas e minimapa.
- Arrastar elementos com mouse, redimensionar pela alça no canto inferior direito; posicionamento com encaixe em grade (mantenha **Alt** para movimento livre).
- Criar processos, entidades externas, depósitos e notas por clique ou arrastando da biblioteca para o canvas.
- Desenhar ligações: tecle **C**, clique na origem e depois no destino. Alternativamente, com um nó selecionado, clique na pequena alça circular da face desejada e escolha o destino.
- Editar rótulos das setas, código, texto, cor, dimensões, portas e rota, além de detalhamento para impressão.
- Zoom da roda do mouse, pan segurando e arrastando o fundo, botão Enquadrar e minimapa.
- Desfazer/refazer, excluir, importação/exportação de JSON e recuperação automática de rascunho no navegador embutido.
- Salvar projetos localmente pelo backend, exportar SVG vetorial e HTML independente; ambos também ficam em `Documentos/DFD Studio/exportacoes`.
- Inclui atividade 06 já preenchida, com **1.8 → 1.11**, **1.13 → 1.04**, verificação de antecipação **1.15** e cálculo de desconto **1.16**; a taxa de desconto continua indefinida, pois depende das regras do exercício.
- Workflow GitHub Actions que valida Python/JS e gera pacote `.zip` com **`.exe` Windows** (diretório completo, não um executável solto).

## Instalar no Linux Mint

A instalação do GTK do pywebview usa pacotes do sistema. Em Debian/Ubuntu/Mint:

```bash
sudo apt update
sudo apt install -y python3-venv python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.1 \
   libgirepository-2.0-dev libcairo2-dev pkg-config python3-dev
bash INICIAR_LINUX.sh
```

Ou manualmente, usando `python3 -m venv .venv --system-site-packages`, `pip install -r requirements.txt`, `python manage.py collectstatic --no-tailwind`, `python manage.py runapp`.

## Instalar no Windows em modo desenvolvimento

Instale Python 3.13 e Git. Execute `INICIAR_WINDOWS.bat` (ou os comandos equivalentes em terminal). O executável gerado pelas Actions já inclui runtime Python e Qt, mas você precisa extrair **toda a pasta** do ZIP.

## Gerar o executável usando GitHub Actions

1. Crie um repositório vazio no GitHub e envie **o conteúdo desta pasta**, incluindo `.github/workflows/build.yml`.
2. Na aba **Actions**, abra **Testes e executavel DFD Studio** e pressione **Run workflow**; também será disparado a cada push na branch `main` ou `master`.
3. Após a conclusão, baixe o artefato **DFD-Studio-Windows**, extraia os dois ZIPs quando necessário e execute `DFD-Studio.exe` dentro da pasta resultante.

**Importante:** o workflow está implementado, mas não foi executado em runner Windows neste ambiente. Erros de empacotamento específicos do Vela/Qt só poderão ser confirmados em um runner real.

## Estrutura

```text
DFD_Studio_Vela/
├── manage.py, launcher.py, config/
├── apps/dfd/
│   ├── views/, urls.py, api.py
│   ├── services/diagram_service.py
│   ├── repositories/project_repository.py
│   ├── templates/dfd/index.html
│   └── static/dfd/{css,js}/
├── model.py, exporter.py, example.py  # motor herdado, compatível com Tkinter
├── assets/                            # exemplo e exportação original de entrega
├── .github/workflows/build.yml
└── tests/
```

### Formato entregue ao professor

**Recomendado:** exporte em **HTML** e abra em Firefox/Chrome para conferir todas as informações. A página HTML é independente, abre sem internet e tem um botão **Imprimir / salvar em PDF**. Exporte também em **SVG** para inserir o diagrama em apresentações e **JSON** como fonte editável do projeto.

### Fluxo de dados vs. fluxograma

Este é um editor DFD: as setas representam **dados**, não a ordem temporal das ações. Confira com o professor os rótulos e regras de desconto. Não foi inventada uma taxa de antecipação.

### Testes

```bash
python -m unittest discover -s tests -v
node --check apps/dfd/static/js/app.js
```

### Limitações desta edição

As conexões criadas em modo visual são automáticas (linha direta ou ortogonal com portas selecionáveis); o modelo v1 já suporta `bends`, mas o editor visual ainda não oferece uma alça para desenhar manualmente curvas ortogonais complexas. O frontend preserva os pontos `bends` existentes. A geração do EXE e a execução da GUI não puderam ser verificadas localmente sem o Vela instalado; o motor JSON/SVG/HTML foi coberto por testes.

O app é local. A API é ligada a `127.0.0.1`, e os dados ficam no computador do usuário.


## Build Linux PyQt6 e releases versionadas

A partir da v0.0.1, o build Linux usa **PyQt6/QtWebEngine**, enquanto
Windows continua usando Qt5. O arquivo
[README.md](README.md) descreve a execução local Qt6, o fluxo de tags
e a publicação dos executáveis e checksums SHA-256 por GitHub Actions.


## Modo de compatibilidade para GLX/OpenGL (Linux)

O DFD Studio Linux pode apresentar `Could not initialize GLX` ao usar
Qt6 em sistemas com drivers de GPU/X11 incompatíveis. A partir da v0.0.2,
o executável inicia com renderização por software. Para testar o hardware:

```bash
DFD_HARDWARE_ACCELERATION=1 ./DFD-Studio
```

O arquivo de distribuição Linux mudou de TAR.GZ para ZIP por conveniência;
essa mudança **não altera o binário** dentro do pacote. Uma versão
publicada v0.0.1 permanece inalterada na seção Releases.
