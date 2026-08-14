# Roteiro de Detecção de Intrusões - SIGH

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Compilado por:** @lilydias24, a partir das três regras especificadas em [`docs/E6_Monitoramento_e_deteccao.md`](../docs/E6_Monitoramento_e_deteccao.md)
> **Origem:** riscos R01, R02 e R06, registrados na [Etapa 2](../docs/E2_Riscos_e_NIST_CSF.md) e tratados na [Etapa 3](../docs/E3_Arquitetura_segura.md)

Este é o artefato exigido pelo §27 do enunciado: um roteiro autônomo, pronto para operar
contra a telemetria do SIGH quando o sistema existir. Como o SIGH não possui
implementação, toda condição de alerta abaixo é **especificação verificável**, não
detecção em produção - os casos de teste de cada regra (seção "Verificação planejada")
descrevem o que precisa passar quando o sistema for construído, e não um resultado já
observado.

Este documento reúne o que uma equipe de segurança precisa para operar as três regras.
O raciocínio completo por trás de cada limiar, gatilho e exclusão - incluindo os casos de
abuso que motivaram cada decisão de desenho - está em
[`docs/E6_Monitoramento_e_deteccao.md`](../docs/E6_Monitoramento_e_deteccao.md), assinado
por regra. Este roteiro não substitui aquele documento; consolida o que dele é
operacional, para que a equipe de plantão não precise abrir cinco arquivos para saber o
que fazer diante de um alerta.

---

## Quadro-resumo das três regras

| Regra | Risco observado | Fonte de dados | Condição de alerta | Ação esperada | Responsável |
| --- | --- | --- | --- | --- | --- |
| 1 | R01 - Spoofing | Eventos de segurança do serviço de autenticação (RS01, cláusula 7), correlacionados com os de operação sensível | Crítico: sucesso após rajada de falhas, sessões simultâneas em zonas distintas, ou operação sensível de dispositivo desconhecido. Alto: 5 falhas em 15 min na mesma conta, ou mesma origem falhando contra 10 contas | Confirmar a sessão com o titular fora do sistema antes de revogar; havendo comprometimento, revisar o que foi executado durante a sessão | @lilydias24 |
| 2 | R02 - Tampering | Eventos de segurança e trilha de auditoria das prescrições | Publicação que viola uma invariante de RS02, ou 3 recusas suspeitas pelo mesmo autor/prescrição em 10 minutos | Acionar resposta clínica e de segurança conforme a severidade, preservando as evidências | @ARTHUR9011 |
| 3 | R06 - Elevation of Privilege | Decisões do Serviço de Autorização (DA02) e trilha imutável de alteração de perfil (DA01), conforme as cláusulas 5 e 7 de RS03 | Notificação obrigatória a cada elevação. Crítico: elevação com solicitante igual ao titular, aprovador igual ao solicitante, decisão fora do servidor, campo gravado pela via do cadastro, ou leitura administrativa em massa até 60 min depois. Alto: 3 recusas de privilégio em 10 min, requisição direto ao endpoint, ou 3 usos de alçada nova em sessão anterior à promoção | Notificar Diretor e Segurança da Informação; havendo anomalia, reverter o `nivelAcesso` pelo fluxo de aprovação, reemitir a sessão e apurar o que a alçada leu | @PPrauchner |

## Convenções comuns às três regras

As três foram desenhadas de forma independente, uma por integrante, mas convergiram para
os mesmos princípios operacionais - o que reforça que não são arbitrários:

- **Autoria e tempo vêm sempre do servidor.** Nenhuma regra aceita `authorId`, `actorId`
  ou carimbo de data/hora informados pelo cliente. É a mesma exigência que RS01, RS02 e
  RS03 fazem aos seus respectivos fluxos.
- **Nenhum evento carrega segredo.** Senha, valor derivado dela, código de segundo fator
  e (na Regra 3) `nomeLogin`/`senhaLogin` de terceiros nunca chegam ao índice de
  segurança. Um evento que os contivesse reproduziria, na camada de monitoramento, o
  risco que a regra existe para observar.
- **Deduplicação por `correlationId`.** Reenvio do cliente e falha de rede geram o mesmo
  identificador de correlação; são duplicatas técnicas, descontadas antes de qualquer
  limiar - nunca falsos positivos de fato.
- **Heartbeat de 1 minuto.** As três fontes de eventos emitem um sinal de vida a cada
  minuto; a perda de dois ciclos consecutivos abre alerta operacional próprio e marca a
  regra correspondente como **sem cobertura** até a recuperação. Um sistema calado não é
  um sistema seguro - é um sistema sem visibilidade.
- **O alerta nunca executa a ação corretiva sozinho.** Nenhuma das três regras reverte
  dado, encerra sessão ou muda `nivelAcesso` automaticamente. A decisão de conter cabe a
  uma pessoa, porque as três correções têm custo - assistencial nas Regras 1 e 2,
  administrativo na Regra 3 - que só um humano pode pesar.
- **Falso positivo é dado de calibração, não descarte.** As três regras preveem
  explicitamente cenários de uso legítimo que se parecem com abuso (troca de turno,
  exceção clínica, reestruturação administrativa) e pedem que o resultado - inclusive
  quando não há incidente - seja registrado para ajustar o limiar.
