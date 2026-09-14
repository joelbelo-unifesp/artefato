"""Interface de linha de comando do FIGOV.

Comandos:
    run       — executa o pipeline completo sobre um conjunto de configs.
    comparar  — compara alternativas de planejamento (RF-07).
    validar   — executa o protocolo de validação (RF-05).

Uso:
    PYTHONPATH=src python -m figov.cli run --vertiporto config/vertiporto_A.json \
        --vertiporto config/vertiporto_B.json --frota config/frota.json \
        --seguranca config/seguranca.json --cenario config/cenario.json
"""

from __future__ import annotations

import argparse
import copy
import json
import sys

from .io import loader
from .io.demanda_gen import gerar_demanda
from . import pipeline as pipe
from .models import validacao as val


def _montar_config(args, *, nome: str, frota: dict | None = None) -> pipe.ConfiguracaoCenario:
    vertiportos = {}
    for vp_path in args.vertiporto:
        vp = loader.load_vertiporto(vp_path)
        vertiportos[vp["id"]] = vp
    if not vertiportos:
        raise SystemExit("Erro: informe ao menos um --vertiporto.")

    frota = frota if frota is not None else loader.load_frota(args.frota)
    seguranca = loader.load_seguranca(args.seguranca)
    cenario = loader.load_cenario(args.cenario)

    if args.demanda:
        demanda = loader.load_demanda(args.demanda)
    else:
        demanda = gerar_demanda(
            list(vertiportos.keys()),
            seed=cenario["seed"],
            n_movimentos=args.n_movimentos,
        )

    return pipe.ConfiguracaoCenario(
        nome=nome,
        vertiportos=vertiportos,
        frota=frota,
        demanda=demanda,
        seguranca=seguranca,
        atraso_aceitavel_min=cenario.get("atraso_aceitavel_min", 5.0),
        desvio_capacidade_max_pct=cenario.get("desvio_capacidade_max_pct", 10.0),
        replicas_referencia=cenario.get("replicas_referencia", 10),
        seed=cenario["seed"],
    )


def _add_config_args(p: argparse.ArgumentParser, *, exige_vertiporto=True) -> None:
    p.add_argument("--vertiporto", action="append", default=[],
                   help="Caminho de config de vertiporto (repetível).")
    p.add_argument("--frota", default="config/frota.json")
    p.add_argument("--seguranca", default="config/seguranca.json")
    p.add_argument("--cenario", default="config/cenario.json")
    p.add_argument("--demanda", default=None,
                   help="Caminho de demanda JSON; se omitido, gera determinística.")
    p.add_argument("--n-movimentos", type=int, default=300, dest="n_movimentos")


def cmd_run(args) -> int:
    cfg = _montar_config(args, nome="run")
    res = pipe.executar(cfg)
    print(json.dumps(res.to_dict(), ensure_ascii=False, indent=2))
    return 0


def cmd_comparar(args) -> int:
    # se não houver vertiportos passados, usa os dois exemplos
    if not args.vertiporto:
        args.vertiporto = ["config/vertiporto_A.json", "config/vertiporto_B.json"]
    base = _montar_config(args, nome="base")
    # alternativa: frota dobrada (demonstra RF-07)
    frota_2x = copy.deepcopy(base.frota)
    for a in frota_2x["aeronaves"]:
        a["quantidade"] = a.get("quantidade", 1) * 2
    alt = _montar_config(args, nome="frota_2x", frota=frota_2x)
    alt.demanda = base.demanda  # mesma demanda para comparação justa
    comp = pipe.comparar_cenarios([base, alt])
    print(json.dumps(comp.to_dict(), ensure_ascii=False, indent=2))
    return 0


def cmd_validar(args) -> int:
    if not args.vertiporto:
        args.vertiporto = ["config/vertiporto_A.json", "config/vertiporto_B.json"]
    base = _montar_config(args, nome="base")
    frota_menor = copy.deepcopy(base.frota)
    for a in frota_menor["aeronaves"]:
        a["quantidade"] = max(1, a.get("quantidade", 1) // 2)
    alt = _montar_config(args, nome="frota_reduzida", frota=frota_menor)
    alt.demanda = base.demanda
    rel = val.executar_protocolo([base, alt], living_lab_disponivel=args.living_lab)
    print(json.dumps(rel.to_dict(), ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="figov", description="FIGOV — protótipo computacional")
    sub = parser.add_subparsers(dest="comando", required=True)

    p_run = sub.add_parser("run", help="executa o pipeline completo")
    _add_config_args(p_run)
    p_run.set_defaults(func=cmd_run)

    p_cmp = sub.add_parser("comparar", help="compara alternativas de planejamento (RF-07)")
    _add_config_args(p_cmp)
    p_cmp.set_defaults(func=cmd_comparar)

    p_val = sub.add_parser("validar", help="executa o protocolo de validação (RF-05)")
    _add_config_args(p_val)
    p_val.add_argument("--living-lab", action="store_true", dest="living_lab",
                       help="marca dados reais do Living Lab como disponíveis.")
    p_val.set_defaults(func=cmd_validar)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
