import time
from pathlib import Path

import pyautogui
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from src.shared.constant import IMAGEM_AGUARDANDO, IMAGEM_AVALIAR, IMAGEM_FILL
from src.modules.database.main import buscar_palavra, adicionar_ou_atualizar_palavra


def imagem_aparece_na_tela(caminho_imagem, confidence=0.75):
    if not Path(caminho_imagem).exists():
        return False
    try:
        posicao = pyautogui.locateOnScreen(
            str(caminho_imagem),
            confidence=confidence
        )
        return posicao is not None
    except Exception:
        return False


def aguardar_sair_da_tela_aguardando():
    print("Verificando tela de espera...")

    while imagem_aparece_na_tela(IMAGEM_AGUARDANDO, confidence=0.75):
        print("Imagem de espera encontrada. Aguardando a rodada começar...")
        time.sleep(1)

    print("Tela de espera sumiu. Tentando ler a letra...")


def pegar_letra(page):
    seletores = [
        ".letter p",
        "div[class*='letter'] p",
        "div[class*='maskLetter'] p"
    ]

    for seletor in seletores:
        try:
            elemento = page.locator(seletor).first
            elemento.wait_for(state="visible", timeout=10000)

            letra = elemento.inner_text().strip().upper()

            if len(letra) == 1 and letra.isalpha():
                return letra

        except Exception:
            pass

    return None


def validar_letra_com_usuario(letra):
    if not letra:
        letra = ""

    resposta = input(
        f"Letra lida: [{letra}] | Pressione ENTER para confirmar ou digite a letra correta: "
    ).strip().upper()

    if resposta == "":
        return letra

    return resposta[0]


def pegar_campos(page):
    lista = []

    try:
        respostas = page.locator("section[class*='answers'] div[class*='answer']").filter(
            has_not=page.locator("div[class*='answer-help']")
        )

        total = respostas.count()

        for i in range(total):
            resposta = respostas.nth(i)

            if not resposta.is_visible():
                continue

            tema = ""

            try:
                tema = resposta.locator("div[class*='tooltip'] p").first.inner_text(timeout=1000)
            except Exception:
                pass

            if not tema:
                try:
                    tema = resposta.locator("p").first.inner_text(timeout=1000)
                except Exception:
                    pass

            if not tema:
                continue

            tema = tema.strip()

            campo = None

            seletores_campo = [
                "input",
                "textarea",
                "[contenteditable='true']",
                "div[class*='input']",
                "div[class*='text']"
            ]

            for seletor in seletores_campo:
                try:
                    candidato = resposta.locator(seletor).first

                    if candidato.count() > 0 and candidato.is_visible():
                        campo = candidato
                        break

                except Exception:
                    pass

            if campo:
                lista.append({
                    "tema": tema,
                    "campo": campo,
                    "container": resposta
                })

    except Exception as erro:
        print(f"Erro ao buscar campos pela section answers: {erro}")

    if lista:
        return lista

    print("Tentando fallback por input, textarea e contenteditable...")

    try:
        campos = page.locator("input, textarea, [contenteditable='true']")
        total = campos.count()

        for i in range(total):
            campo = campos.nth(i)

            if not campo.is_visible():
                continue

            tema = campo.get_attribute("aria-label")

            if not tema:
                tema = campo.get_attribute("placeholder")

            if not tema:
                tema = campo.evaluate("""
                    elemento => {
                        let atual = elemento;
                        for (let i = 0; i < 8; i++) {
                            if (!atual) break;

                            const tooltip = atual.querySelector("div[class*='tooltip'] p");
                            if (tooltip && tooltip.innerText.trim()) {
                                return tooltip.innerText.trim();
                            }

                            const p = atual.querySelector("p");
                            if (p && p.innerText.trim()) {
                                return p.innerText.trim();
                            }

                            atual = atual.parentElement;
                        }

                        return "";
                    }
                """)

            if tema:
                lista.append({
                    "tema": tema.strip(),
                    "campo": campo,
                    "container": None
                })

    except Exception as erro:
        print(f"Erro no fallback dos campos: {erro}")

    return lista


def pedir_palavra_ao_usuario(letra, tema):
    palavra = input(
        f"Sem palavra para [{letra}] - [{tema}]. Digite uma palavra: "
    ).strip()

    if palavra:
        adicionar_ou_atualizar_palavra(letra, tema, palavra)

    return palavra


def preencher_campo(page, campo, container, palavra):
    try:
        campo.click()
        campo.fill(palavra)
        return True

    except Exception:
        pass

    try:
        campo.click()
        page.keyboard.press("Control+A")
        page.keyboard.type(palavra, delay=20)
        return True

    except Exception:
        pass

    try:
        if container:
            container.click()
            page.keyboard.press("Control+A")
            page.keyboard.type(palavra, delay=20)
            return True

    except Exception:
        pass

    return False


