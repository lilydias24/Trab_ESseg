# Modelagem de Ameaças e Tratamento de Riscos — [Nome do Sistema]

---

## Etapa 1 — Casos de Abuso e Modelagem de Ameaças com STRIDE

### 1. Identificação do sistema

- **Nome do sistema:**
- **Integrantes do grupo:**
- **Repositório:**
- **Justificativa para a escolha do sistema:**

### 2. Descrição do sistema

*(Descrever o problema que o sistema resolve, quem o utiliza, principais funcionalidades, informações armazenadas/transmitidas e recursos que precisam ser protegidos.)*

### 3. Usuários, ativos e pontos de interação

#### 3.1 Usuários e perfis de acesso

| Usuário/Perfil | Principais ações |
| --- | --- |
| | |

#### 3.2 Ativos importantes

*(Listar dados pessoais, credenciais, pagamentos, avaliações, mensagens, localização, documentos, etc., destacando os que causam prejuízo se comprometidos.)*

#### 3.3 Pontos de interação e componentes

| Elemento | Função |
| --- | --- |
| | |

### 4. Visão geral da arquitetura ou fluxo

*(Descrição textual e/ou diagrama — ver `diagramas/`. Pode ser diagrama de contexto, fluxo de dados, componentes ou casos de uso.)*

`![Diagrama de contexto](../diagramas/diagrama-contexto.png)`

### 5. Modelagem de ameaças com STRIDE

| ID | Categoria STRIDE | Componente ou ativo | Ameaça identificada | Possível impacto |
| --- | --- | --- | --- | --- |
| T01 | Spoofing | | | |
| T02 | Tampering | | | |
| T03 | Repudiation | | | |
| T04 | Information Disclosure | | | |
| T05 | Denial of Service | | | |
| T06 | Elevation of Privilege | | | |

*(Adicionar quantas linhas forem necessárias por categoria; justificar caso alguma categoria não seja aplicável.)*

### 6. Casos de abuso

#### CA01 — [Título]

- **Ator:**
- **Objetivo:**
- **Condições necessárias:**
- **Fluxo de abuso:**
  1.
  2.
- **Impacto esperado:**
- **Categorias STRIDE relacionadas:**

*(Repetir a estrutura acima para CA02, CA03... — recomenda-se ao menos 1 caso por integrante.)*

### 7. Considerações finais (Etapa 1)

- **Ameaças mais preocupantes:**
- **Ativos mais importantes:**
- **Tipos de abuso de maior impacto:**
- **Principais dificuldades encontradas pelo grupo:**

---

## Etapa 2 — Análise, Priorização e Tratamento de Riscos com o NIST CSF 2.0

### 8. Critérios de probabilidade

| Valor | Classificação | Critério |
| --- | --- | --- |
| 1 | Baixa | O evento depende de condições incomuns, acesso muito específico ou grande capacidade técnica |
| 2 | Média-baixa | O evento é possível, mas depende de uma vulnerabilidade ou condição específica |
| 3 | Média-alta | O evento é plausível e pode ocorrer em situações comuns de uso ou ataque |
| 4 | Alta | O evento pode ocorrer com facilidade, frequência ou durante condições previsíveis do sistema |

### 9. Critérios de impacto

| Valor | Classificação | Critério |
| --- | --- | --- |
| 1 | Baixo | Causa pequeno transtorno e pode ser corrigido rapidamente |
| 2 | Moderado | Causa interrupção ou inconsistência limitada, com possibilidade de recuperação |
| 3 | Alto | Causa prejuízo relevante aos usuários, ao negócio, à administração ou à privacidade |
| 4 | Muito alto | Pode afetar muitos usuários, comprometer operações críticas ou causar prejuízo grave |

### 10. Cálculo e classificação dos riscos

Pontuação = Probabilidade × Impacto

| Pontuação | Nível do risco |
| --- | --- |
| 1 a 3 | Baixo |
| 4 a 7 | Médio |
| 8 a 11 | Alto |
| 12 a 16 | Crítico |

### 11. Registro de riscos

| ID | Origem STRIDE | Evento de risco | Vulnerabilidade ou condição | Probabilidade | Impacto | Pontuação | Nível |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R01 | Spoofing | | | | | | |
| R02 | Tampering | | | | | | |
| R03 | Repudiation | | | | | | |
| R04 | Information Disclosure | | | | | | |
| R05 | Denial of Service | | | | | | |
| R06 | Elevation of Privilege | | | | | | |

### 12. Justificativas das avaliações

*(Para cada risco: por que a probabilidade e o impacto receberam aqueles valores, quem/o que é afetado, e por que o nível calculado representa adequadamente o contexto.)*

### 13. Priorização dos riscos

*(Ordem de tratamento considerando pontuação, gravidade das consequências, usuários afetados, importância do ativo, possibilidade de recuperação, dependências e urgência.)*

### 14. Estratégias de tratamento

| Estratégia | Descrição |
| --- | --- |
| Evitar | Eliminar a atividade ou condição que dá origem ao risco |
| Reduzir | Implementar medidas para diminuir a probabilidade ou o impacto |
| Compartilhar | Atribuir parte da operação ou das consequências a um terceiro |
| Aceitar | Reconhecer e manter conscientemente o risco, com justificativa e acompanhamento |

| Risco | Estratégia escolhida | Justificativa |
| --- | --- | --- |
| R01 | | |
| R02 | | |
| R03 | | |
| R04 | | |
| R05 | | |
| R06 | | |

### 15. Funções do NIST CSF 2.0

| Função | Finalidade |
| --- | --- |
| Govern | Definir políticas, responsabilidades, prioridades e critérios de decisão |
| Identify | Conhecer ativos, dependências, vulnerabilidades e riscos |
| Protect | Implementar salvaguardas para reduzir a probabilidade ou o impacto |
| Detect | Identificar eventos suspeitos, falhas e possíveis incidentes |
| Respond | Conter, analisar, comunicar e tratar incidentes |
| Recover | Restaurar serviços e dados e reduzir os prejuízos causados |

### 16. Mapeamento dos riscos para as funções do NIST CSF

| Risco | Govern | Identify | Protect | Detect | Respond | Recover |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| R01 | | | | | | |
| R02 | | | | | | |
| R03 | | | | | | |
| R04 | | | | | | |
| R05 | | | | | | |
| R06 | | | | | | |

### 17. Plano de tratamento

| Risco | Estratégia | Controles propostos | Funções relacionadas | Responsáveis | Evidências e verificação |
| --- | --- | --- | --- | --- | --- |
| R01 | | | | | |
| R02 | | | | | |
| R03 | | | | | |
| R04 | | | | | |
| R05 | | | | | |
| R06 | | | | | |

### 18. Ordem inicial de implementação

1.
2.
3.

### 19. Estimativa do risco residual

| Risco | Nível inicial | Nível residual esperado | Condição para aceitar o residual |
| --- | --- | --- | --- |
| R01 | | | |
| R02 | | | |
| R03 | | | |
| R04 | | | |
| R05 | | | |
| R06 | | | |

### 20. Considerações finais (Etapa 2)

- **Riscos mais importantes:**
- **Razões da priorização:**
- **Estratégias de tratamento predominantes:**
- **Funções do NIST mais relevantes:**
- **Controles considerados essenciais:**
- **Principais dificuldades e limitações da avaliação:**
- **Pontos a detalhar nas próximas etapas:**

---

## Etapa 3 — *(aguardando enunciado do professor)*
