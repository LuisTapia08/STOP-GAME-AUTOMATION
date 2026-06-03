from src.shared.constant import URL, STATE_PATH


def create_context(browser):
    context = browser.new_context(
        viewport={"width": 1366, "height": 768},
        locale="pt-BR",
        timezone_id="America/Manaus"
    )

    page = context.new_page()
    page.goto(URL, wait_until="domcontentloaded")

    page.wait_for_timeout(3000)

    context.storage_state(path=STATE_PATH)

    print("Contexto salvo com sucesso.")

    context.close()