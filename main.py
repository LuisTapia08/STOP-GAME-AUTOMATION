import os
from playwright.sync_api import sync_playwright

from src.shared.constant import URL, STATE_PATH, IMAGEM_FILL, IMAGEM_AVALIAR
from src.modules.create_context.main import create_context
from src.modules.start.main import iniciar_jogo
from src.modules.game.main import imagem_aparece_na_tela, preencher_rodada, clicar_stop, confirmar_resultado, clicar_avaliar_pyautogui


def run():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        #usar o contexto salvo ou criar um novo se não existir
        if not os.path.exists(STATE_PATH):
            print("State não encontrado. Criando contexto...")
            create_context(browser)
        context = browser.new_context(
            storage_state=STATE_PATH,
            viewport={"width": 1366, "height": 768},
            locale="pt-BR",
            timezone_id="America/Manaus"
        )

        page = context.new_page()
        page.goto(URL, wait_until="domcontentloaded")

        try:
            iniciou = iniciar_jogo(page)

            if not iniciou:
                print("Não consegui iniciar o jogo.")
                return

            while True:
                if imagem_aparece_na_tela(IMAGEM_FILL):
                    print("fill.png apareceu na tela. Iniciando preenchimento...")
                    sucesso = preencher_rodada(page)

                    if sucesso:
                        resposta = input(
                            "Pressione ENTER para clicar em STOP ou digite N para não clicar: "
                        ).strip().upper()

                        if resposta != "N":
                            clicar_stop(page)
                            confirmar_resultado(page)
                            page.wait_for_timeout(2000)
                            clicar_avaliar_pyautogui()
                    else:
                        print("Rodada interrompida ou encerrada por outro jogador.")

                    print("Aguardando 48000ms para próxima rodada...")
                    page.wait_for_timeout(48000)

                elif imagem_aparece_na_tela(IMAGEM_AVALIAR):
                    print("avaliar.png apareceu na tela. Clicando em AVALIAR...")
                    clicar_avaliar_pyautogui()
                    page.wait_for_timeout(1000)

                else:
                    print("Nenhuma imagem de fluxo detectada. Aguardando antes de verificar novamente...")
                    page.wait_for_timeout(1000)

        except KeyboardInterrupt:
            print("Programa encerrado pelo usuário.")

        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    run()