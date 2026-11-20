# Teste inicial no Manus (antes do briefing completo)

Este teste confere se o ambiente do Manus consegue rodar o pipeline: clonar o repositório, instalar, gerar a voz, montar o vídeo e renderizar. Não cria perfil, quadro nem agendamento, e não publica nada.

Cole o bloco abaixo numa tarefa nova do Manus.

---

Quero testar se o seu ambiente roda o meu pipeline de vídeo. Não crie perfis, grupos, quadros nem agendamentos, e não publique nada.

1. Clone o repositório privado `https://github.com/ferfagner/redacao-fato`. Se precisar de acesso ao GitHub e aparecer um cartão de autorização, pare e me mostre.
2. Dentro da pasta, rode `bash setup.sh` e me mostre as últimas linhas da saída. Se faltar algo (Python 3.10+, Node 22+, FFmpeg ou o Chrome do HyperFrames), tente instalar pelo gerenciador de pacotes do sistema. Se não der, pare e me diga o que faltou.
3. Rode `python3 -m fato revisar exemplos/teste-objetos` e depois `python3 -m fato render exemplos/teste-objetos`.
4. Me devolva:
   - o conteúdo de `exemplos/teste-objetos/saida/relatorio.json` dos dois comandos;
   - o tempo que cada comando levou;
   - a imagem `exemplos/teste-objetos/saida/folha.png`;
   - o vídeo `exemplos/teste-objetos/saida/video.mp4`.
5. Não edite nenhum arquivo do repositório. Se algum comando falhar, mostre o erro completo e pare.

---

## Como ler o resultado

- Nos dois comandos, `ok: true` e a folha igual à do teste local significam que o ambiente funciona. Aí é só colar o `briefing_coordenador.md`.
- **O render passou de 10 min:** o Chrome do Manus está sem placa de vídeo e o 3D ficou lento. Ainda funciona para um vídeo por dia, mas convém adiantar o horário da Rotina B.
- **Falhou no `setup.sh` ou no `edge-tts`:** traga a mensagem de erro para ajustarmos o setup.
