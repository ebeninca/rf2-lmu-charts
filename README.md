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

> Application is running at: [HuggingFace Spaces](https://huggingface.co/spaces/ebeninca/rf2-lmu-charts)

Alternatively you can download the Release for Linux and Windows in this page.

## How to run the source code locally

Address in all cases: http://localhost:7860/

### Local development (Flask)

Why? Flask allows hot-deploy

```sh 
$ DEBUG=True python app.py
``` 

### Build for standalone execution (PyInstaller / Waitress server)

Why? Waitress (multi-thread) runs both in Windows and Linux

Linux

```sh
$ rm -rf build dist *.spec && pyinstaller --onefile --name rf2-lmu-charts --icon=assets/finish-flag.png --add-data "assets:assets" --add-data "samples:samples" --hidden-import=waitress app.py 2>&1 | tail -10
```

Windows 

```sh
$ rmdir /s /q build dist & del /q *.spec & pip install pyinstaller & pyinstaller --onefile --name rf2-lmu-charts-windows.exe --icon=assets/finish-flag.ico --add-data "assets;assets" --add-data "samples;samples" --hidden-import=waitress app.py

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

- ~~Segurança, evitar DDOS, etc.~~ ✅ **IMPLEMENTADO** - Ver [SECURITY_README.md](SECURITY_README.md)
- Gravação dos arquivos e geração de link
- Inversao de cores de Icones em Events
- Manter logs gerais em stdout, mandar logs criticos e erros para Discord ??

## 🔒 Security

This application implements comprehensive security measures including:
- Rate limiting (200/day, 50/hour per IP)
- File upload validation (size, type, structure)
- XXE attack prevention
- Security headers (CSP, XSS protection)
- Request timeouts
- Secure XML parsing

For details, see:
- [SECURITY_README.md](SECURITY_README.md) - Quick start guide
- [SECURITY.md](SECURITY.md) - Complete security plan
- [SECURITY_IMPLEMENTATION.md](SECURITY_IMPLEMENTATION.md) - Implementation details

Test security implementation:
```bash
python test_security.py
```