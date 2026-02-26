# AssetFlow - Gestão de Ativos de TI

O **AssetFlow** é uma solução moderna e segura para o controlo de inventário de hardware. Desenvolvido para equipas de TI, o sistema permite o registo de ativos, gestão de status (Disponível, Em Uso, Manutenção) e atribuição rápida de responsáveis, agora com camadas reforçadas de segurança.


## Funcionalidades Principais

- **Segurança Avançada:** Armazenamento de palavras-passe utilizando hash **PBKDF2** com salt, garantindo a proteção dos dados dos utilizadores.
- **Controlo de Acesso (RBAC):** Distinção entre perfis de **Administrador** (controlo total) e **Técnico** (apenas leitura e atribuição).
- **Filtros Dinâmicos:** Pesquisa inteligente por **Tipo** (via select) e **Modelo** para localização rápida de equipamentos.
- **Relatórios Inteligentes:** Exportação de relatórios em **PDF** que respeitam os filtros aplicados na visualização atual.
- **Dashboard SaaS:** Interface limpa e moderna com indicadores em tempo real sobre o estado do inventário.

## Tecnologias Utilizadas

- **Back-end:** Python 3 + Flask
- **Segurança:** Werkzeug Security (PBKDF2)
- **Front-end:** HTML5, CSS3 (Custom SaaS Style), Bootstrap 5, Bootstrap Icons
- **Base de Dados:** SQLite3
- **Relatórios:** FPDF2

## Como Executar o Projeto

### Pré-requisitos
- Python 3.x instalado.

### Instalação
1. **Clonar o repositório:**
   ```bash
   git clone [https://github.com/teu-utilizador/AssetFlow.git](https://github.com/teu-utilizador/AssetFlow.git)
   cd AssetFlow
