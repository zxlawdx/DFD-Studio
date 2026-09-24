# DFD Studio — v0.0.2 (em preparação)

Editor de Diagramas de Fluxo de Dados com **Python + Vela Framework**,
JavaScript e SVG. Salve diagramas em JSON e exporte HTML ou SVG.

## Executáveis

A aba **Releases** disponibiliza dois builds nativos:

- **Linux x86_64: PyQt6 + QtWebEngine**, gerado no Ubuntu 22.04;
  formato `DFD-Studio-Linux-x86_64-v0.0.2.zip` (**ZIP contendo pasta executável**).
- **Windows x86_64: Qt5 + QtWebEngine**, pacote ZIP.
- Cada arquivo vem acompanhado de um checksum SHA-256.

Extraia **a pasta inteira**, não só o executável. No Linux,
bibliotecas gráficas nativas compatíveis ainda são necessárias.

## Problemas gráficos no Linux

Em computadores sem uma configuração GLX/OpenGL compatível com o Qt6
(por exemplo, em determinados sistemas com drivers híbridos), a versão
v0.0.1 pode fechar com `Could not initialize GLX`.

**Solução imediata para o binário v0.0.1**, dentro da pasta extraída:

```bash
QT_XCB_GL_INTEGRATION=none \
QT_QUICK_BACKEND=software \
LIBGL_ALWAYS_SOFTWARE=1 \
QTWEBENGINE_CHROMIUM_FLAGS=--disable-gpu \
./DFD-Studio
```

A partir de **v0.0.2**, o binário Linux habilita esse modo de
compatibilidade automaticamente. Se sua GPU tiver aceleração GLX funcional,
use `DFD_HARDWARE_ACCELERATION=1 ./DFD-Studio` para tentar utilizar
a aceleração gráfica.

Avisos `xapp-gtk3-module` e `gvfs` são separados do erro GLX; a
presença deles não significa, isoladamente, que a interface irá falhar.
Se continuar fechando, inspecione drivers e execute `glxinfo -B`.

## Desenvolvimento local

```bash
git clone https://github.com/zxlawdx/DFD-Studio.git
cd DFD-Studio
# Linux com PyQt6, usando venv separado:
bash INICIAR_LINUX_QT6.sh
# Alternativa Linux com GTK:
bash INICIAR_LINUX.sh
# Testes portáveis:
python -m unittest discover -s tests -v
```

Instale primeiro python3-venv e bibliotecas Qt do sistema
(libxcb-cursor0, libxkbcommon-x11-0, libnss3, libgbm1, libegl1).
No Windows, use INICIAR_WINDOWS.bat.

## Tags e releases

O GitHub Actions testa o projeto e compila Windows/Linux em cada push
na main. Os artefatos desses pushes são builds de CI, não releases.

**Publicação de correções, começando por v0.0.2:** abra a aba **Actions**, escolha
**DFD Studio - CI e releases**, selecione a branch **main**, execute
**Run workflow** com a entrada `tag=v0.0.2`. Após testes e builds
aprovados, a Action cria a tag e publica ambos os pacotes e seus hashes.

Alternativamente, crie a tag a partir do commit da main:

```bash
git checkout main
git pull --ff-only
git tag -a v0.0.2 -m "DFD Studio v0.0.2"
git push origin v0.0.2
```

Em próximas versões, atualize VERSION e CHANGELOG.md antes de criar
a tag. **Não mova uma tag publicada:** faça uma versão seguinte.
Documentação funcional: [LEIA-ME.md](LEIA-ME.md).
