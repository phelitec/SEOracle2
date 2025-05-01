# 🚀 SEO Content Generator for WordPress

Um gerador automatizado de conteúdo SEO que utiliza a OpenAI (GPT-4o-mini) para criar posts otimizados e publicá-los diretamente em blogs WordPress.

## ✨ Funcionalidades

- 📝 Geração automática de conteúdo otimizado para SEO
- 🔍 Análise de palavras-chave e planejamento de conteúdo
- 📊 Otimização de densidade de palavras-chave
- 🌐 Publicação automática via WordPress REST API
- 🔄 Fluxo completo de trabalho: planejamento → criação → revisão → publicação

## 📋 Pré-requisitos

- Python 3.7 ou superior
- Uma conta na OpenAI com API key
- Um site WordPress com aplicação de senhas configurada

## 🔧 Instalação

1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/seo-content-generator.git
cd seo-content-generator
```

2. Instale as dependências
```bash
pip install -r requirements.txt
```

3. Configure suas credenciais
```bash
python setup.py
```

## ⚙️ Configuração

O arquivo `config.ini` contém todas as configurações necessárias:

```ini
[OpenAI]
api_key = sua_api_key_aqui
model = gpt-4o-mini

[WordPress]
site_url = https://seu-site.com
username = seu_usuario
app_password = sua_senha_de_aplicacao

[Keywords]
file = keywords.txt

[Content]
posts_per_run = 1
min_words = 800
max_words = 1500
target_category = 

[CTA]
url = https://seu-site.com/oferta
text = Quero Crescer
```

## 📝 Arquivo de Palavras-chave

O arquivo `keywords.txt` deve conter uma palavra-chave por linha:

```
# Coloque suas palavras-chave aqui (uma por linha)
# Você pode adicionar contexto após dois-pontos
marketing digital: estratégias para pequenas empresas
seo para iniciantes
```

## 🚀 Uso

Para gerar conteúdo, execute:

```bash
python main.py
```

Opções:
- `--config`: Especificar um arquivo de configuração alternativo
- `--posts`: Número de posts a serem gerados

Exemplo:
```bash
python main.py --posts 5
```

## 📊 Estrutura do Projeto

```
seo-content-generator/
├── main.py                    # Ponto de entrada principal
├── setup.py                   # Script de configuração inicial
├── requirements.txt           # Dependências
├── config.ini                 # Arquivo de configuração
├── keywords.txt               # Lista de palavras-chave
├── seo_generator/
│   ├── __init__.py
│   ├── config_manager.py      # Gerenciamento de configurações
│   ├── content_generator.py   # Geração de conteúdo
│   ├── wordpress_api.py       # Interação com WordPress
│   └── utils.py               # Funções utilitárias
└── logs/
    └── seo_content_generator.log  # Logs de execução
```

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

1. Fork o projeto
2. Crie sua Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request