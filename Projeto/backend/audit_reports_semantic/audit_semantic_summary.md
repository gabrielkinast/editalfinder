# Auditoria semântica

- Fontes: **94**
- Itens: **802**

## Top 20 problemas

- area_cientifica_sem_evidencia: 105
- area_tecnologica_sem_evidencia: 83
- area_excessiva: 61
- classificacao_muito_ampla: 52
- setor_estrategico_excessivo: 42
- tipo_recurso_generico: 38
- classificacao_incoerente_com_fonte: 27
- publico_alvo_sem_evidencia: 24
- oportunidade_fomento_sem_fomento: 1

## Top ajustes recomendados

- Restringir perfil_ideal genérico por evidência textual mínima.
- Separar regras de crédito vs fomento por fonte + palavras-chave obrigatórias.
- Exigir marcador de licitação para tipo_oportunidade=licitacao/compra_publica.
- Reduzir classificação ampla quando classficacao_confianca=baixa.
- Para fontes nucleares/defesa: usar peso institucional + objeto para evitar over/under tag.
- Fortalecer extração de publico_alvo por entidades explícitas.
- Adicionar fallback de área para itens com tipo_recurso definido e área vazia.
- Revisar taxonomia em fontes com flag_rate > 100%.