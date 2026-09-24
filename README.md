# DFD Studio — v0.0.1

Editor de Diagramas de Fluxo de Dados com **Python + Vela Framework**,
JavaScript e SVG. Salve diagramas em JSON e exporte HTML ou SVG.

## Executáveis

A aba **Releases** disponibiliza dois builds nativos:

- **Linux x86_64: PyQt6 + QtWebEngine**, gerado no Ubuntu 22.04;
  formato `DFD-Studio-Linux-x86_64-v0.0.1.tar.gz`.
- **Windows x86_64: Qt5 + QtWebEngine**, pacote ZIP.
- Cada arquivo vem acompanhado de um checksum SHA-256.

Extraia **a pasta inteira**, não só o executável. No Linux,
bibliotecas gráficas nativas compatíveis ainda são necessárias.

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

**Primeira publicação v0.0.1:** abra a aba **Actions**, escolha
**DFD Studio - CI e releases**, selecione a branch **main**, execute
**Run workflow** com a entrada `tag=v0.0.1`. Após testes e builds
aprovados, a Action cria a tag e publica ambos os pacotes e seus hashes.

Alternativamente, crie a tag a partir do commit da main:

```bash
git checkout main
git pull --ff-only
git tag -a v0.0.1 -m "DFD Studio v0.0.1"
git push origin v0.0.1
```

Em próximas versões, atualize VERSION e CHANGELOG.md antes de criar
a tag. **Não mova uma tag publicada:** faça uma versão seguinte.
Documentação funcional: [LEIA-ME.md](LEIA-ME.md).
