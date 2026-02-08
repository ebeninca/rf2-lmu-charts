---
title: rFactor2 / LMU Charts
emoji: 🏁
colorFrom: gray
colorTo: blue
sdk: docker
pinned: false
short_description: rFactor2 and LMU race data visualization and analysis
---

# rFactor2 / LMU Charts 🏎️

[![Tests](https://github.com/ebeninca/rf2-lmu-charts/actions/workflows/test-deploy.yml/badge.svg)](https://github.com/ebeninca/rf2-lmu-charts/actions/workflows/test-deploy.yml)
[![CodeQL](https://github.com/ebeninca/rf2-lmu-charts/actions/workflows/codeql.yml/badge.svg)](https://github.com/ebeninca/rf2-lmu-charts/actions/workflows/codeql.yml)
[![Security Audit](https://github.com/ebeninca/rf2-lmu-charts/actions/workflows/security.yml/badge.svg)](https://github.com/ebeninca/rf2-lmu-charts/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/ebeninca/rf2-lmu-charts/branch/main/graph/badge.svg)](https://codecov.io/gh/ebeninca/rf2-lmu-charts)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)

Visualization and analysis tool for rFactor2 and Le Mans Ultimate race data.

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

## How to Run

Address in all cases: http://localhost:7860/

### Local development (Flask)

Why? Flask allows hot-deploy

```sh 
$ DEBUG=True python app.py
``` 

### Build for standalone execution (PyInstaller / Waitress server)

Why? Waitress (multi-thread) runs both in Windows and Linux

```sh
$ rm -rf build dist *.spec && pyinstaller --onefile --name rf2-lmu-charts --add-data "assets:assets" --add-data "samples:samples" --hidden-import=waitress app.py 2>&1 | tail -10
```

### Production (Gunicorn / Docker)

Why? Gunicorn runs multi-process, more efficient for Python

```sh
$ docker build -t rf2-lmu-charts .
$ docker run -p 7860:7860 rf2-lmu-charts
```

To stop the container

```sh
$ docker stop rf2-lmu-charts && docker rm rf2-lmu-charts
```

## Backlog

- Segurança, evitar DDOS, etc.
- Gravação dos arquivos e geração de link

