# Deploy para Hugging Face Spaces

## Passos:

1. Acesse https://huggingface.co/spaces e faça login
2. Clique em "Create new Space"
3. Escolha um nome (ex: race-data-viz)
4. Selecione "Docker" como SDK
5. Clique em "Create Space"

6. No seu terminal, execute:

```bash
cd /home/ebeninca/repo/race-graphs

# Instale git-lfs se não tiver
git lfs install

# Clone o repositório do Space
git clone https://huggingface.co/spaces/SEU_USERNAME/NOME_DO_SPACE
cd NOME_DO_SPACE

# Copie os arquivos
cp ../README_HF.md README.md
cp ../Dockerfile .
cp ../requirements.txt .
cp ../app.py .
cp ../2025_10_26_01_40_42-54R1.xml .

# Commit e push
git add .
git commit -m "Initial commit"
git push
```

7. Aguarde alguns minutos e sua aplicação estará online!

## Arquivos necessários (já criados):
- ✅ README_HF.md (renomear para README.md no Space)
- ✅ Dockerfile
- ✅ requirements.txt
- ✅ app.py (atualizado para porta 7860)
- ✅ 2025_10_26_01_40_42-54R1.xml

## URL final:
https://huggingface.co/spaces/SEU_USERNAME/NOME_DO_SPACE
