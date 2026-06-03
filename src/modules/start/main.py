import time

from src.modules.game.main import clicar_avaliar_pyautogui, imagem_aparece_na_tela
from src.shared.constant import IMAGEM_AVALIAR, IMAGEM_FILL, IMAGEM_READY, NICKNAME


def nickname(page):
    try:
        campo = page.get_by_role("textbox").first
        campo.wait_for(state="visible", timeout=15000)
        campo.click()
        campo.fill(NICKNAME)
        page.get_by_role("button", name="JOGAR").click(timeout=15000)
        print("Nickname preenchido e cliquei em JOGAR.")
        return True

    except Exception as erro:
        print(f"Não consegui entrar com nickname: {erro}")
        return False


def clicar_estou_pronto(page):
    if imagem_aparece_na_tela(IMAGEM_READY, confidence=0.9):
        print("ready.png apareceu na tela. Clicando em ESTOU PRONTO...")
        page.click("text=ESTOU PRONTO", timeout=50000)
        return True

    return False


def iniciar_jogo(page):
    entrou = nickname(page)

    if not entrou:
        return False

    page.wait_for_timeout(2000)

    if clicar_estou_pronto(page):
        print("Botão ESTOU PRONTO clicado. Aguardando partida começar...")
        page.wait_for_timeout(10000)
    else:
        print("Botão ESTOU PRONTO não encontrado. Usando imagens para determinar o fluxo de início.")

    inicio = time.time()
    timeout = 120

    while True:
        if imagem_aparece_na_tela(IMAGEM_FILL):
            print("fill.png detectada. Iniciando preenchimento assim que o jogo estiver ativo.")
            return True

        if imagem_aparece_na_tela(IMAGEM_AVALIAR):
            print("avaliar.png detectada. Clicando em AVALIAR para avançar no fluxo.")
            clicar_avaliar_pyautogui()
            page.wait_for_timeout(2000)
            continue

        if imagem_aparece_na_tela(IMAGEM_READY):
            print("ready.png detectada. Aguardando partida iniciar...")
            page.wait_for_timeout(2000)
            continue

        if time.time() - inicio > timeout:
            print("Timeout ao tentar determinar o fluxo de início do jogo.")
            return False

        print("Nenhuma imagem de início detectada. Verificando novamente...")
        page.wait_for_timeout(1000)