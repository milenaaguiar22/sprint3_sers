# =========================================================
# Gestão Sustentável de Eletropostos
# Sprint 3 - Prototipagem Funcional e Integração
# =========================================================
#
# Evolução da Sprint 2: em vez de simular apenas UMA recarga
# isolada, o sistema agora integra:
#
#   - Painel solar (geração variável conforme o horário do dia)
#   - Bateria de armazenamento (guarda o excedente de energia solar)
#   - Vários eletropostos (potências diferentes)
#   - Uma lógica de automação que decide sozinha qual fonte de
#     energia usar em cada recarga (prioridade: solar > bateria > rede)
#   - Histórico das recargas guardado em memória durante a execução
#   - Relatório final com um gráfico simples feito só com texto
#
# =========================================================

import math
from datetime import datetime

# ---------- Configurações fixas do sistema ----------
CAPACIDADE_PAINEL_KW = 10.0
CAPACIDADE_BATERIA_KWH = 20.0
VALOR_KWH_REDE = 0.85

# Eletropostos disponíveis (lista de dicionários)
eletropostos = [
    {"id": 1, "nome": "Ponto Rápido", "potencia_kw": 50.0},
    {"id": 2, "nome": "Ponto Semirrápido", "potencia_kw": 22.0},
    {"id": 3, "nome": "Ponto Padrão", "potencia_kw": 7.4},
]

# Estado da bateria (começa com 50% de carga)
bateria = {
    "capacidade_kwh": CAPACIDADE_BATERIA_KWH,
    "nivel_kwh": CAPACIDADE_BATERIA_KWH * 0.5,
}

# Histórico de recargas feitas na execução atual (lista de dicionários)
historico = []


# ---------- Funções do painel solar ----------

def gerar_energia_solar(hora=None):
    """Calcula a potência solar gerada (kW) para uma hora do dia.

    Usa uma curva simples com seno: geração zero antes das 6h e depois
    das 18h, com pico ao meio-dia. Isso representa, de forma
    simplificada, como a geração solar real varia ao longo do dia.
    """
    if hora is None:
        agora = datetime.now()
        hora = agora.hour + agora.minute / 60

    if hora < 6 or hora > 18:
        return 0.0

    fator = math.sin(math.pi * (hora - 6) / 12)
    if fator < 0:
        fator = 0.0

    return round(CAPACIDADE_PAINEL_KW * fator, 2)


# ---------- Funções da bateria ----------

def carregar_bateria(kwh):
    """Coloca energia na bateria, sem ultrapassar a capacidade máxima."""
    espaco_livre = bateria["capacidade_kwh"] - bateria["nivel_kwh"]
    carregado = min(espaco_livre, kwh)
    bateria["nivel_kwh"] = bateria["nivel_kwh"] + carregado
    return carregado


def descarregar_bateria(kwh):
    """Retira energia da bateria, sem passar do que ela tem disponível."""
    fornecido = min(bateria["nivel_kwh"], kwh)
    bateria["nivel_kwh"] = bateria["nivel_kwh"] - fornecido
    return fornecido


def nivel_bateria_pct():
    return round((bateria["nivel_kwh"] / bateria["capacidade_kwh"]) * 100, 1)


# ---------- Funções dos eletropostos ----------

def listar_eletropostos():
    print("\nEletropostos disponíveis:")
    for e in eletropostos:
        print(f"{e['id']} - {e['nome']} ({e['potencia_kw']} kW)")


def buscar_eletroposto(id_escolhido):
    for e in eletropostos:
        if e["id"] == id_escolhido:
            return e
    return None


# ---------- Status e relatório ----------

def mostrar_status():
    geracao = gerar_energia_solar()
    print("\n====== STATUS DO SISTEMA ======")
    print(f"Horário atual: {datetime.now().strftime('%H:%M')}")
    print(f"Geração solar atual: {geracao:.2f} kW")
    print(
        f"Nível da bateria: {nivel_bateria_pct()}% "
        f"({bateria['nivel_kwh']:.2f}/{bateria['capacidade_kwh']:.2f} kWh)"
    )


def mostrar_barra(nome, valor, total):
    """Mostra uma barrinha de texto proporcional ao valor (gráfico simples)."""
    if total > 0:
        tamanho = int((valor / total) * 40)
    else:
        tamanho = 0
    barra = "#" * tamanho
    print(f"{nome:8s} | {barra} {valor:.1f} kWh")


