# Military / Research Expansion — dry-run

- **Execução:** 2026-05-20T06:00:48Z
- **Apply:** não

## Por fonte

| Fonte | Destino | Raw | Std | Válidos | Review | Desc. | Recomendação |
|-------|---------|-----|-----|---------|--------|-------|--------------|
| afrl_technology_areas | pesquisa | 12 | 12 | 12 | 0 | 0 | `apply_controlado` |
| arl_news | noticia | 12 | 12 | 12 | 0 | 0 | `apply_controlado` |
| arl_resources | pesquisa | 20 | 20 | 20 | 2 | 0 | `apply_controlado` |
| afnwc_innovation | pesquisa | 4 | 4 | 4 | 0 | 0 | `precisa_melhoria` |
| afnwc_weapon_systems | pesquisa | 1 | 1 | 1 | 0 | 0 | `precisa_melhoria` |
| space_force_news | noticia | 30 | 28 | 18 | 2 | 0 | `apply_controlado` |
| afnwc_news | noticia | 0 | 0 | 0 | 0 | 0 | `nao_recomendado` |
| afmc_news | noticia | 30 | 9 | 0 | 0 | 21 | `latente` |

## Diagnóstico HTTP (live, browser UA)

- https://www.afmc.af.mil/News/: status=403 bytes=380
- https://www.afnwc.af.mil/News/: status=403 bytes=383
- https://www.spaceforce.mil/News/: status=403 bytes=379
- https://afresearchlab.com/technology/: status=200 bytes=133180
- https://arl.devcom.army.mil/media-center/: status=200 bytes=234402
- https://arl.devcom.army.mil/resources/: status=200 bytes=208451