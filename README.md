# freeze-cli

O programa gera arquivos de requirements para ambientes de produção e desenovlimento

Gerado um binario executável com pyinstaller.

```bash
pip install --upgrade pip wheel setuptools
pip install pyinstaller
```

O Comando do PyInstaller
```bash
pyinstaller -F --path=src ./src/main.py -n freeze-cli.sh
```

Arquivo freeze.ini que pode ser configurada
```properties
[main]
name:requirements
file:${name}.txt
config:config/${name}/
[files]
dev:${main:config}${main:name}_dev.txt
core:${main:config}${main:name}_core.txt
all:${main:config}${main:name}_all.txt
[command]
pip:pip freeze
cat:cat {} 2> /dev/null
```

Gera um arquivo **requirements_dev.txt** no caminho **config/requirements** 
e o arquivo requirements.txt com a inclusão do requirements_dev.txt
```bash
python src/main.py -d
```

Gera um arquivo **requirements_core.txt** no caminho **config/requirements** 
e o arquivo requirements.txt com a inclusão do requirements_core.txt
```bash
python src/main.py -c
```

Para mais dúvidas veja o help
```
python src/main.py -h
```