def gerar_relatorio():
    if len(historico) == 0:
        print("\nNenhuma recarga foi simulada ainda.")
        return

    total_energia = 0
    total_solar = 0
    total_bateria = 0
    total_rede = 0
    total_custo = 0

    for sessao in historico:
        total_energia = total_energia + sessao["energia_kwh"]
        total_solar = total_solar + sessao["solar_kwh"]
        total_bateria = total_bateria + sessao["bateria_kwh"]
        total_rede = total_rede + sessao["rede_kwh"]
        total_custo = total_custo + sessao["custo_rs"]

    if total_energia > 0:
        perc_medio = round(((total_solar + total_bateria) / total_energia) * 100, 1)
    else:
        perc_medio = 0

    print("\n====== RELATÓRIO GERAL ======")
    print(f"Sessões registradas: {len(historico)}")
    print(f"Energia total: {total_energia:.2f} kWh")
    print(f"  Solar:   {total_solar:.2f} kWh")
    print(f"  Bateria: {total_bateria:.2f} kWh")
    print(f"  Rede:    {total_rede:.2f} kWh")
    print(f"Custo total: R$ {total_custo:.2f}")
    print(f"Participação renovável média: {perc_medio}%")

    print("\nDistribuição de energia por fonte:")
    mostrar_barra("Solar", total_solar, total_energia)
    mostrar_barra("Bateria", total_bateria, total_energia)
    mostrar_barra("Rede", total_rede, total_energia)


# ---------- Simulação de recarga ----------

def simular_recarga(hora_simulada=None):
    listar_eletropostos()

    try:
        escolha = int(input("Escolha o eletroposto (1-3): "))
    except ValueError:
        print("Opção inválida.")
        return

    estacao = buscar_eletroposto(escolha)
    if estacao is None:
        print("Eletroposto inválido.")
        return

    try:
        tempo = float(input("Tempo de carregamento (horas): "))
    except ValueError:
        print("Tempo inválido.")
        return

    energia_necessaria = tempo * estacao["potencia_kw"]

    geracao_kw = gerar_energia_solar(hora_simulada)
    solar_disponivel = geracao_kw * tempo

    # -----------------------------------------------------
    # Lógica de automação: decide a combinação de fontes
    # prioridade: solar -> bateria -> rede elétrica
    # -----------------------------------------------------
    if solar_disponivel >= energia_necessaria:
        solar_usado = energia_necessaria
        excedente = solar_disponivel - energia_necessaria
        carregar_bateria(excedente)
        bateria_usada = 0.0
        rede_usada = 0.0
    else:
        solar_usado = solar_disponivel
        faltante = energia_necessaria - solar_usado
        bateria_usada = descarregar_bateria(faltante)
        faltante = faltante - bateria_usada
        rede_usada = faltante

    custo = rede_usada * VALOR_KWH_REDE

    if energia_necessaria > 0:
        perc_renovavel = round(((solar_usado + bateria_usada) / energia_necessaria) * 100, 1)
    else:
        perc_renovavel = 0

    print("\n====== RESULTADO DA RECARGA ======")
    print(f"Estação: {estacao['nome']} ({estacao['potencia_kw']} kW)")
    print(f"Tempo de carregamento: {tempo:.1f} horas")
    print(f"Energia total consumida: {energia_necessaria:.2f} kWh")
    print(f"  -> Solar:   {solar_usado:.2f} kWh")
    print(f"  -> Bateria: {bateria_usada:.2f} kWh")
    print(f"  -> Rede:    {rede_usada:.2f} kWh")
    print(f"Custo estimado: R$ {custo:.2f}")
    print(f"Participação renovável nesta recarga: {perc_renovavel}%")
    print(f"Nível da bateria após a recarga: {nivel_bateria_pct()}%")

    # Guarda os dados dessa recarga no histórico (em memória)
    sessao = {
        "estacao": estacao["nome"],
        "tempo_h": tempo,
        "energia_kwh": energia_necessaria,
        "solar_kwh": solar_usado,
        "bateria_kwh": bateria_usada,
        "rede_kwh": rede_usada,
        "custo_rs": custo,
        "perc_renovavel": perc_renovavel,
    }
    historico.append(sessao)


# ---------- Programa principal ----------

def main():
    print("===================================")
    print(" GESTÃO SUSTENTÁVEL DE ELETROPOSTOS ")
    print("       Sprint 3 - Integração        ")
    print("===================================")

    while True:
        print("\nMENU")
        print("1 - Simular recarga")
        print("2 - Ver status do sistema (solar + bateria)")
        print("3 - Gerar relatório")
        print("4 - Simular recarga em horário personalizado (teste)")
        print("5 - Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            simular_recarga()
        elif opcao == "2":
            mostrar_status()
        elif opcao == "3":
            gerar_relatorio()
        elif opcao == "4":
            try:
                hora = float(input("Informe a hora do dia para simular (0-23): "))
            except ValueError:
                print("Hora inválida.")
                continue
            simular_recarga(hora_simulada=hora)
        elif opcao == "5":
            print("\nEncerrando sistema...")
            print("Obrigado por utilizar o sistema!")
            break
        else:
            print("\nOpção inválida! Tente novamente.")


if __name__ == "__main__":
    main()