def preencher_rodada(page):
    aguardar_sair_da_tela_aguardando()

    letra = pegar_letra(page)
    letra = validar_letra_com_usuario(letra)

    if not letra:
        print("Letra não informada.")
        return False

    print(f"Letra confirmada: {letra}")

    campos = pegar_campos(page)

    if not campos:
        print("Nenhum campo encontrado.")
        return False

    print("Temas encontrados:")
    for item in campos:
        print(f"- {item['tema']}")

    for item in campos:
        if outro_player_deu_stop(page):
            print("Outro jogador deu STOP. Parando autopreenchimento.")
            confirmar_resultado(page)
            page.wait_for_timeout(2000)
            clicar_avaliar_pyautogui()
            return False

        tema = item["tema"]
        campo = item["campo"]
        container = item["container"]

        palavra = buscar_palavra(letra, tema)

        if palavra:
            print(f"[CSV] {tema}: {palavra}")
        else:
            print(f"[NÃO ENCONTRADO NO CSV] {letra} - {tema}")
            palavra = pedir_palavra_ao_usuario(letra, tema)

        if outro_player_deu_stop(page):
            print("Outro jogador deu STOP antes de preencher este campo.")
            confirmar_resultado(page)
            page.wait_for_timeout(2000)
            clicar_avaliar_pyautogui()
            return False

        if palavra:
            preenchido = preencher_campo(page, campo, container, palavra)

            if preenchido:
                print(f"Preenchido: {tema} -> {palavra}")
            else:
                print(f"Não consegui preencher o campo: {tema}")

            time.sleep(0.2)

    return True


def clicar_stop(page):
    try:
        page.get_by_role("button", name="STOP!").click(timeout=5000)

        print("Cliquei em STOP.")

        return True

    except PlaywrightTimeoutError:
        print("Botão STOP não encontrado.")
        return False

    except Exception as erro:
        print(f"Erro ao clicar em STOP: {erro}")
        return False


def confirmar_resultado(page):
    seletores = [
        lambda: page.get_by_role("button", name="OK"),
        lambda: page.get_by_text("OK")
    ]

    for seletor in seletores:
        try:
            botao = seletor()
            botao.wait_for(state="visible", timeout=10000)
            botao.click()

            print("Cliquei em OK.")

            return True

        except Exception:
            pass

    print("Botão OK não apareceu.")
    return False


def aguardar_avaliar_aparecer(timeout=30, confidence=0.90):
    if not Path(IMAGEM_AVALIAR).exists():
        print("Imagem avaliar.png não encontrada em assets.")
        return None

    print("Aguardando botão AVALIAR aparecer...")

    inicio = time.time()

    while time.time() - inicio < timeout:
        try:
            botao = pyautogui.locateCenterOnScreen(
                str(IMAGEM_AVALIAR),
                confidence=confidence
            )

            if botao:
                print("Botão AVALIAR encontrado.")
                return botao

        except Exception:
            pass

        time.sleep(1)

    print("Botão AVALIAR não apareceu dentro do tempo.")
    return None


def clicar_avaliar_pyautogui():
    botao = aguardar_avaliar_aparecer(timeout=30, confidence=0.90)

    if not botao:
        return False

    pyautogui.click(botao.x, botao.y)

    print("Cliquei em AVALIAR.")

    return True

def outro_player_deu_stop(page):
    seletores_texto = [
        "STOP AUTOMÁTICO",
        "stop automático",
        "alguém apertou stop",
        "Alguém apertou stop"
    ]

    for texto in seletores_texto:
        try:
            if page.get_by_text(texto, exact=False).first.is_visible(timeout=300):
                return True
        except Exception:
            pass

    try:
        botao_ok = page.get_by_role("button", name="OK")
        if botao_ok.is_visible(timeout=300):
            return True
    except Exception:
        pass

    try:
        botao_avaliar = page.get_by_role("button", name="AVALIAR")
        if botao_avaliar.is_visible(timeout=300):
            return True
    except Exception:
        pass

    try:
        inputs = page.locator("input, textarea, [contenteditable='true']")
        total = inputs.count()

        if total > 0:
            desabilitados = 0

            for i in range(total):
                campo = inputs.nth(i)

                try:
                    disabled = campo.get_attribute("disabled")
                    readonly = campo.get_attribute("readonly")

                    if disabled is not None or readonly is not None:
                        desabilitados += 1

                except Exception:
                    pass

            if desabilitados == total:
                return True

    except Exception:
        pass

    return False