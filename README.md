# 🧪 Laboratório 02 – Um Estudo das Características de Qualidade de Sistemas Java

**Alunos:**  
- Luiz Felipe Campos de Morais  
- Marcus Vinícius Carvalho de Oliveira  

---

## 📌 Introdução
No desenvolvimento de sistemas *open-source*, em que diversos desenvolvedores contribuem em diferentes partes do código, há riscos relacionados à **evolução da qualidade interna**.  
Aspectos como **modularidade, manutenibilidade e legibilidade** podem ser comprometidos caso não haja boas práticas de revisão ou análise estática.  

Neste trabalho, analisamos **repositórios Java populares no GitHub** sob a perspectiva de métricas de qualidade calculadas pela ferramenta **CK**, buscando compreender como atributos de processo (popularidade, maturidade, atividade e tamanho) se relacionam com a qualidade do software.  

---

## ❓ Questões de Pesquisa

| RQ | Pergunta |
|----|----------|
| **RQ01** | Qual a relação entre a **popularidade** dos repositórios e as suas características de qualidade? |
| **RQ02** | Qual a relação entre a **maturidade** dos repositórios e as suas características de qualidade? |
| **RQ03** | Qual a relação entre a **atividade** dos repositórios e as suas características de qualidade? |
| **RQ04** | Qual a relação entre o **tamanho** dos repositórios e as suas características de qualidade? |

---

## 💡 Hipóteses Informais

- **RQ01:** Repositórios mais populares (mais estrelas) tendem a apresentar melhores métricas de qualidade, já que atraem mais colaboradores e maior rigor no processo de desenvolvimento.  
- **RQ02:** Repositórios mais maduros (mais antigos) devem apresentar maior estabilidade e possivelmente melhor coesão, mas também podem acumular mais acoplamento devido à evolução do código.  
- **RQ03:** Repositórios com maior atividade (mais *releases*) provavelmente mantêm boas práticas de engenharia, refletidas em melhor modularidade e manutenibilidade.  
- **RQ04:** Repositórios maiores (mais linhas de código) tendem a ter maior acoplamento e menor coesão, impactando negativamente a qualidade interna.  

---

## ⚙️ Metodologia

1. **Coleta dos Repositórios**  
   - Utilizamos a **API GraphQL do GitHub** para coletar os **1.000 repositórios mais populares escritos em Java**.  
   - Foram extraídas as seguintes métricas de processo:  
     - **Popularidade:** número de estrelas ⭐  
     - **Maturidade:** idade do repositório em anos 📅 (diferença entre a data de criação e a data atual)  
     - **Atividade:** número de *releases* 🚀  

2. **Geração do Dataset**  
   - As informações extraídas foram consolidadas em um arquivo **CSV (`repositorios.csv`)** contendo:  
     - Nome do repositório  
     - Número de *releases*  
     - Número de estrelas  
     - Idade em anos  

3. **Extração das Métricas de Qualidade (CK Tool)**  
   - Cada repositório foi **clonado localmente**.  
   - Utilizamos a ferramenta **[CK](https://github.com/mauricioaniche/ck)** para análise estática do código.  
   - Foram extraídas as métricas de qualidade:  
     - **CBO (Coupling Between Objects)** – acoplamento entre classes.  
     - **DIT (Depth of Inheritance Tree)** – profundidade da hierarquia de herança.  
     - **LCOM (Lack of Cohesion of Methods)** – coesão entre os métodos de uma classe.  

4. **Análise Estatística**  
   - Para cada questão de pesquisa (RQ), serão calculados **média, mediana e desvio padrão** das métricas de qualidade.  
   - As análises buscarão identificar correlações entre métricas de processo e métricas de qualidade.  

---

## 📊 Resultados (a preencher)

### 🔹 RQ01: Popularidade × Qualidade
| Métrica de Qualidade | Média | Mediana | Desvio Padrão |
|-----------------------|-------|---------|---------------|
| **CBO**              |       |         |               |
| **DIT**              |       |         |               |
| **LCOM**             |       |         |               |

---

### 🔹 RQ02: Maturidade × Qualidade
| Métrica de Qualidade | Média | Mediana | Desvio Padrão |
|-----------------------|-------|---------|---------------|
| **CBO**              |       |         |               |
| **DIT**              |       |         |               |
| **LCOM**             |       |         |               |

---

### 🔹 RQ03: Atividade × Qualidade
| Métrica de Qualidade | Média | Mediana | Desvio Padrão |
|-----------------------|-------|---------|---------------|
| **CBO**              |       |         |               |
| **DIT**              |       |         |               |
| **LCOM**             |       |         |               |

---

### 🔹 RQ04: Tamanho × Qualidade
| Métrica de Qualidade | Média | Mediana | Desvio Padrão |
|-----------------------|-------|---------|---------------|
| **CBO**              |       |         |               |
| **DIT**              |       |         |               |
| **LCOM**             |       |         |               |

---

## 🗣️ Discussão (a preencher)
> Nesta seção serão comparadas as hipóteses informais com os resultados obtidos, analisando se as tendências esperadas se confirmaram ou não.  

---

## 🎁 Bônus (opcional)
- Gráficos de correlação entre métricas de processo e de qualidade.  
- Testes estatísticos (ex.: Spearman ou Pearson) para validar as correlações observadas.  

---
