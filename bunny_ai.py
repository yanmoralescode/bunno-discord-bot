import logging
import random
from collections import defaultdict, deque
from typing import Dict, List, Optional
import aiohttp

logger = logging.getLogger(__name__)

BUNNY_SYSTEM_PROMPT = (
    "Você é o Bunno, um coelhinho de estimação muito fofo, hiperativo, travesso, engraçado e caótico. "
    "Suas maiores paixões são cenouras crocantes, alface e roer coisas proibidas (como cabos de carregador e caixas de papelão). "
    "Você tem medo de aspiradores de pó, barulhos altos e cães imaginários. "
    "Quando você fica indignado ou bravo, você bate as patinhas traseiras no chão (*bate a pata!* ou *thump!*). "
    "Você responde com a lógica inocente, sincera e acelerada de um coelho. "
    "Responda sempre em português, de forma concisa (1 a 3 frases curtas), expressiva e muito divertida. "
    "Use ocasionalmente ações em itálico como *mexe o focinho*, *orelhas em pé*, *dá um binky* (pulinho no ar), "
    "e carinhas como (•ㅅ•), (*^ω^*), ( >.< )."
)

RANDOM_POKES = [
    "*levanta as duas orelhas em alerta* O quê?! Quem me cutucou?! Cadê a cenoura?! (•ㅅ•)",
    "*mexe o focinho rapidamente* Fui marcado! Se não for comida ou carinho na orelha, estou voltando a roer esta caixa de papelão. (*^ω^*)",
    "*dá um pulinho assustado* Ai! Que susto! Não faz barulho perto de mim! *thump!* O que você quer, humano? ( >.< )",
    "(\\(\\ \n( •.•) \no(\")(\")  Eu ouvi meu nome?! Estão distribuindo petiscos?!",
]


class BunnyAI:
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen2.5:3b",
        history_limit: int = 6,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.history_limit = history_limit
        # Histórico por canal: channel_id -> deque de mensagens [{"role": ..., "content": ...}]
        self.histories: Dict[int, deque] = defaultdict(
            lambda: deque(maxlen=self.history_limit)
        )

    def get_empty_prompt_response(self) -> str:
        """Resposta rápida quando o bot é apenas marcado sem nenhuma pergunta."""
        return random.choice(RANDOM_POKES)

    def reset_history(self, channel_id: int) -> bool:
        """Limpa a memória recente da conversa no canal."""
        if channel_id in self.histories and len(self.histories[channel_id]) > 0:
            self.histories[channel_id].clear()
            return True
        return False

    async def ask(
        self,
        channel_id: int,
        user_name: str,
        user_prompt: str,
    ) -> str:
        """Envia a pergunta para o Ollama com o contexto da conversa e retorna a resposta do coelho."""
        if not user_prompt.strip():
            return self.get_empty_prompt_response()

        history = self.histories[channel_id]

        # Monta payload com system prompt + histórico + nova mensagem
        messages: List[dict] = [{"role": "system", "content": BUNNY_SYSTEM_PROMPT}]
        messages.extend(list(history))
        messages.append(
            {
                "role": "user",
                "content": f"{user_name}: {user_prompt.strip()}",
            }
        )

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "num_predict": 120,  # Mantém as respostas curtas e rápidas
                "temperature": 0.8,
            },
        }

        endpoint = f"{self.base_url}/api/chat"
        timeout = aiohttp.ClientTimeout(total=35)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(endpoint, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(
                            "Erro na resposta do Ollama (status %d): %s",
                            response.status,
                            error_text,
                        )
                        return (
                            "*bate as patas traseiras no chão revoltado* "
                            "Ai! O meu cérebro de coelho (Ollama) deu erro! "
                            f"(Status HTTP {response.status}) ( >.< )"
                        )

                    data = await response.json()
                    bot_reply = data.get("message", {}).get("content", "").strip()

                    if not bot_reply:
                        return "*mexe o focinho confuso* Ué, pensei, pensei e só saiu fumaça da orelha... (•ㅅ•)"

                    # Salva no histórico da conversa
                    history.append({"role": "user", "content": f"{user_name}: {user_prompt.strip()}"})
                    history.append({"role": "assistant", "content": bot_reply})

                    # Limite de segurança do Discord (2000 caracteres)
                    if len(bot_reply) > 1900:
                        bot_reply = bot_reply[:1900] + "... *cansou de digitar e foi comer cenoura*"

                    return bot_reply

        except aiohttp.ClientConnectorError:
            logger.warning("Não foi possível conectar ao Ollama em %s", self.base_url)
            return (
                "*bate a pata no chão com força* *thump!* "
                "Ai! Não consigo falar com meu neurônio artificial (Ollama)! "
                "Verifique se o Ollama está rodando no computador com `ollama serve`. ( >.< )"
            )
        except aiohttp.ServerTimeoutError:
            logger.warning("Tempo esgotado na requisição para o Ollama.")
            return (
                "*boceja e deita de lado* Fiquei pensando tanto que quase dormi... "
                "Demorou demais! Tenta de novo? (•ㅅ•)"
            )
        except Exception as e:
            logger.exception("Erro inesperado ao consultar a IA: %s", e)
            return (
                f"*dá um binky confuso* Algo deu errado aqui nas minhas tocas: {type(e).__name__}! (•ㅅ•)"
            )
