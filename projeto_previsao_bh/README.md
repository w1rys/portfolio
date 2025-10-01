# Previsão de Preços de Imóveis – Belo Horizonte/MG

Este projeto analisa o mercado de apartamentos em Belo Horizonte-MG e fornece uma ferramenta interativa para estimar o valor de venda de imóveis com base em suas características.  

## Objetivo
Criar um modelo de Machine Learning capaz de prever preços de forma precisa e interpretável, considerando fatores como metragem, localização e número de quartos e banheiros.

## Estrutura do Projeto
O projeto segue cinco etapas principais:

1. **Coleta de Dados:**  
   Extração de informações de portais imobiliários usando automação com Selenium e tratamento de conteúdos dinâmicos.

2. **Análise e Limpeza:**  
   Processamento e organização dos dados com Pandas, e visualizações com Matplotlib e Seaborn para entender padrões e correlações.

3. **Engenharia de Features:**  
   Criação de variáveis geoespaciais usando Geopy, calculando distâncias até pontos de interesse da cidade, como shoppings, parques e hospitais.

4. **Modelagem e Interpretação:**  
   Teste e comparação de diferentes modelos de regressão (Linear, Random Forest, XGBoost e Rede Neural) com otimização de hiperparâmetros.  
   O modelo final (Random Forest) foi analisado com SHAP para explicar suas previsões.

5. **Aplicação Web:**  
   Desenvolvimento de uma interface interativa em Streamlit, permitindo que usuários obtenham estimativas de preço em tempo real, incluindo análise de incerteza.

## Tecnologias Utilizadas
- **Coleta de Dados:** Selenium, BeautifulSoup  
- **Análise de Dados:** Pandas, Matplotlib, Seaborn, Geopy  
- **Modelagem:** Scikit-learn, XGBoost, Statsmodels  
- **Interpretabilidade:** SHAP  
- **Aplicação Web:** Streamlit  
- **Gerenciamento de Dependências:** Poetry
