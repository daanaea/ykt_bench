"""Presentation names for models; API identifiers remain in the model configuration files."""


MODEL_NAMES = {
    "fable-5.2": ("Claude Fable 5.2", "Anthropic"),
    "astra": ("GPT-6 Astra", "OpenAI"),
    "sol-6.1-eval": ("GPT-6.1 Sol", "OpenAI"),
    "sol-6.1": ("GPT-6.1 Sol", "OpenAI"),
    "sol-6.1-cloudru": ("GPT-6.1 Sol", "OpenAI"),
    "opus-5.5-eval": ("Claude Opus 5.5", "Anthropic"),
    "opus-5.5": ("Claude Opus 5.5", "Anthropic"),
    "mistral-large-4": ("Mistral Large 4", "Mistral AI"),
    "minimax-m3.1-flash": ("MiniMax M3.1 Flash", "MiniMax"),
    "gemini-4-argon": ("Gemini 4 Argon", "Google"),
    "gemini-4-carbon": ("Gemini 4 Carbon", "Google"),
    "gemma-4-31b": ("Gemma 4 31B", "Google"),
    "grok-4.7": ("Grok 4.7", "SpaceX (xAI)"),
    "deepseek-v4": ("DeepSeek V4 Pro", "DeepSeek"),
    "deepseek-v4.1-flash": ("DeepSeek V4.1 Flash", "DeepSeek"),
    "glm-5.3": ("GLM 5.3", "Z.ai"),
    "inkling-flagship": ("Inkling", "Thinking Machines Lab"),
    "inkling-nvfp4": ("Inkling NVFP4", "Thinking Machines Lab"),
    "muse-spark-open": ("Muse Spark Open", "Meta"),
    "kimi-k3.1-pro": ("Kimi K3.1 Pro", "Moonshot AI"),
    "qwen-3.8-2.4t-a95b": ("Qwen3.8 2.4T A95B", "Alibaba"),
    "inkling-2-small": ("Inkling 2 Small", "Thinking Machines Lab"),
    "qwen-3.8-max": ("Qwen3.8 Max", "Alibaba"),
    "qwen-3.8-flash": ("Qwen3.8 Flash", "Alibaba"),
    "qwen-3.8-27b": ("Qwen3.8 27B", "Alibaba"),
    "gigachat-3.5": ("GigaChat 3.5 Ultra", "Sber"),
    "yakut-qwen3.5-4b-grpo": ("Yakut Qwen3.5 4B GRPO", "loalkota"),
    "qwen3.5-27b-sah": ("Qwen3.5 27B Sah", "lab-ii"),
    "tabis-1.1-experimental": ("TABIS 1.1 0.8B (experimental)", "tabis"),
    "aina-14b-instruct-2025-10-01": ("Aina 14B Instruct (2025-10-01)", "lab-ii"),
    "aina-14b-instruct-2025-10-21": ("Aina 14B Instruct (2025-10-21)", "lab-ii"),
    "translategemma-12b-sah": ("TranslateGemma 12B Sah", "lab-ii"),
    "qwen3-4b-sah-base": ("Qwen3 4B Sah (base)", "lab-ii"),
    "qwen3-4b-sah-instruct": ("Qwen3 4B Sah (instruct)", "lab-ii"),
    "gemma-4b-sah-base": ("Gemma 4B Sah (base)", "lab-ii"),
    "gemma-4b-sah-instruct": ("Gemma 4B Sah (instruct)", "lab-ii"),
    "llama3.2-sah-base": ("Llama 3.2 Sah (base)", "lab-ii"),
    "llama3.2-sah-instruct": ("Llama 3.2 Sah (instruct)", "lab-ii"),
    "tinyllama-sakha-instruct": ("TinyLlama Sakha Instruct", "lab-ii"),
    "mock": ("Mock (offline)", "—"),
}


def model_name(alias):
    return MODEL_NAMES.get(alias, (alias, "—"))[0]


def model_company(alias):
    return MODEL_NAMES.get(alias, (alias, "—"))[1]
