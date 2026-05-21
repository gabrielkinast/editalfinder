-- sql_updates_sugeridos.sql (audit_editais_visibility_noise.py)
-- REVISAR ANTES DE EXECUTAR. Não deleta linhas.
-- generated=2026-05-20T22:39:58Z rule=editais_visibility_v1

-- id_edital=2102 | visible_recent_strong_signal | Dispensa de Licitação 03/2024
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2102;

-- id_edital=2097 | review_missing_deadline | FNO Amazônia Empresarial
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 2097;

-- id_edital=2096 | review_missing_deadline | FNO Amazônia Rural
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 2096;

-- id_edital=2095 | review_missing_deadline | Linhas de Fomento
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 2095;

-- id_edital=2071 | visible_recent_strong_signal | Funding finder
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2071;

-- id_edital=2070 | review_missing_deadline | RSS feed
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 2070;

-- id_edital=2069 | visible_recent_strong_signal | Funding opportunity: Contracts for Innovation: Cyber scale in critical sectors
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2069;

-- id_edital=2068 | visible_recent_strong_signal | Funding opportunity: Experimental medicine stage one
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2068;

-- id_edital=2067 | visible_recent_strong_signal | Funding opportunity: Environmental sciences: Global Partnerships Seedcorn Fund 2
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2067;

-- id_edital=2066 | hidden_institutional | Funding opportunity: BBSRC new investigator award: applicant-led mode
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 2066;

-- id_edital=2065 | visible_recent_strong_signal | Funding opportunity: BBSRC standard research grant: applicant-led mode
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2065;

-- id_edital=2064 | visible_recent_strong_signal | Funding opportunity: Particle Physics Experiment Consolidated Grants 2026
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2064;

-- id_edital=2063 | visible_recent_strong_signal | Funding opportunity: National Materials Innovation Programme: Feasibility studie
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2063;

-- id_edital=2062 | visible_recent_strong_signal | Funding opportunity: Dual-use aviation systems and autonomy
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2062;

-- id_edital=2061 | visible_recent_strong_signal | Funding opportunity: Centre for Quantum Commercialisation Skills
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2061;

-- id_edital=2060 | visible_recent_strong_signal | Funding opportunity: Battery Innovation Programme: battery skills initiatives
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2060;

-- id_edital=2059 | review_missing_deadline | OSIP
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 2059;

-- id_edital=2058 | visible_recent_strong_signal | Open Discovery Ideas Channel
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2058;

-- id_edital=2057 | visible_continuous_flow | ARTES COMPETITIVENESS & GROWTH - CALL FOR OUTLINE PROPOSALS
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_continuous_flow", "reason": "Fluxo contínuo ou chamada permanente.", "confidence": "alta", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["continuous_flow"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2057;

-- id_edital=2056 | visible_recent_strong_signal | Competitiveness Segment of the Space Safety Programme
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2056;

-- id_edital=2055 | visible_recent_strong_signal | Civil Security from Space programme - Open Call for Proposals
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2055;

-- id_edital=2054 | visible_recent_strong_signal | The ESA Marketplace
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2054;

-- id_edital=2053 | visible_recent_strong_signal | Visiting researchers – access to ESA labs and expertise for your research projec
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2053;

-- id_edital=2052 | visible_recent_strong_signal | GSTP Element 1 - Building Blocks Framework
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2052;

-- id_edital=2051 | visible_recent_strong_signal | GSTP Element 1 - De-Risk, Advanced Manufacturing & Quantum Technology Frameworks
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2051;

-- id_edital=2050 | visible_recent_strong_signal | NAVISP Element 2: Competitiveness
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2050;

-- id_edital=2049 | visible_recent_strong_signal | PNT Competitiveness - NAVISP Element 2
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2049;

-- id_edital=2048 | hidden_historical | Celeste In-Orbit Demonstrator – Call for LEO-PNT experimentation opportunities
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 2048;

-- id_edital=2047 | visible_recent_strong_signal | European Space for Sustainability Award 2026
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2047;

-- id_edital=2046 | hidden_expired | Call for Inter-Disciplinary Scientists and Guest Investigators for TGO
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 2046;

-- id_edital=2045 | visible_recent_strong_signal | Announcement of Opportunity: Science opportunities on Uncrewed Autonomous Free F
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2045;

-- id_edital=2044 | hidden_historical | INDustrialisation / Serialisation Support Campaign
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 2044;

-- id_edital=2043 | visible_recent_strong_signal | Open Discovery Ideas Channel
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2043;

-- id_edital=2042 | visible_recent_strong_signal | Urban Mobility Explained (UMX) Open Call
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2042;

-- id_edital=2041 | hidden_historical | InnoNext Call
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 2041;

-- id_edital=2040 | hidden_historical | Citizens on the Move 2026
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 2040;

-- id_edital=2039 | visible_recent_strong_signal | EIT EdTech Conference Open Call
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2039;

-- id_edital=2038 | visible_recent_strong_signal | Strategic Innovation Open Call
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2038;

-- id_edital=2037 | hidden_institutional | Venture Incubation Program
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 2037;

-- id_edital=2036 | hidden_historical | Women2Invest
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 2036;

-- id_edital=2035 | visible_recent_strong_signal | Scaleup Promotion Initiative Open Call
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2035;

-- id_edital=2034 | hidden_historical | EIT Jumpstarter 2026
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 2034;

-- id_edital=2033 | visible_recent_strong_signal | ClimateLaunchpad 2026
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2033;

-- id_edital=2032 | visible_recent_strong_signal | NEB Mentors - Open Call 2026
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2032;

-- id_edital=2031 | review_missing_deadline | Other Calls and Notices
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 2031;

-- id_edital=2030 | review_missing_deadline | Open Calls
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 2030;

-- id_edital=2029 | review_missing_deadline | EIT Culture & Creativity
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 2029;

-- id_edital=2028 | hidden_institutional | EIT Water
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 2028;

-- id_edital=2027 | visible_recent_strong_signal | Call for EIT Knowledge and Innovation Communities
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 2027;

-- id_edital=1868 | visible_recent_strong_signal | 国家重点研发计划：“政府间国际科技创新合作”重点专项2026年度...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1868;

-- id_edital=1860 | visible_recent_strong_signal | Funding & Support
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1860;

-- id_edital=1859 | review_missing_deadline | Funding & Support
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1859;

-- id_edital=1858 | visible_recent_strong_signal | Funding & Support
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1858;

-- id_edital=1857 | visible_recent_strong_signal | Chinese Researchers Achieve Key Prog...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1857;

-- id_edital=1854 | visible_recent_strong_signal | Funding & Support
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1854;

-- id_edital=1851 | review_missing_deadline | 资助成果
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1851;

-- id_edital=1850 | review_missing_deadline | 第436期双清论坛“奔向空天的生命科学研究”在西安召开 11-03
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1850;

-- id_edital=1849 | review_missing_deadline | 第435期双清论坛“脑化学研究的机遇与挑战”召开 11-05
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1849;

-- id_edital=1848 | review_missing_deadline | 第438期双清论坛（青年）“数学学科青年人才的成长路径”召开 11-05
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1848;

-- id_edital=1847 | review_missing_deadline | 第442期双清论坛“人工智能与中医药传承创新”在珠海召开 01-29
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1847;

-- id_edital=1846 | visible_recent_strong_signal | 我国学者与海外合作者实现多尺度光学超材料规模打印创制 05-07 05-07
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:56Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1846;

-- id_edital=1845 | visible_recent_strong_signal | 我国学者在量子点超晶格及高清显示应用方面取得新进展 05-07
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1845;

-- id_edital=1844 | review_missing_deadline | > 资助期限
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1844;

-- id_edital=1843 | review_missing_deadline | 科学基金网络信息系统 NSFC
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1843;

-- id_edital=1837 | review_missing_deadline | 关于2026年第一季度国家自然科学基金委员会政府网站与政务新媒体抽查情况的通报 04-15
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1837;

-- id_edital=1836 | review_missing_deadline | 【人民日报】强化战略布局 筑牢创新根基（“十五五”开好局起好步） 05-06 05-06
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1836;

-- id_edital=1835 | visible_recent_strong_signal | 自然科学基金委党组传达学习习近平总书记在加强基础研究座谈会上的重要讲话精神 05-06 05-06
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1835;

-- id_edital=1834 | review_missing_deadline | 【新华社】习近平对国家自然科学基金委员会工作作出重要指示 02-12 02-12
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1834;

-- id_edital=1833 | review_missing_deadline | 2026年度浙江、安徽、江西、湖北、湖南五省国家自然科学基金项目资金监督检查进场会在杭州召开
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1833;

-- id_edital=1832 | review_missing_deadline | 国家自然科学基金委员会召开2026年项目评审工作动员部署会议
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1832;

-- id_edital=1831 | review_missing_deadline | 习近平对国家自然科学基金委员会工作作出重要指示
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1831;

-- id_edital=1820 | visible_recent_strong_signal | 科技部召开党组理论学习中心组学习（扩大）会议暨科技部安全生产委员会2026年第一次全体会议
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1820;

-- id_edital=1814 | hidden_historical | 中国共产党德钦县委员会机构编...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1814;

-- id_edital=1813 | hidden_historical | 全国各部门及地方机电进出口办公室
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1813;

-- id_edital=1812 | hidden_historical | 中国邮政储蓄银行广西区分行20...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1812;

-- id_edital=1811 | hidden_historical | 云南文化艺术职业学院（云南省...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1811;

-- id_edital=1810 | hidden_historical | 【缙云县天然气有限公司2026-2...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1810;

-- id_edital=1809 | hidden_historical | 2026年房产超市运营营销活动和...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1809;

-- id_edital=1808 | hidden_historical | 特种光纤设计仿真分析软件招标...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1808;

-- id_edital=1807 | hidden_historical | 法国开发署贷款陕西省宝鸡市凤...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1807;

-- id_edital=1806 | hidden_historical | 自动钻铆离线编程软件评标结果...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1806;

-- id_edital=1805 | hidden_historical | 中国投资有限责任公司法律服务...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1805;

-- id_edital=1804 | hidden_historical | 2521120008-A和B(重新招标） ...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1804;

-- id_edital=1803 | hidden_historical | 华润水泥(贵港)有限公司2026年...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1803;

-- id_edital=1802 | hidden_historical | 广西电网公司2026年第一批基建...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1802;

-- id_edital=1801 | hidden_historical | 辽宁轻工职业学院智慧财商虚拟...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1801;

-- id_edital=1798 | hidden_historical | 从地方购买服务项目（第三片区...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1798;

-- id_edital=1795 | hidden_historical | 南网超高压公司2026年第一批物...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1795;

-- id_edital=1794 | hidden_historical | 昆明医科大学第二附属医院关于...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1794;

-- id_edital=1793 | hidden_historical | 海油发展-清洁能源公司2026-20...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1793;

-- id_edital=1792 | hidden_historical | H050400366 笔记本内存/三星/3...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1792;

-- id_edital=1791 | hidden_historical | 【中国邮政集团有限公司云南省...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1791;

-- id_edital=1789 | hidden_historical | 唐山市路南区教育局本级城南九...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1789;

-- id_edital=1786 | hidden_historical | 新源劲吾(北京)科技有限公司碳...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1786;

-- id_edital=1783 | hidden_historical | 2025年公路运输框架协议公路运...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1783;

-- id_edital=1782 | hidden_historical | 青海大学校园基础设施更新和节...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1782;

-- id_edital=1781 | hidden_historical | 格尔木污水处理厂南部片区中水...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1781;

-- id_edital=1780 | hidden_historical | 中国新兴建设一公司中国电子科...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1780;

-- id_edital=1779 | hidden_historical | 郑州航空港经济综合实验区农事...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1779;

-- id_edital=1778 | hidden_historical | 昌宁县职业技术学校实训工位建...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1778;

-- id_edital=1775 | hidden_historical | 甘肃河西走廊（张掖）公共卫生...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1775;

-- id_edital=1772 | hidden_historical | [遂川县]遂川县新江乡横石村“...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1772;

-- id_edital=1769 | hidden_historical | 福建海辰化学(漳州)己二腈及原...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1769;

-- id_edital=1767 | hidden_historical | 大连太平湾临港产业项目指挥部...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1767;

-- id_edital=1760 | hidden_historical | 湟水河河湟新区段北岸防洪生态...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1760;

-- id_edital=1759 | hidden_historical | 江西省世界银行贷款预防准备和...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1759;

-- id_edital=1757 | hidden_historical | 涂胶显影机采购中标结果公告(1)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1757;

-- id_edital=1756 | hidden_historical | 晶圆级原子力显微镜中标结果公告(1)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1756;

-- id_edital=1755 | hidden_historical | 快速成像高分辨原子力显微镜中标结果公告(1)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1755;

-- id_edital=1754 | hidden_historical | 南通深南电路有限公司项目-垂直连续电镀机【重新招...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1754;

-- id_edital=1753 | hidden_historical | 重庆工具厂有限责任公司一批设备采购(第二次）（分...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1753;

-- id_edital=1752 | hidden_historical | 极端环境微纳米力学综合测试系统中标结果公告(1)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1752;

-- id_edital=1751 | hidden_historical | 京东方第8.6代AMOLED生产线项目重新招标澄清或变更...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1751;

-- id_edital=1750 | hidden_duplicate | 京东方第8.6代AMOLED生产线项目重新招标澄清或变更...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1750;

-- id_edital=1749 | hidden_duplicate | 京东方第8.6代AMOLED生产线项目重新招标澄清或变更...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1749;

-- id_edital=1748 | hidden_duplicate | 京东方第8.6代AMOLED生产线项目重新招标澄清或变更...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1748;

-- id_edital=1747 | hidden_duplicate | 京东方第8.6代AMOLED生产线项目重新招标澄清或变更...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1747;

-- id_edital=1746 | hidden_historical | 离子束刻蚀系统国际招标澄清或变更公告(3)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1746;

-- id_edital=1745 | hidden_historical | 上海新材料研究院 X射线衍射仪国际招标澄清或变更公...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1745;

-- id_edital=1744 | hidden_historical | 南通深南电路有限公司项目-真空塞孔机【重新招标】...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1744;

-- id_edital=1743 | hidden_historical | 无锡深南电路有限公司项目-三次元测量仪【重新招标...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1743;

-- id_edital=1742 | hidden_historical | 无锡深南电路有限公司项目-退膜机【重新招标】评标...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1742;

-- id_edital=1741 | hidden_historical | 上海交通大学高精度二维材料表面综合表征与处理系统...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1741;

-- id_edital=1740 | hidden_institutional | 2026年5月上旬国防部例行新闻发布
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1740;

-- id_edital=1739 | hidden_duplicate | 2026年5月上旬国防部例行新闻发布
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1739;

-- id_edital=1727 | review_missing_deadline | 中广核广东太平岭核电厂2号机组首次核燃料装载工作圆满完...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1727;

-- id_edital=1726 | review_missing_deadline | 中广核能源国际韩国大山二期项目完成燃气轮机首次点火
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1726;

-- id_edital=1718 | review_missing_deadline | “虚拟宇宙”模拟暗能量与暗物质神秘角力
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1718;

-- id_edital=1712 | review_missing_deadline | 【科技日报】我国科研团队实现14.5公里远距离“物质纠缠”
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1712;

-- id_edital=1711 | review_missing_deadline | 【人民日报】研究团队把生物防伪“写进”材料本体
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1711;

-- id_edital=1682 | hidden_institutional | Fundos de investimento em empresas e projetos
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1682;

-- id_edital=1680 | hidden_resultado | Chamada Pública BNDES Fundo Mercado de Acesso
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1680;

-- id_edital=1678 | hidden_historical | Fundos da série Criatec
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1678;

-- id_edital=1676 | hidden_institutional | Seleção de Gestor do Fundo Nordeste
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1676;

-- id_edital=1674 | review_missing_deadline | Seleção de Fundo nos setores aeroespacial, aeronáutico, de defesa e de segurança
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1674;

-- id_edital=1672 | hidden_resultado | Primeira Chamada Multissetorial para a Seleção de Fundos de Investimento
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1672;

-- id_edital=1670 | hidden_institutional | Seleção de Gestor Nacional do Fundo Criatec III
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1670;

-- id_edital=1668 | hidden_resultado | Segunda Chamada Multissetorial para a Seleção de Fundos de Investimento
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1668;

-- id_edital=1666 | hidden_resultado | Seleção de fundos de crédito para Pequenas e Médias Empresas Inovadoras
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1666;

-- id_edital=1664 | hidden_historical | Seleção de gestor do Fundo de Energia Sustentável
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1664;

-- id_edital=1662 | hidden_historical | Seleção de gestor do FIDC Debêntures de Infraestrutura
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1662;

-- id_edital=1661 | hidden_resultado | Seleção de Instituição Financeira para Coordenar, Estruturar e Distribuir as cot
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1661;

-- id_edital=1659 | hidden_resultado | Seleção de Fundo de Investimento em Participações no setor de Internet das Coisa
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1659;

-- id_edital=1657 | hidden_resultado | Chamada Pública para seleção de fundos de investimento em participações – Capita
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1657;

-- id_edital=1655 | review_missing_deadline | Chamada Pública para Seleção de Gestor para Fundo de Investimento em Participaçõ
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1655;

-- id_edital=1653 | review_missing_deadline | Chamada Pública para Seleção de Fundo de Investimento em Participações no Comple
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1653;

-- id_edital=1652 | hidden_resultado | Chamada Pública para Seleção de Fundos com Foco em Mitigação Climática - Chamada
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1652;

-- id_edital=1650 | review_missing_deadline | Chamada Pública para Seleção de Fundos de Investimento em Índice de Mercado – Fu
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1650;

-- id_edital=1648 | review_missing_deadline | Chamada Pública para Seleção de Fundo de Investimento em Participações de Startu
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1648;

-- id_edital=1559 | hidden_historical | licitações e contratos
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1559;

-- id_edital=1558 | hidden_historical | IAra Global Encontre mercados para exportação e muito mais com a IAra. É simples
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1558;

-- id_edital=1471 | review_missing_deadline | JavaScript is disabled
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1471;

-- id_edital=1470 | hidden_duplicate | JavaScript is disabled
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1470;

-- id_edital=1469 | hidden_duplicate | JavaScript is disabled
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1469;

-- id_edital=1468 | hidden_duplicate | JavaScript is disabled
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1468;

-- id_edital=1467 | hidden_duplicate | JavaScript is disabled
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1467;

-- id_edital=1466 | visible_recent_strong_signal | Funded grants
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1466;

-- id_edital=1465 | visible_recent_strong_signal | Funding portfolio: funded people and projects
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1465;

-- id_edital=1464 | visible_recent_strong_signal | Funding policies and grant conditions
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1464;

-- id_edital=1463 | visible_recent_strong_signal | Prepare to apply
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1463;

-- id_edital=1462 | review_missing_deadline | Find a funding opportunity
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1462;

-- id_edital=1461 | visible_recent_strong_signal | Research funding
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1461;

-- id_edital=1460 | review_missing_deadline | Thales Security Requirements - Purchasing
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1460;

-- id_edital=1459 | review_missing_deadline | Supplier Relations | Thales Group
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1459;

-- id_edital=1458 | review_missing_deadline | Softex e CAIXA lançam Programa Amazônia Geek para capacitar jovens e mulheres em
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1458;

-- id_edital=1457 | review_missing_deadline | Inscrições abertas para o Amazônia Geek, programa de formação de talentos em gam
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1457;

-- id_edital=1456 | review_missing_deadline | Fomento à Pesquisa em Saúde
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1456;

-- id_edital=1455 | review_missing_deadline | Rheinmetall procurement portal
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1455;

-- id_edital=1454 | review_missing_deadline | Become a supplier
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1454;

-- id_edital=1453 | review_missing_deadline | Regulamento Seleção Pública 2023.1 – Projetos Não Incentivados
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1453;

-- id_edital=1452 | review_missing_deadline | Regulamento Seleção Pública 2023.1 – Projetos Incentivados
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1452;

-- id_edital=1451 | hidden_historical | Inscrições Projetos Incentivados
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1451;

-- id_edital=1450 | hidden_historical | Inscrições Projetos Não Incentivados
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1450;

-- id_edital=1449 | hidden_institutional | Convênios e Transferências
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1449;

-- id_edital=1448 | hidden_institutional | Auditorias
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1448;

-- id_edital=1447 | hidden_institutional | Paticipação Social
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1447;

-- id_edital=1446 | hidden_institutional | Institucional
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1446;

-- id_edital=1445 | hidden_institutional | Segmento de Óleo & Gás
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1445;

-- id_edital=1444 | hidden_institutional | Segmento de Energia
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1444;

-- id_edital=1443 | hidden_institutional | Segmento Nuclear
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1443;

-- id_edital=1442 | hidden_institutional | Segmento de Defesa
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1442;

-- id_edital=1441 | hidden_institutional | Organograma
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1441;

-- id_edital=1440 | hidden_institutional | Diretoria Industrial
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1440;

-- id_edital=1439 | hidden_institutional | Diretoria Comercial
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1439;

-- id_edital=1438 | hidden_institutional | Diretoria Administrativa
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1438;

-- id_edital=1437 | hidden_institutional | Presidência da empresa
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1437;

-- id_edital=1436 | hidden_institutional | Sala Limpa
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1436;

-- id_edital=1435 | hidden_institutional | Centro de Treinamento
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1435;

-- id_edital=1434 | hidden_institutional | Terminal Portuário
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1434;

-- id_edital=1433 | hidden_institutional | Expertise
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1433;

-- id_edital=1432 | hidden_expired | Quem Somos
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Registro marcado ativo=false.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["ativo_false"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1432;

-- id_edital=1431 | hidden_institutional | Página Inicial
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1431;

-- id_edital=1430 | hidden_institutional | NUCLEP
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1430;

-- id_edital=1429 | review_missing_deadline | Site Map
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1429;

-- id_edital=1428 | visible_recent_strong_signal | Exit Disclaimer
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1428;

-- id_edital=1427 | visible_recent_strong_signal | Accessibility & Compliance
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1427;

-- id_edital=1426 | review_missing_deadline | XML EXTRACT
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1426;

-- id_edital=1425 | review_missing_deadline | Alerts
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1425;

-- id_edital=1424 | hidden_institutional | YouTube
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1424;

-- id_edital=1423 | review_missing_deadline | JavaScript is not available.
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1423;

-- id_edital=1422 | review_missing_deadline | “How to…” Blog Series
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1422;

-- id_edital=1421 | visible_recent_strong_signal | Help Page Content
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1421;

-- id_edital=1420 | review_missing_deadline | Search Site Content
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1420;

-- id_edital=1419 | hidden_expired | NATO DIANA — Programme FAQ (challenges, eligibility, portal)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Registro marcado ativo=false.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["ativo_false"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1419;

-- id_edital=1418 | hidden_institutional | Decision Superiority for NATO Warfighters — DIANA challenge call
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1418;

-- id_edital=1417 | review_missing_deadline | Editais de Chamamento Público
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1417;

-- id_edital=1416 | hidden_duplicate | Editais de Chamamento Público
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1416;

-- id_edital=1415 | hidden_historical | EDITAL CHAMAMENTO PÚBLICO Nº 11, DE 15 DE JUNHO DE 2021
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1415;

-- id_edital=1414 | hidden_historical | EDITAL Nº 17/2021/MCTI - PROCESSO DE ESCOLHA NOVO DIRETOR MAST/MCTI
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1414;

-- id_edital=1413 | hidden_historical | EDITAL Nº 18/2021/MCTI - PROCESSO DE ESCOLHA NOVO DIRETOR OBSERVATÓRIO NACIONAL/
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1413;

-- id_edital=1412 | review_missing_deadline | MAPA - Página de Editais e Programas
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1412;

-- id_edital=1411 | review_missing_deadline | Webinars & Programs
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1411;

-- id_edital=1410 | review_missing_deadline | Supplier Documentation
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1410;

-- id_edital=1409 | hidden_historical | Small Business Programs
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1409;

-- id_edital=1408 | review_missing_deadline | Supplier Ethics
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1408;

-- id_edital=1407 | review_missing_deadline | Cybersecurity
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1407;

-- id_edital=1406 | review_missing_deadline | Small Business Innovation Research
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1406;

-- id_edital=1405 | review_missing_deadline | Business Area Procurement
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1405;

-- id_edital=1404 | review_missing_deadline | Doing Business
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1404;

-- id_edital=1403 | review_missing_deadline | Defense Technology Innovation
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1403;

-- id_edital=1402 | review_missing_deadline | Strategic and Missile Defense Systems
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1402;

-- id_edital=1401 | review_missing_deadline | Infrared and Advanced Sensor Technology
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1401;

-- id_edital=1400 | review_missing_deadline | Integrated Air and Missile Defense
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1400;

-- id_edital=1399 | review_missing_deadline | Electronic Warfare, Deterrence and Protection
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1399;

-- id_edital=1398 | review_missing_deadline | C4ISR All-Domain Battle Management System
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1398;

-- id_edital=1397 | hidden_historical | Military and Veteran Support
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1397;

-- id_edital=1396 | review_missing_deadline | Suppliers
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1396;

-- id_edital=1395 | review_missing_deadline | RIKEN Center for Advanced Photonics (RAP)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1395;

-- id_edital=1394 | review_missing_deadline | RIKEN Center for Sustainable Resource Science (CSRS)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1394;

-- id_edital=1393 | review_missing_deadline | RIKEN Information R&D Strategy Headquarters (R-IH)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1393;

-- id_edital=1392 | review_missing_deadline | Chief Scientist Laboratories etc
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1392;

-- id_edital=1391 | review_missing_deadline | RIKEN Baton Zone Program (BZP)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1391;

-- id_edital=1390 | review_missing_deadline | RIKEN Industrial Co-creation Program (ICoP)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1390;

-- id_edital=1389 | review_missing_deadline | Advanced Semiconductor Science Program (ASSP)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1389;

-- id_edital=1388 | review_missing_deadline | RIKEN Program for Drug Discovery and Medical Technology Platforms (DMP)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1388;

-- id_edital=1387 | review_missing_deadline | Fundamental Quantum Science Program
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1387;

-- id_edital=1386 | review_missing_deadline | Advanced General Intelligence for Science Program (AGIS)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1386;

-- id_edital=1385 | review_missing_deadline | TRIP Headquarters
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1385;

-- id_edital=1384 | hidden_historical | [Press Release]3GeV Electron Acceleration Succeeded at 3GeV synchrotron radiatio
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1384;

-- id_edital=1383 | review_missing_deadline | Quantum Beam Science
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1383;

-- id_edital=1382 | review_missing_deadline | Quantum Energy
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1382;

-- id_edital=1381 | review_missing_deadline | Quantum Medicine
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1381;

-- id_edital=1380 | review_missing_deadline | Quantum Technology Innovation
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1380;

-- id_edital=1379 | review_missing_deadline | Postdoctoral Researcher
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1379;

-- id_edital=1378 | visible_recent_strong_signal | Researcher
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1378;

-- id_edital=1377 | review_missing_deadline | メインコンテンツへ移動
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1377;

-- id_edital=1376 | hidden_duplicate | メインコンテンツへ移動
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1376;

-- id_edital=1375 | hidden_duplicate | メインコンテンツへ移動
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1375;

-- id_edital=1374 | hidden_duplicate | メインコンテンツへ移動
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1374;

-- id_edital=1373 | visible_recent_strong_signal | 契約(調達情報)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1373;

-- id_edital=1372 | review_missing_deadline | 研究を知る(研究情報)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1372;

-- id_edital=1371 | review_missing_deadline | 現在募集中の情報を見る
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1371;

-- id_edital=1370 | review_missing_deadline | 研究センター・部門紹介
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1370;

-- id_edital=1369 | review_missing_deadline | Researcher and Engineer Positions
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1369;

-- id_edital=1368 | review_missing_deadline | Our Research Achievements
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1368;

-- id_edital=1367 | review_missing_deadline | The Strength of NIMS''s Research in Numbers
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1367;

-- id_edital=1366 | review_missing_deadline | グリーンイノベーション基金事業／次世代型太陽電池の開発【事業紹介】
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1366;

-- id_edital=1365 | review_missing_deadline | グリーンイノベーション基金事業費補助金交付規程（218KB）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1365;

-- id_edital=1364 | review_missing_deadline | 本公募に関するQ＆A（357KB）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1364;

-- id_edital=1363 | review_missing_deadline | 公募要領（552KB）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1363;

-- id_edital=1362 | review_missing_deadline | グリーンイノベーション基金事業の基本方針（本文）（802KB）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1362;

-- id_edital=1361 | review_missing_deadline | グリーンイノベーション基金事業の基本方針（概要）（616KB）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1361;

-- id_edital=1360 | visible_recent_strong_signal | 実施者募集（公募）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1360;

-- id_edital=1359 | review_missing_deadline | データマネジメント（委託／補助・助成）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1359;

-- id_edital=1358 | review_missing_deadline | 知財マネジメント（委託）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1358;

-- id_edital=1357 | visible_recent_strong_signal | 委託事業・補助・助成事業の契約手続き
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1357;

-- id_edital=1356 | review_missing_deadline | 年度別の公募一覧
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1356;

-- id_edital=1355 | review_missing_deadline | 「グリーンイノベーション基金事業／次世代型単接合太陽電池実証事業」の追加公募について
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1355;

-- id_edital=1354 | review_missing_deadline | （情報更新）2026年度「二国間クレジット制度（JCM）等を活用した低炭素技術普及促進事業／低炭素技術による市場創出促進事業（実証設計）」の公募について
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1354;

-- id_edital=1353 | visible_recent_strong_signal | （情報更新）2026年度「二国間クレジット制度（JCM）等を活用した低炭素技術普及促進事業／定量化促進事業／有望技術分野の新規方法論開発に向けた調査」の公募につ
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1353;

-- id_edital=1352 | visible_recent_strong_signal | （情報更新）2026年度「二国間クレジット制度（JCM）等を活用した低炭素技術普及促進事業／定量化促進事業／JCMクレジット化支援調査事業」の公募について
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1352;

-- id_edital=1351 | review_missing_deadline | 「半導体・デジタル産業戦略の戦略的実行に向けた調査分析」の実施体制の決定について
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1351;

-- id_edital=1350 | review_missing_deadline | Japan Ministry of Defense (Japanese)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1350;

-- id_edital=1349 | hidden_historical | Measures on Defense Equipment and Technology Cooperation
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1349;

-- id_edital=1348 | hidden_not_opportunity | 05 DIGITAL INNOVATION
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_not_opportunity", "reason": "Conteúdo classificado como notícia/portal/página institucional, sem chamada ativa.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["not_opportunity"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1348;

-- id_edital=1347 | hidden_not_opportunity | 04 R&D CENTER, FACILITY
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_not_opportunity", "reason": "Conteúdo classificado como notícia/portal/página institucional, sem chamada ativa.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["not_opportunity"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1347;

-- id_edital=1346 | hidden_not_opportunity | 02 INNOVATION
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_not_opportunity", "reason": "Conteúdo classificado como notícia/portal/página institucional, sem chamada ativa.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["not_opportunity"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1346;

-- id_edital=1345 | hidden_not_opportunity | Space & Defense
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_not_opportunity", "reason": "Conteúdo classificado como notícia/portal/página institucional, sem chamada ativa.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["not_opportunity"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1345;

-- id_edital=1344 | hidden_not_opportunity | Energy & Environment
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_not_opportunity", "reason": "Conteúdo classificado como notícia/portal/página institucional, sem chamada ativa.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["not_opportunity"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1344;

-- id_edital=1343 | review_missing_deadline | Registration
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1343;

-- id_edital=1342 | hidden_not_opportunity | Procurement Network
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_not_opportunity", "reason": "Conteúdo classificado como notícia/portal/página institucional, sem chamada ativa.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["not_opportunity"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1342;

-- id_edital=1341 | hidden_not_opportunity | MHI Group Supply Chain Sustainability Promotion Guidelines
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_not_opportunity", "reason": "Conteúdo classificado como notícia/portal/página institucional, sem chamada ativa.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["not_opportunity"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1341;

-- id_edital=1340 | hidden_not_opportunity | Procurement Policy
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_not_opportunity", "reason": "Conteúdo classificado como notícia/portal/página institucional, sem chamada ativa.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["not_opportunity"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1340;

-- id_edital=1339 | hidden_not_opportunity | Procurement
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_not_opportunity", "reason": "Conteúdo classificado como notícia/portal/página institucional, sem chamada ativa.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["not_opportunity"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1339;

-- id_edital=1338 | hidden_not_opportunity | Research & Innovation Center
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_not_opportunity", "reason": "Conteúdo classificado como notícia/portal/página institucional, sem chamada ativa.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["not_opportunity"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1338;

-- id_edital=1337 | hidden_not_opportunity | Nuclear Energy Systems
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_not_opportunity", "reason": "Conteúdo classificado como notícia/portal/página institucional, sem chamada ativa.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["not_opportunity"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1337;

-- id_edital=1336 | hidden_historical | Science and Technology
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1336;

-- id_edital=1335 | review_missing_deadline | Closing date 2025/04/05 (Extended due to the AcademicJobsOnline site trouble) Re
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1335;

-- id_edital=1334 | review_missing_deadline | Closing date 2025/05/16 正午必着 Researcher 24-12 Current openings 1 Department 素粒子原
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1334;

-- id_edital=1333 | visible_recent_strong_signal | Closing date Tuesday August 19, 2025 12:00 (JST). ACCL25-1（Assistant Professor） 
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1333;

-- id_edital=1332 | visible_recent_strong_signal | Closing date Tuesday August 19, 2025 12:00 (JST). ACCL 25-2（Assistant Professor）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1332;

-- id_edital=1331 | visible_recent_strong_signal | Closing date 2025/12/31 ※The posting shall remain open until the positions are f
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1331;

-- id_edital=1330 | visible_recent_strong_signal | Closing date 2025/12/31 ※The posting shall remain open until the positions are f
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1330;

-- id_edital=1329 | visible_recent_strong_signal | Closing date 2025/08/21 必着 Researcher 25-1 Current openings 若干名 Department 素粒子原子
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1329;

-- id_edital=1328 | visible_recent_strong_signal | Closing date 2025/08/15 必着 Researcher 25-2 Current openings 1 Department 素粒子原子核研
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1328;

-- id_edital=1327 | visible_recent_strong_signal | Closing date Wednesday, December 24, 2025 12:00 (JST) ACCL25-3（Postdoctoral Fell
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1327;

-- id_edital=1326 | visible_recent_strong_signal | Closing date Wednesday, November 5, 2025 12:00 (JST) ACCL25-4 （Professor） Curren
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1326;

-- id_edital=1325 | visible_recent_strong_signal | Closing date Wednesday, November 5, 2025 12:00 (JST) ACCL25-5 （Associate Profess
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1325;

-- id_edital=1324 | visible_recent_strong_signal | Closing date Wednesday, December 24, 2025 12:00 (JST) ACCL25-6 （Assistant Profes
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1324;

-- id_edital=1323 | visible_recent_strong_signal | Closing date 2025/11/30 正午必着 Researcher 25-3 Current openings 1人 Department 素粒子原
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1323;

-- id_edital=1322 | visible_recent_strong_signal | Closing date Tuesday, February 17, 2026 12:00 (JST) ACCL25-10（Assistant Professo
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1322;

-- id_edital=1321 | visible_recent_strong_signal | Closing date Tuesday February17, 2026 12:00 (JST) ACCL25-9（Assistant Professor） 
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1321;

-- id_edital=1320 | visible_recent_strong_signal | Closing date 2026/2/1 12:00 JST February 1, 2026 Researcher 25-4 Current opening
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1320;

-- id_edital=1319 | visible_recent_strong_signal | Closing date Wednesday, April 22, 2026 12:00（JST) ACCL25-11（Professor） Current o
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1319;

-- id_edital=1318 | visible_recent_strong_signal | Closing date Wednesday, April 5, 2026 12:00（JST) ACCL25-12（Professor） Current op
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1318;

-- id_edital=1317 | visible_recent_strong_signal | Closing date March 10, 2026 ＊The posting shall remain open until the positions a
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1317;

-- id_edital=1316 | visible_recent_strong_signal | Closing date Tuesday, May 19, 2026 12:00（JST) ACCL25-13（Postdoctoral Fellow） Cur
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1316;

-- id_edital=1315 | visible_recent_strong_signal | Closing date Tuesday, May 19, 2026 12:00（JST) ACCL25-14（Assistant Professor） Cur
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1315;

-- id_edital=1314 | visible_recent_strong_signal | Closing date 2026/5/22 正午必着 Researcher 25-6 Current openings 1 Department 素粒子原子核
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1314;

-- id_edital=1313 | visible_recent_strong_signal | Closing date 2026/5/22 正午必着 Researcher 26-2 Current openings 1 Department 素粒子原子核
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1313;

-- id_edital=1312 | review_missing_deadline | Accelerator Laboratory(ACCL)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1312;

-- id_edital=1311 | visible_recent_strong_signal | 加速器・共通基盤研究施設運営会議
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1311;

-- id_edital=1310 | visible_recent_strong_signal | 素粒子原子核研究所運営会議
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1310;

-- id_edital=1309 | review_missing_deadline | 加速器研究施設（ACCL）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1309;

-- id_edital=1308 | review_missing_deadline | 素粒子原子核研究所（IPNS）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1308;

-- id_edital=1307 | review_missing_deadline | 安全への取り組み
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1307;

-- id_edital=1280 | review_missing_deadline | 科研費における研究データの管理・利活用
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1280;

-- id_edital=1279 | review_missing_deadline | 審査委員としての委嘱時の様式（様式1･2）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1279;

-- id_edital=1278 | review_missing_deadline | 審査区分表等
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1278;

-- id_edital=1277 | review_missing_deadline | 審査・評価について
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1277;

-- id_edital=1276 | review_missing_deadline | 交付決定後の様式(B･C様式)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1276;

-- id_edital=1275 | review_missing_deadline | 交付申請時の様式(A･D様式)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1275;

-- id_edital=1274 | review_missing_deadline | 様式提出方法一覧
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1274;

-- id_edital=1273 | review_missing_deadline | 研究成果における謝辞の表示
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1273;

-- id_edital=1272 | review_missing_deadline | 「調整金」について
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1272;

-- id_edital=1271 | review_missing_deadline | 繰越制度
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1271;

-- id_edital=1270 | review_missing_deadline | 国際共同研究加速基金
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1270;

-- id_edital=1269 | review_missing_deadline | 特別研究員奨励費
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1269;

-- id_edital=1268 | review_missing_deadline | 研究成果公開促進費
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1268;

-- id_edital=1267 | review_missing_deadline | 基盤研究（A・B・C）・挑戦的研究・若手研究
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1267;

-- id_edital=1266 | review_missing_deadline | 基盤研究（Ｓ）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1266;

-- id_edital=1265 | hidden_historical | 学術変革領域研究
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1265;

-- id_edital=1264 | review_missing_deadline | 新学術領域研究（研究領域提案型）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1264;

-- id_edital=1263 | review_missing_deadline | 特別推進研究
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1263;

-- id_edital=1262 | review_missing_deadline | 「基盤研究（Ｃ）」及び「若手研究」における独立基盤形成支援（試行）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1262;

-- id_edital=1261 | review_missing_deadline | 国際共同研究加速基金（帰国発展研究）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1261;

-- id_edital=1260 | review_missing_deadline | 国際共同研究加速基金（海外連携研究）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1260;

-- id_edital=1259 | review_missing_deadline | 国際共同研究加速基金（国際共同研究強化）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1259;

-- id_edital=1258 | review_missing_deadline | 国際共同研究加速基金（国際先導研究）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1258;

-- id_edital=1257 | review_missing_deadline | 特別研究員奨励費
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1257;

-- id_edital=1256 | review_missing_deadline | 奨励研究
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1256;

-- id_edital=1255 | review_missing_deadline | 研究活動スタート支援
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1255;

-- id_edital=1254 | visible_recent_strong_signal | 基盤研究（Ａ・Ｂ・Ｃ）・挑戦的研究・若手研究
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1254;

-- id_edital=1253 | visible_recent_strong_signal | 特別推進研究・基盤研究（Ｓ）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1253;

-- id_edital=1252 | hidden_expired | 科研費FAQ
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Registro marcado ativo=false.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["ativo_false"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1252;

-- id_edital=1251 | review_missing_deadline | 科研費ハンドブック
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1251;

-- id_edital=1250 | visible_recent_strong_signal | 科研費説明会
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1250;

-- id_edital=1249 | review_missing_deadline | 科研費パンフレット
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1249;

-- id_edital=1248 | review_missing_deadline | 科研費ロゴタイプ
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1248;

-- id_edital=1247 | review_missing_deadline | 科研費の「基金化」
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1247;

-- id_edital=1246 | review_missing_deadline | スケジュール
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1246;

-- id_edital=1245 | review_missing_deadline | 調達情報
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1245;

-- id_edital=1244 | review_missing_deadline | 若手研究者向けの支援事業一覧
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1244;

-- id_edital=1243 | review_missing_deadline | 外国人研究者招へい事業
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1243;

-- id_edital=1242 | review_missing_deadline | 研究開発マネジメント人材に関する体制整備事業
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1242;

-- id_edital=1241 | review_missing_deadline | 科学研究費助成事業（科研費）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1241;

-- id_edital=1240 | hidden_historical | National Government
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1240;

-- id_edital=1239 | hidden_duplicate | National Government
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1239;

-- id_edital=1238 | hidden_duplicate | National Government
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1238;

-- id_edital=1237 | hidden_duplicate | National Government
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1237;

-- id_edital=1236 | hidden_duplicate | National Government
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1236;

-- id_edital=1235 | hidden_historical | Points of attention
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1235;

-- id_edital=1234 | hidden_historical | Links to Core Cities and Exceptional Cities
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1234;

-- id_edital=1233 | hidden_historical | List of organizations covered
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1233;

-- id_edital=1232 | hidden_historical | Points of attention
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1232;

-- id_edital=1231 | hidden_historical | About Government Procurement
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1231;

-- id_edital=1230 | hidden_historical | Government Procurement
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1230;

-- id_edital=1229 | hidden_not_opportunity | IHI AEROSPACE and ArianeGroup Sign Cooperation Agreement for the Operation of an
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_not_opportunity", "reason": "Conteúdo classificado como notícia/portal/página institucional, sem chamada ativa.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["not_opportunity"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1229;

-- id_edital=1228 | hidden_not_opportunity | IHI signs JCDA with PETRONAS and Gentari for demonstration of an ammonia-powered
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_not_opportunity", "reason": "Conteúdo classificado como notícia/portal/página institucional, sem chamada ativa.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["not_opportunity"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1228;

-- id_edital=1227 | hidden_not_opportunity | IHI, Subsidiaries of Babcock Power Inc. Sign Strategic Collaboration Agreement f
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_not_opportunity", "reason": "Conteúdo classificado como notícia/portal/página institucional, sem chamada ativa.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["not_opportunity"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1227;

-- id_edital=1226 | hidden_not_opportunity | IHI will participate as a speaker at a prime seminar at “SEA JAPAN 2026”, an int
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_not_opportunity", "reason": "Conteúdo classificado como notícia/portal/página institucional, sem chamada ativa.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["not_opportunity"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1226;

-- id_edital=1225 | review_missing_deadline | Tokyo Gas Ohgishima LNG Terminal No. 4 In-Ground LNG Storage Tank Certified by G
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1225;

-- id_edital=1224 | hidden_not_opportunity | Aero Engine, Space & Defense
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_not_opportunity", "reason": "Conteúdo classificado como notícia/portal/página institucional, sem chamada ativa.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["not_opportunity"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1224;

-- id_edital=1223 | hidden_not_opportunity | Industrial Systems & General-purpose Machinery
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_not_opportunity", "reason": "Conteúdo classificado como notícia/portal/página institucional, sem chamada ativa.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["not_opportunity"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1223;

-- id_edital=1222 | hidden_not_opportunity | Resources, Energy & Environment
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_not_opportunity", "reason": "Conteúdo classificado como notícia/portal/página institucional, sem chamada ativa.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["not_opportunity"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1222;

-- id_edital=1221 | visible_recent_strong_signal | 防衛装備庁について
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1221;

-- id_edital=1220 | review_missing_deadline | 防衛装備庁ロゴについて
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1220;

-- id_edital=1219 | review_missing_deadline | リーフレット
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1219;

-- id_edital=1218 | review_missing_deadline | 公募のページ
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1218;

-- id_edital=1217 | review_missing_deadline | 令和７年度終了評価および中間評価の結果
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1217;

-- id_edital=1216 | review_missing_deadline | 需要調査
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1216;

-- id_edital=1215 | review_missing_deadline | 事務処理関係
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1215;

-- id_edital=1214 | review_missing_deadline | 応募状況採択課題
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1214;

-- id_edital=1213 | hidden_duplicate | 防衛装備庁について
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1213;

-- id_edital=1212 | visible_recent_strong_signal | R&D page
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1212;

-- id_edital=1211 | review_missing_deadline | Ground Systems Research Center page
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1211;

-- id_edital=1210 | review_missing_deadline | Naval Systems Research Center page
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1210;

-- id_edital=1209 | review_missing_deadline | Request for Tender page
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1209;

-- id_edital=1208 | hidden_historical | Defense Equipment and Technology Cooperation page
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1208;

-- id_edital=1207 | review_missing_deadline | 九州センター
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1207;

-- id_edital=1206 | visible_recent_strong_signal | 四国センター
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1206;

-- id_edital=1205 | review_missing_deadline | 中国センター
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1205;

-- id_edital=1204 | visible_recent_strong_signal | 中部センター
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1204;

-- id_edital=1203 | visible_recent_strong_signal | 北海道センター
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1203;

-- id_edital=1202 | visible_recent_strong_signal | 北陸デジタルものづくりセンター
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1202;

-- id_edital=1201 | review_missing_deadline | 臨海副都心センター
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1201;

-- id_edital=1200 | visible_recent_strong_signal | 東北センター
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1200;

-- id_edital=1199 | review_missing_deadline | 産総研ブランドストーリー
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1199;

-- id_edital=1198 | hidden_historical | Gestão de Projetos
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1198;

-- id_edital=1197 | review_missing_deadline | Nuclear
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1197;

-- id_edital=1196 | hidden_historical | Indústria
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1196;

-- id_edital=1195 | hidden_resultado | Meio Ambiente
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1195;

-- id_edital=1194 | hidden_historical | Energia
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1194;

-- id_edital=1193 | hidden_historical | Áreas de Pesquisa
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1193;

-- id_edital=1192 | hidden_resultado | Internacionalização
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1192;

-- id_edital=1191 | hidden_historical | Pesquisa e Desenvolvimento
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1191;

-- id_edital=1190 | hidden_historical | Parcerias de P&D com Empresas
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1190;

-- id_edital=1189 | visible_recent_strong_signal | Fusão Nuclear
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1189;

-- id_edital=1188 | hidden_historical | Centros de Pesquisa
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1188;

-- id_edital=1187 | hidden_historical | Emergência Radiológica IPEN
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1187;

-- id_edital=1186 | hidden_resultado | Convênios e Transferências
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1186;

-- id_edital=1185 | review_missing_deadline | Programa de Política Nuclear - PPA
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1185;

-- id_edital=1184 | hidden_institutional | Escola de Verão
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1184;

-- id_edital=1183 | hidden_expired | Intelligence Community Centers for Academic Excellence
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1183;

-- id_edital=1182 | hidden_expired | Intelligence Community Centers For Academic Excellence
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1182;

-- id_edital=1181 | hidden_expired | BROAD AGENCY ANNOUNCEMENT FOR Entangled Logical Qubits (ELQ)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1181;

-- id_edital=1180 | hidden_expired | TrojAI
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1180;

-- id_edital=1179 | hidden_expired | SuperCables
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1179;

-- id_edital=1178 | hidden_expired | Advanced Materials and Fabrication for Coherent Superconducting Qubits -
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1178;

-- id_edital=1177 | hidden_expired | IARPA Advanced Materials and Fabrication for Coherent Superconducting Qubits Pro
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1177;

-- id_edital=1176 | hidden_expired | Targeted Evaluation of Ionizing Radiation Exposure (TEI-REX)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1176;

-- id_edital=1175 | review_missing_deadline | HORIZON-CL2-2022-DEMOCRACY-01-07
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1175;

-- id_edital=1174 | review_missing_deadline | HORIZON-CL2-2022-DEMOCRACY-01-06
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1174;

-- id_edital=1173 | review_missing_deadline | HORIZON-CL2-2022-DEMOCRACY-01-05
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1173;

-- id_edital=1172 | review_missing_deadline | HORIZON-CL2-2022-DEMOCRACY-01-04
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1172;

-- id_edital=1171 | review_missing_deadline | HORIZON-CL2-2022-DEMOCRACY-01-03
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1171;

-- id_edital=1170 | review_missing_deadline | HORIZON-CL2-2022-DEMOCRACY-01-02
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1170;

-- id_edital=1169 | review_missing_deadline | HORIZON-CL2-2022-DEMOCRACY-01-01
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1169;

-- id_edital=1168 | review_missing_deadline | HORIZON-CL2-2021-TRANSFORMATIONS-01-07
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1168;

-- id_edital=1167 | review_missing_deadline | HORIZON-CL2-2021-TRANSFORMATIONS-01-06
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1167;

-- id_edital=1166 | review_missing_deadline | HORIZON-CL2-2021-TRANSFORMATIONS-01-05
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1166;

-- id_edital=1165 | review_missing_deadline | HORIZON-CL2-2021-TRANSFORMATIONS-01-04
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1165;

-- id_edital=1164 | review_missing_deadline | HORIZON-CL2-2021-TRANSFORMATIONS-01-03
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1164;

-- id_edital=1163 | review_missing_deadline | HORIZON-CL2-2021-TRANSFORMATIONS-01-02
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1163;

-- id_edital=1162 | review_missing_deadline | HORIZON-CL2-2021-TRANSFORMATIONS-01-01
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1162;

-- id_edital=1161 | review_missing_deadline | HORIZON-CL2-2021-HERITAGE-02-02
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1161;

-- id_edital=1160 | review_missing_deadline | HORIZON-CL2-2021-HERITAGE-02-01
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1160;

-- id_edital=1159 | review_missing_deadline | HORIZON-CL2-2021-HERITAGE-01-04
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1159;

-- id_edital=1158 | review_missing_deadline | HORIZON-CL2-2021-HERITAGE-01-03
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1158;

-- id_edital=1157 | review_missing_deadline | HORIZON-CL2-2021-HERITAGE-01-02
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1157;

-- id_edital=1156 | review_missing_deadline | HORIZON-CL2-2021-HERITAGE-01-01
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1156;

-- id_edital=1155 | review_missing_deadline | HORIZON-CL2-2021-DEMOCRACY-01-05
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1155;

-- id_edital=1154 | review_missing_deadline | HORIZON-CL2-2021-DEMOCRACY-01-04
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1154;

-- id_edital=1153 | review_missing_deadline | HORIZON-CL2-2021-DEMOCRACY-01-03
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1153;

-- id_edital=1152 | review_missing_deadline | HORIZON-CL2-2021-DEMOCRACY-01-02
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1152;

-- id_edital=1151 | review_missing_deadline | HORIZON-CL2-2021-DEMOCRACY-01-01
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1151;

-- id_edital=1150 | review_missing_deadline | Grants for Adaptive Sports Programs for Disabled Veterans and Disabled Members o
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1150;

-- id_edital=1149 | review_missing_deadline | Strengthening Community Colleges Training Grants (Round 6)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1149;

-- id_edital=1148 | review_missing_deadline | Low-Cost Chip-Scale Atomic Clock (LC CSAC)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1148;

-- id_edital=1147 | review_missing_deadline | U.S. Embassy Lome Public Diplomacy Small Grants Program
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1147;

-- id_edital=1146 | visible_current | Protecting U.S. Critical Energy Investments Through C-UAS and UAS Surveillance C
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-08-06).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1146;

-- id_edital=1145 | review_missing_deadline | FY25 Naval Air Warfare Center Aircraft Division Office-Wide Broad Agency Announc
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1145;

-- id_edital=1144 | review_missing_deadline | AFCEC Land Management Mapping for CONUS/Europe/PACAF Air Force Installations
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1144;

-- id_edital=1143 | review_missing_deadline | Manufacturing in America E2G Grant Initiative
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1143;

-- id_edital=1142 | review_missing_deadline | Cultural Resources Technical Guidance Support for Joint Base San Antonio, Texas
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1142;

-- id_edital=1141 | visible_current | Updated National Dislocated Worker Grant Program Guidance and Application Inform
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-08-05).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1141;

-- id_edital=1140 | hidden_duplicate | Updated National Dislocated Worker Grant Program Guidance and Application Inform
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1140;

-- id_edital=1139 | review_missing_deadline | Research Initiatives at the Naval Postgraduate School
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1139;

-- id_edital=1138 | review_missing_deadline | FY25 ONR Office Of Naval Research (ONR) Science, Technology, Engineering, and Ma
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1138;

-- id_edital=1137 | review_missing_deadline | Mgt, Species, Pollinators, Western Bumble bee Joint Base Elmendorf- Richardson, 
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1137;

-- id_edital=1136 | review_missing_deadline | DoW Breast Cancer, Transformative Breast Cancer Consortium Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1136;

-- id_edital=1135 | review_missing_deadline | Research and Development (RAD) Directed Energy (RD) University Assistance Instru
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1135;

-- id_edital=1134 | visible_current | DoW Pancreatic Cancer Research Program, Translational Research Partnership Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-07-10).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1134;

-- id_edital=1133 | review_missing_deadline | LPS Qubit Collaboratory (LQC)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1133;

-- id_edital=1132 | visible_current | DEVCOM ANALYSIS CENTER BROAD AGENCY ANNOUNCEMENT FOR APPLIED RESEARCH
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2028-04-01).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1132;

-- id_edital=1131 | review_missing_deadline | DoW Breast Cancer, Breakthrough Award Level 3
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1131;

-- id_edital=1130 | visible_current | DoW Pancreatic Cancer Research Program, Focused Pilot Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-07-10).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1130;

-- id_edital=1129 | visible_current | DoW Pancreatic Cancer Research Program, Idea Development Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-07-10).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1129;

-- id_edital=1128 | review_missing_deadline | FY25 Long Range Broad Agency Announcement (BAA) for Navy and Marine Corps Scienc
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1128;

-- id_edital=1127 | review_missing_deadline | DoW Amyotrophic Lateral Sclerosis Research Program, Pilot Clinical Trial Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1127;

-- id_edital=1126 | visible_current | DoW Breast Cancer, Breakthrough Award Levels 1 and 2
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-08-07).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1126;

-- id_edital=1125 | visible_current | DoW Tuberous Sclerosis Complex, Idea Development Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-06-08).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1125;

-- id_edital=1124 | visible_current | Ecosystem and Natural Resource Range Study at Fort Stewart/Hunter Army Airfield,
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-08-05).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1124;

-- id_edital=1123 | hidden_expired | DoW Ovarian Cancer, Clinical Trial Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1123;

-- id_edital=1122 | review_missing_deadline | DoW Breast Cancer, Breakthrough Award Level 4
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1122;

-- id_edital=1121 | visible_current | Staff Research Program
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2030-02-06).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1121;

-- id_edital=1120 | visible_current | DoW Breast Cancer, Clinical Research Extension Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-08-07).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1120;

-- id_edital=1119 | review_missing_deadline | DoW Multiple Sclerosis Clinical Trial Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1119;

-- id_edital=1118 | visible_current | DoW Breast Cancer, Era of Hope Scholar Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-08-07).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1118;

-- id_edital=1117 | review_missing_deadline | DoW Lupus, Transformative Vision Development Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1117;

-- id_edital=1116 | review_missing_deadline | Military-Connected Schools Construction, Modernization and Facilities Maintenanc
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1116;

-- id_edital=1115 | visible_current | DoW Tuberous Sclerosis Complex, Clinical Translational Research Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-06-08).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1115;

-- id_edital=1114 | review_missing_deadline | Measurement Science and Engineering (MSE) Research Grant Programs
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1114;

-- id_edital=1113 | visible_current | DoW Breast Cancer, Transformative Breast Cancer Consortium Development Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-08-07).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1113;

-- id_edital=1112 | review_missing_deadline | DoW Lupus, Transformative Vision Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1112;

-- id_edital=1111 | review_missing_deadline | DoW Lupus, Idea Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1111;

-- id_edital=1110 | hidden_expired | DoW, Ovarian Cancer, Ovarian Cancer Clinical Trial Academy – Early-Career Invest
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1110;

-- id_edital=1109 | hidden_expired | DoW, Ovarian Cancer, Investigator-Initiated Research Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1109;

-- id_edital=1108 | review_missing_deadline | DoW Alzheimer’s Transforming Care Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1108;

-- id_edital=1107 | hidden_expired | DoW, Ovarian Cancer, Ovarian Cancer Academy – Early-Career Investigator Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1107;

-- id_edital=1106 | review_missing_deadline | DoW Amyotrophic Lateral Sclerosis Research Program, Clinical Outcomes and Biomar
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1106;

-- id_edital=1105 | review_missing_deadline | DoW Lupus, Impact Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1105;

-- id_edital=1104 | review_missing_deadline | DoW Multiple Sclerosis Exploration-Hypothesis Development Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1104;

-- id_edital=1103 | review_missing_deadline | DoW Alzheimer’s Transforming Diagnosis Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1103;

-- id_edital=1102 | review_missing_deadline | DoW Multiple Sclerosis Early Investigator Research Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1102;

-- id_edital=1101 | hidden_expired | DoW, Ovarian Cancer, Pilot Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1101;

-- id_edital=1100 | visible_current | DoW Tuberous Sclerosis Complex, Exploration-Hypothesis Development Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-06-08).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1100;

-- id_edital=1099 | review_missing_deadline | DoW Tick-Borne Disease Idea Development Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1099;

-- id_edital=1098 | review_missing_deadline | DoW Amyotrophic Lateral Sclerosis Research Program, Therapeutic Idea Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1098;

-- id_edital=1097 | review_missing_deadline | DoW Alzheimer’s Transforming Research Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1097;

-- id_edital=1096 | visible_current | DoW Spinal Cord Injury, Clinical Trial Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-12-11).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1096;

-- id_edital=1095 | review_missing_deadline | DoW Multiple Sclerosis Investigator-Initiated Research Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1095;

-- id_edital=1094 | visible_current | DoW Spinal Cord Injury, Clinical Translation Research Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-12-11).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1094;

-- id_edital=1093 | visible_current | DoW Spinal Cord Injury, Translational Research Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-12-11).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1093;

-- id_edital=1092 | review_missing_deadline | DoW Arthritis Clinical Research Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1092;

-- id_edital=1091 | hidden_expired | DoW Peer Reviewed Cancer, Clinical Trial Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1091;

-- id_edital=1090 | review_missing_deadline | DoW Tick-Borne Disease Therapeutic/Diagnostic Research Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1090;

-- id_edital=1089 | visible_current | DoW Spinal Cord Injury, Investigator-Initiated Research Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-12-11).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1089;

-- id_edital=1088 | hidden_expired | DoW Lung Cancer Patient-Centered Outcomes and Survivorship Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1088;

-- id_edital=1087 | hidden_expired | DoW Lung Cancer Translational Research Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1087;

-- id_edital=1086 | review_missing_deadline | DoW Arthritis Translational Research Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1086;

-- id_edital=1085 | hidden_expired | DoW Lung Cancer Idea Development Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1085;

-- id_edital=1084 | review_missing_deadline | Naval Engineering Education Consortium (NEEC) Broad Agency Announcement for Fisc
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1084;

-- id_edital=1083 | review_missing_deadline | DoW Amyotrophic Lateral Sclerosis Research Program, Therapeutic Development Awar
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1083;

-- id_edital=1082 | review_missing_deadline | DoW Peer Reviewed Medical, Clinical Trial Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1082;

-- id_edital=1081 | visible_current | DoW Peer Reviewed Medical, Lifestyle and Applied Health Research Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-06-08).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1081;

-- id_edital=1080 | visible_current | DoW Peer Reviewed Medical, Impact Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-06-08).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1080;

-- id_edital=1079 | review_missing_deadline | DoW Peer Reviewed Medical, Discovery Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1079;

-- id_edital=1078 | review_missing_deadline | DoW Peer Reviewed Medical, Research Advancement Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1078;

-- id_edital=1077 | visible_current | ARMY APPLICATIONS LAB BROAD AGENCY ANNOUNCEMENT FOR DISRUPTIVE APPLICATIONS
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2029-04-04).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1077;

-- id_edital=1076 | review_missing_deadline | Fundamental Research to Counter Weapons of Mass Destruction
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1076;

-- id_edital=1075 | review_missing_deadline | NRL Long Range Broad Agency Announcement (BAA) for Basic and Applied Research
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1075;

-- id_edital=1074 | review_missing_deadline | Continuing Human Enabling Enhancing Restoring and Sustaining
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1074;

-- id_edital=1073 | review_missing_deadline | Grants to Expand Substance Use Disorder Treatment Capacity in Adult and Family T
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1073;

-- id_edital=1072 | review_missing_deadline | Public Diplomacy Small Grants Program
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1072;

-- id_edital=1071 | review_missing_deadline | Announcement of Stand Down Grants
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1071;

-- id_edital=1070 | review_missing_deadline | Tactical Behaviors for Autonomous Maneuver
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1070;

-- id_edital=1069 | review_missing_deadline | UNITED STATES ARMY RESEARCH INSTITUTE FOR THE BEHAVIORAL AND SOCIAL SCIENCES (AR
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1069;

-- id_edital=1068 | review_missing_deadline | BROAD AGENCY ANNOUNCEMENT (BAA) for Extramural Biomedical and Human Performance 
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1068;

-- id_edital=1067 | review_missing_deadline | DoW Peer Reviewed Medical, Platform Clinical Translation Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1067;

-- id_edital=1066 | visible_current | DoW Peer Reviewed Medical, Technology/Therapeutic Development Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-06-08).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1066;

-- id_edital=1065 | hidden_expired | DoW, Peer Reviewed Cancer, Impact Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1065;

-- id_edital=1064 | visible_current | DoW Vision, Clinical Trial Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-12-11).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1064;

-- id_edital=1063 | visible_current | DoW Vision, Translational Research Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-12-11).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1063;

-- id_edital=1062 | visible_current | DoW Hearing Restoration Focused Research Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-10-09).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1062;

-- id_edital=1061 | visible_current | Laboratory Flexible Funding Model (LFFM)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2028-11-01).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1061;

-- id_edital=1060 | review_missing_deadline | DoW Military Burn, Discovery Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1060;

-- id_edital=1059 | review_missing_deadline | Research Interests of the United States Air Force Academy (formerly USAFA-BAA-20
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1059;

-- id_edital=1058 | review_missing_deadline | Broad Agency Announcement for Fundamental AI Research
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1058;

-- id_edital=1057 | review_missing_deadline | DoW Military Burn, Technology/Therapeutic Development Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1057;

-- id_edital=1056 | review_missing_deadline | Automated Discovery for Design and Control of Turbulent Systems (AutoDIDACTS)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1056;

-- id_edital=1055 | review_missing_deadline | DoW Military Burn, Patient-Centered Research Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1055;

-- id_edital=1054 | review_missing_deadline | Development of Candidate Medical Countermeasures (MCMs) and Technologies Against
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1054;

-- id_edital=1053 | visible_current | Shared Instrumentation Grant (SIG) Program (S10 Clinical Trial Not Allowed)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2027-01-06).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1053;

-- id_edital=1052 | visible_current | High-End Instrumentation (HEI) Grant Program (S10 Clinical Trial Not Allowed)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2027-01-06).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1052;

-- id_edital=1051 | hidden_expired | DoW Peer Reviewed Cancer, Idea Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1051;

-- id_edital=1050 | visible_current | DoW Vision, Investigator-Initiated Research Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-12-11).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1050;

-- id_edital=1049 | visible_current | DoW Vision, Mentored Clinical Research Award
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-10-09).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1049;

-- id_edital=1048 | visible_current | Defense Security Cooperation University - Research Grants
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2028-07-08).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1048;

-- id_edital=1047 | review_missing_deadline | DEVCOM ARMY RESEARCH LABORATORY BROAD AGENCY ANNOUNCEMENT FOR FOUNDATIONAL RESEA
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1047;

-- id_edital=1046 | visible_current | Defense Production Act Title III Expansion of Domestic Production Capability and
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-12-07).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1046;

-- id_edital=1045 | review_missing_deadline | UNITED STATES MILITARY ACADEMY Broad Agency Announcement
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1045;

-- id_edital=1044 | review_missing_deadline | Advancing NATO’s Collective Defense and Industrial Capacity
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1044;

-- id_edital=1043 | hidden_expired | Defense Sciences Office (DSO) Office-wide BAA
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1043;

-- id_edital=1042 | review_missing_deadline | Fiscal Year 2026 University Nuclear Research Infrastructure Revitalization
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1042;

-- id_edital=1041 | review_missing_deadline | Advanced Nuclear Energy Licensing Cost-Share Grant Program
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1041;

-- id_edital=1040 | review_missing_deadline | High-performance Optimized Recycled Nuclear Isotopes for Gen IV reactors (HORNIG
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1040;

-- id_edital=1039 | visible_current | Fiscal Year 2026 Consolidated Innovative Nuclear Research
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-09-06).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1039;

-- id_edital=1038 | review_missing_deadline | University Nuclear Leadership Program– Scholarship and Fellowship Support
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1038;

-- id_edital=1037 | review_missing_deadline | Fiscal Year 2026 Phase II Continuation Consolidated Innovative Nuclear Research
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1037;

-- id_edital=1036 | review_missing_deadline | CHEERS Open Period 1 - All Technical Areas
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1036;

-- id_edital=1035 | visible_current | Collaboration for Innovative Research on Aircraft Structure (CIRAS)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-11-05).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1035;

-- id_edital=1034 | review_missing_deadline | Pioneering Aerospace Capabilities, Engineering and Research (PACER)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1034;

-- id_edital=1033 | review_missing_deadline | DRAFT Community Noise Mitigation Program
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1033;

-- id_edital=1032 | review_missing_deadline | Military and Civilian Partnership for Trauma Readiness Grant Program/Mission Zer
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1032;

-- id_edital=1031 | review_missing_deadline | STARBASE Wright Patt
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1031;

-- id_edital=1030 | review_missing_deadline | Department of Defense HIV/AIDS Prevention Program
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1030;

-- id_edital=1029 | review_missing_deadline | FY 2026 Defense Community Infrastructure Program
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1029;

-- id_edital=1028 | review_missing_deadline | NIEHS Worker Training Program’s HAZMAT Training at DOE Nuclear Weapons Complex (
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1028;

-- id_edital=1027 | review_missing_deadline | National Defense Education Program (NDEP) Science, Technology, Engineering, and 
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1027;

-- id_edital=1026 | review_missing_deadline | DOD Defense Health Agency (DHA) Research & Development FY23-FY27 BROAD AGENCY AN
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1026;

-- id_edital=1025 | visible_current | CONSORTIUM FOR NUCLEAR FORENSICS
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-10-06).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 1025;

-- id_edital=1024 | review_missing_deadline | CHEERS Open Period 2 - All Technical Areas
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1024;

-- id_edital=1023 | review_missing_deadline | LIGHT ARMORED VEHICLE
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1023;

-- id_edital=1022 | review_missing_deadline | PURCHASE ORDER TERMS & CONDITIONS
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1022;

-- id_edital=1021 | review_missing_deadline | SUPPLIER PERFORMANCE
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1021;

-- id_edital=1020 | review_missing_deadline | QUALITY
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1020;

-- id_edital=1019 | review_missing_deadline | iSUPPLIER
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1019;

-- id_edital=1018 | review_missing_deadline | ETHICS & CONDUCT BLUE BOOK (v7)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1018;

-- id_edital=1017 | hidden_historical | CYBERSECURITY
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1017;

-- id_edital=1016 | review_missing_deadline | SUPPLIERS
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1016;

-- id_edital=1015 | review_missing_deadline | Mentor-Protégé Program
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1015;

-- id_edital=1014 | hidden_expired | Supplier FAQs
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Registro marcado ativo=false.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["ativo_false"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 1014;

-- id_edital=1013 | review_missing_deadline | FNDE - Página de Programas e Chamadas
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1013;

-- id_edital=1012 | review_missing_deadline | PI 01/2026. PELD
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1012;

-- id_edital=1011 | review_missing_deadline | PI 05/26: Ganhando o Mundo da Ciência: La Trobe
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1011;

-- id_edital=1010 | review_missing_deadline | PI 07/2026: INCTs
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1010;

-- id_edital=1009 | review_missing_deadline | CP 01/26: PIBIC & PIBIT
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1009;

-- id_edital=1008 | hidden_institutional | CP 02/26: PIBIS
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1008;

-- id_edital=1007 | hidden_institutional | CP 03/26: PIBEX
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1007;

-- id_edital=1006 | hidden_institutional | CP 05/26: Eventos - ASI (jul/26 - jan/27)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 1006;

-- id_edital=1005 | review_missing_deadline | CP 06/26: Prêmio Confap
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1005;

-- id_edital=1004 | review_missing_deadline | PI 01/25. NAPI Saúde Pública de Precisão
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1004;

-- id_edital=1003 | review_missing_deadline | PI 02/25. Equinos
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1003;

-- id_edital=1002 | review_missing_deadline | PI 03/25. Colágeno de Jumento
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1002;

-- id_edital=1001 | review_missing_deadline | PI 04/25. Grande Reserva Mata Atlântica
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1001;

-- id_edital=1000 | review_missing_deadline | PI 05/25. FIIL
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1000;

-- id_edital=999 | review_missing_deadline | PI 06/25. Programa Wash
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 999;

-- id_edital=998 | review_missing_deadline | PI 07/25. NAPI Erva-Mate
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 998;

-- id_edital=997 | review_missing_deadline | PI 08/25. Amazônia + 10
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 997;

-- id_edital=996 | review_missing_deadline | PI 09/25. Mitacs GRI
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 996;

-- id_edital=995 | review_missing_deadline | PI 10/25. Biodiversa + 2023
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 995;

-- id_edital=994 | review_missing_deadline | PI 11/25. Robalos e Gaiolas Marinhas
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 994;

-- id_edital=993 | review_missing_deadline | PI 12/25. Economia Azul Sustentável
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 993;

-- id_edital=992 | review_missing_deadline | PI 13/25. NAPI Space
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 992;

-- id_edital=991 | review_missing_deadline | PI 14/25. NAPI Proteômica
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 991;

-- id_edital=990 | review_missing_deadline | PI 15/25. Mitacs GRA
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 990;

-- id_edital=989 | review_missing_deadline | PI 16/25. ERC - IA
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 989;

-- id_edital=988 | review_missing_deadline | PI 18/25. Quintas Paraná Faz Ciência
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 988;

-- id_edital=987 | review_missing_deadline | PI 19/25: Anel de Conectividade
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 987;

-- id_edital=986 | review_missing_deadline | PI 20/25: SECTES-PR 2025
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 986;

-- id_edital=985 | review_missing_deadline | PI 21/25. Wallonie Bruxelles
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 985;

-- id_edital=984 | review_missing_deadline | PI 22/25: NAPI Lutas Marciais
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 984;

-- id_edital=983 | hidden_institutional | PI 23/25. NAPI PITIS (Saúde)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 983;

-- id_edital=982 | review_missing_deadline | PI 24/25. NAPI Biogás
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 982;

-- id_edital=981 | review_missing_deadline | PI 25/25. Jovens Cientistas (Serrapilheira)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 981;

-- id_edital=980 | review_missing_deadline | PI 26/25. Ganhando o Mundo da Ciência: Compiègne
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 980;

-- id_edital=979 | review_missing_deadline | PI 27/25. Ganhando o Mundo da Ciência: Wageningen
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 979;

-- id_edital=978 | review_missing_deadline | PI 28/25: Céus Históricos no Planetário
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 978;

-- id_edital=977 | review_missing_deadline | PI 29/25. Pós-Graduação
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 977;

-- id_edital=976 | review_missing_deadline | PI 30/25: Mobility Confap Italy - MCI
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 976;

-- id_edital=975 | review_missing_deadline | PI 32/25. Resiliência Climática RS
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 975;

-- id_edital=974 | review_missing_deadline | PI 33/25: NAPI Robótica
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 974;

-- id_edital=973 | review_missing_deadline | PI 34/25: Dupla-Diplomação
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 973;

-- id_edital=972 | review_missing_deadline | PI 35/25. PIPAD
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 972;

-- id_edital=971 | review_missing_deadline | PI 36/25: InovaOstra
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 971;

-- id_edital=970 | review_missing_deadline | PI 37/25: SABIÁ (Guarapuava)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 970;

-- id_edital=969 | review_missing_deadline | PI 38/25: Patrulheiros da Sustentabilidade
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 969;

-- id_edital=968 | review_missing_deadline | PI 39/2025: CitrusBot1 - Tecnologias para Laranjas
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 968;

-- id_edital=967 | review_missing_deadline | PI 40/2025: NAPI Agrogenômica - Soja
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 967;

-- id_edital=966 | review_missing_deadline | PI 41/2025: NAPI Agrogenômica - Feijão
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 966;

-- id_edital=965 | review_missing_deadline | PI 42/2025: NAPI Agrogenômica - Solos
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 965;

-- id_edital=964 | review_missing_deadline | PI 43/2025 - Em produção
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 964;

-- id_edital=963 | hidden_institutional | PI 44/25. NAPI Governança e Bioinovação
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 963;

-- id_edital=962 | review_missing_deadline | PI 45/2025. INCTs
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 962;

-- id_edital=961 | review_missing_deadline | PI 46/25. Semana de C&T
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 961;

-- id_edital=960 | review_missing_deadline | PI 47/2025. Ciagro
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 960;

-- id_edital=959 | review_missing_deadline | PI 48/2025. Queijos Finos
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 959;

-- id_edital=958 | review_missing_deadline | PI 49/25. Ganhando o Mundo da Ciência: Kyoto
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 958;

-- id_edital=957 | review_missing_deadline | PI 50/25. Ganhando o Mundo da Ciência: Alberta
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 957;

-- id_edital=956 | review_missing_deadline | PI 51/25. Ganhando o Mundo da Ciência: UTC
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 956;

-- id_edital=955 | review_missing_deadline | PI 52/25. Confap & CNR 2024
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 955;

-- id_edital=954 | review_missing_deadline | PI 53/2025. IPASP-PR
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 954;

-- id_edital=953 | review_missing_deadline | CP 01/25. Piscicultura (Biopark)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 953;

-- id_edital=952 | hidden_institutional | CP 02/25. Eventos (05-10/25)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 952;

-- id_edital=951 | review_missing_deadline | CP 03/25. Interconexões: Itália
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 951;

-- id_edital=950 | hidden_institutional | CP 04/25. Top Managers
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 950;

-- id_edital=949 | review_missing_deadline | CP 05/25. Tecnova III
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 949;

-- id_edital=948 | review_missing_deadline | CP 06/25. PROPAR
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 948;

-- id_edital=947 | hidden_institutional | CP 07/25. Bolsa-Técnico
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 947;

-- id_edital=946 | review_missing_deadline | CP 08/25. PPSUS
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 946;

-- id_edital=945 | review_missing_deadline | CP 09/25. PIBIC & PIBIT
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 945;

-- id_edital=944 | hidden_institutional | CP 10/25. PIBEX
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 944;

-- id_edital=943 | hidden_institutional | CP 11/25. PIBIS
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 943;

-- id_edital=942 | hidden_institutional | CP 12/25. EAIC & EAITI
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 942;

-- id_edital=941 | hidden_institutional | CP 13/25. EAEX
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 941;

-- id_edital=940 | hidden_institutional | CP 14/25. SEURS
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 940;

-- id_edital=939 | review_missing_deadline | CP 15/25. Proteínas Alternativas
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 939;

-- id_edital=938 | hidden_institutional | CP 16/25: Eventos - ASI (nov/25 - jun/26)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 938;

-- id_edital=937 | hidden_institutional | CP 17/25. Eventos - IES (fev/26 - jan/27)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 937;

-- id_edital=936 | review_missing_deadline | CP 18/25. Interconexões: Japão
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 936;

-- id_edital=935 | review_missing_deadline | CP 19/25. Parceria Renault
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 935;

-- id_edital=934 | review_missing_deadline | PI 06/26: Mitacs GRI
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 934;

-- id_edital=933 | review_missing_deadline | PI 13/26: SECTES-PR 2026
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 933;

-- id_edital=932 | visible_continuous_flow | CP 09/22: Acolhida a Ucranianos
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_continuous_flow", "reason": "Fluxo contínuo ou chamada permanente.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["continuous_flow"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 932;

-- id_edital=931 | hidden_institutional | CP 10/22: Universidades Amig@s: Ucrânia
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["continuous_flow", "institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 931;

-- id_edital=930 | visible_continuous_flow | CP 15/24: Permanência de Ucranianos
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_continuous_flow", "reason": "Fluxo contínuo ou chamada permanente.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["continuous_flow"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 930;

-- id_edital=929 | review_missing_deadline | CP 04/26: Interconexões Brasillinois
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 929;

-- id_edital=928 | review_missing_deadline | CP 08/26: Nexus Inovação
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 928;

-- id_edital=927 | review_missing_deadline | CP 09/26: Interconexões Catalunha
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 927;

-- id_edital=926 | review_missing_deadline | CP 10/26: Pró PET (Pesquisa-Ensino-Extensão)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 926;

-- id_edital=925 | hidden_institutional | CP 11/26: SEURS
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 925;

-- id_edital=924 | visible_current | EDITAL DE CHAMADA PÚBLICA FAPESC N.º 14/2026 PROGRAMA MULHERES+TEC 5ª EDIÇÃO
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-05-21).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 924;

-- id_edital=923 | visible_current | EDITAL DE CHAMADA PÚBLICA FAPESC N.º 15/2026 PRÊMIO INOVAÇÃO CATARINENSE PROFESS
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-06-30).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 923;

-- id_edital=922 | visible_current | EDITAL DE CHAMADA PÚBLICA FAPESC N.º 16/2026 PROGRAMA DE CIÊNCIA, TECNOLOGIA E I
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-06-22).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 922;

-- id_edital=921 | visible_current | EDITAL DE CHAMADA PÚBLICA FAPESC N.º 18/2026 PROEVENTOS 2027 — FASE I
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-05-20).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 921;

-- id_edital=920 | hidden_expired | EDITAL DE CHAMADA PÚBLICA FAPESC/SEA N.º 19/2026 PROGRAMA DE APOIO AO DESENVOLVI
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 920;

-- id_edital=919 | hidden_expired | EDITAL SUPLEMENTAR FAPESC N.º 20/2026 À CHAMADA TRANSNACIONAL CONJUNTA BIODIVTRA
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 919;

-- id_edital=918 | visible_current | EDITAL SUPLEMENTAR FAPESC N.º 21/2026 À CHAMADA TRANSNACIONAL CONJUNTA WATER4ALL
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-05-25).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 918;

-- id_edital=917 | hidden_institutional | EDITAL DE CHAMADA PÚBLICA FAPESC/JUCESC N.º 23/2026 PROGRAMA ESTADUAL DE MODERNI
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 917;

-- id_edital=916 | hidden_institutional | EDITAL DE CHAMADA PÚBLICA FAPESC/CIASC N.º 22/2026 PROGRAMA DE INOVAÇÃO DO CIASC
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 916;

-- id_edital=915 | visible_current | EDITAL DE CHAMADA PÚBLICA FAPESC N.º 24/2026 PROGRAMA NASCER DE PRÉ-INCUBAÇÃO DE
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-06-15).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 915;

-- id_edital=914 | review_missing_deadline | Programa Horizon Europe da Comunidade Europeia - FAPERGS - Fundação de Amparo à 
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 914;

-- id_edital=913 | visible_current | EDITAL FAPERGS 03/2026 - PROGRAMA DE APOIO AOS ECOSSISTEMAS DE INOVAÇÃO - EDIÇÃO
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-07-31).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 913;

-- id_edital=912 | review_missing_deadline | Chamada CONFAP–Brasillinois 2026 - FAPERGS - Fundação de Amparo à pesquisa do Es
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 912;

-- id_edital=911 | visible_current | EDITAL FAPERGS 04/2026 - PROBIC/PROBITI (Edição 2026 - 2028) - FAPERGS - Fundaçã
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-06-15).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 911;

-- id_edital=910 | visible_current | FAPERGS - Fundação de Amparo à pesquisa do Estado do RS
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-05-20).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 910;

-- id_edital=909 | hidden_resultado | FAPERGS - Fundação de Amparo à pesquisa do Estado do RS
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 909;

-- id_edital=908 | hidden_institutional | Guias Relacionados
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["continuous_flow", "institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 908;

-- id_edital=907 | hidden_institutional | Guias Relacionados
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 907;

-- id_edital=906 | hidden_institutional | Guias passo a passo
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 906;

-- id_edital=905 | hidden_institutional | Guias passo a passo
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 905;

-- id_edital=904 | hidden_institutional | Guias Relacionados
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 904;

-- id_edital=903 | visible_recent_strong_signal | Guias passo a passo
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 903;

-- id_edital=902 | hidden_resultado | Auxílios e Bolsas
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 902;

-- id_edital=901 | hidden_historical | EU Aeronautics Industry
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 901;

-- id_edital=900 | review_missing_deadline | European Network of Defence-related Regions
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 900;

-- id_edital=899 | review_missing_deadline | SAFE | Security Action for Europe
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 899;

-- id_edital=898 | review_missing_deadline | BraveTech EU
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 898;

-- id_edital=897 | review_missing_deadline | Military Mobility
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 897;

-- id_edital=896 | review_missing_deadline | Introducing the White Paper for European Defence and the ReArm Europe Plan- Read
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 896;

-- id_edital=895 | review_missing_deadline | EU Defence Industry
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 895;

-- id_edital=894 | review_missing_deadline | The EU Observatory of Critical Technologies
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 894;

-- id_edital=893 | review_missing_deadline | Research, Development and Innovation
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 893;

-- id_edital=892 | review_missing_deadline | Entrepreneurship
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 892;

-- id_edital=891 | hidden_historical | SSA | Europe''s Eyes on Space
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 891;

-- id_edital=890 | review_missing_deadline | IRIS² | Secure Connectivity
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 890;

-- id_edital=889 | review_missing_deadline | EU Space
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 889;

-- id_edital=888 | hidden_historical | Transition Pathway
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 888;

-- id_edital=887 | hidden_historical | Targeted consultation on EU Space Law
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 887;

-- id_edital=886 | review_missing_deadline | Latest news
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 886;

-- id_edital=885 | review_missing_deadline | Consultation to contribute to the Defence Omnibus Simplification Proposal
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 885;

-- id_edital=884 | hidden_historical | Consultation on the new European Defence Industrial Strategy
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 884;

-- id_edital=877 | visible_recent_strong_signal | Transnational Eureka Lightweighting Call – 2026
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 877;

-- id_edital=862 | visible_recent_strong_signal | Eurostars
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 862;

-- id_edital=861 | review_missing_deadline | Additional opportunities
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 861;

-- id_edital=860 | visible_recent_strong_signal | For Non-European Researchers
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 860;

-- id_edital=859 | visible_recent_strong_signal | ERC Plus Grant
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 859;

-- id_edital=858 | visible_recent_strong_signal | Synergy Grant
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 858;

-- id_edital=857 | visible_recent_strong_signal | Proof of Concept
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 857;

-- id_edital=856 | visible_recent_strong_signal | Advanced Grant
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 856;

-- id_edital=855 | visible_recent_strong_signal | Consolidator Grant
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 855;

-- id_edital=854 | visible_recent_strong_signal | Starting Grant
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 854;

-- id_edital=853 | hidden_institutional | Chamada Pública para Capacitação em Maturidade para Grupos de Pesquisa em ICTs d
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 853;

-- id_edital=852 | hidden_institutional | Chamada Pública Unidades Embrapii nº 01/2025
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 852;

-- id_edital=851 | hidden_institutional | Chamada Pública Centro de Competência Embrapii nº 01/2025
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 851;

-- id_edital=850 | hidden_institutional | Chamada Pública Unidades Embrapii nº 02/2025
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 850;

-- id_edital=849 | hidden_institutional | Chamada Pública Centro de Competência Embrapii nº 02/2025
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 849;

-- id_edital=848 | hidden_institutional | Chamada Pública Centro de Competência Embrapii nº 03/2025
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 848;

-- id_edital=847 | hidden_institutional | Chamada Pública Unidades Embrapii nº 03/2025
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 847;

-- id_edital=846 | hidden_institutional | CHAMADA PÚBLICA 05/2022 PARA CREDENCIAMENTO NO SISTEMA EMBRAPII – Resultado Prel
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 846;

-- id_edital=845 | hidden_institutional | CHAMADA PÚBLICA 04/2022 – Resultado Final
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 845;

-- id_edital=844 | hidden_institutional | CHAMADA PÚBLICA CENTRO DE COMPETÊNCIA 04/2022
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 844;

-- id_edital=843 | hidden_institutional | Chamada Pública 03/2022 – RESULTADO FINAL
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 843;

-- id_edital=842 | hidden_institutional | CHAMADA PÚBLICA CENTRO DE COMPETÊNCIA 02/2022
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 842;

-- id_edital=841 | hidden_institutional | CHAMADA PÚBLICA CENTRO DE COMPETÊNCIA 01/2022
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 841;

-- id_edital=840 | hidden_institutional | CHAMADA PÚBLICA 04/2020 PROGRAMA ROTA 2030 – Resultado Final
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 840;

-- id_edital=839 | hidden_institutional | Chamada Pública 03/2020 – Resultado Final
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 839;

-- id_edital=838 | hidden_institutional | CHAMADA PÚBLICA – 02/2020 – Resultado final
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 838;

-- id_edital=837 | hidden_institutional | CHAMADA PÚBLICA – 01/2020 – Resultado final
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 837;

-- id_edital=836 | hidden_institutional | Chamada Pública 02/2017 – RESULTADO FINAL
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 836;

-- id_edital=835 | hidden_institutional | Chamada Pública 01/2017 – RESULTADO FINAL
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 835;

-- id_edital=834 | hidden_institutional | Chamada Pública 01/2016 – RESULTADO FINAL
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 834;

-- id_edital=833 | hidden_institutional | PROJETOS DE ALTO IMPACTO
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 833;

-- id_edital=832 | review_missing_deadline | Eletronuclear - Página de Licitações e Oportunidades
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 832;

-- id_edital=817 | review_missing_deadline | DE-FOA-0003551
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 817;

-- id_edital=816 | hidden_duplicate | DE-FOA-0003555
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "Link normalizado já visto nesta auditoria.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_link"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 816;

-- id_edital=815 | hidden_duplicate | DE-FOA-0003552
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "Link normalizado já visto nesta auditoria.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_link"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 815;

-- id_edital=814 | hidden_duplicate | DE-FOA-0003554
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "Link normalizado já visto nesta auditoria.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_link"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 814;

-- id_edital=813 | hidden_duplicate | DE-FOA-0003537
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "Link normalizado já visto nesta auditoria.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_link"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 813;

-- id_edital=812 | hidden_duplicate | DE-FOA-0003536
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "Link normalizado já visto nesta auditoria.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_link"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 812;

-- id_edital=811 | hidden_duplicate | DE-FOA-0003557
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "Link normalizado já visto nesta auditoria.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_link"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 811;

-- id_edital=810 | hidden_duplicate | DE-FOA-0003556
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "Link normalizado já visto nesta auditoria.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_link"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 810;

-- id_edital=809 | hidden_duplicate | DE-FOA-0003624
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "Link normalizado já visto nesta auditoria.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_link"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 809;

-- id_edital=808 | hidden_duplicate | DE-FOA-0003623
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "Link normalizado já visto nesta auditoria.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_link"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 808;

-- id_edital=807 | hidden_duplicate | RFI-0000086 — ARPA-E eXCHANGE
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "Link normalizado já visto nesta auditoria.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_link"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 807;

-- id_edital=806 | hidden_duplicate | DE-FOA-0003467
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "Link normalizado já visto nesta auditoria.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_link"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 806;

-- id_edital=805 | hidden_duplicate | RFI-0000095 — ARPA-E eXCHANGE
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "Link normalizado já visto nesta auditoria.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_link"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 805;

-- id_edital=804 | hidden_duplicate | RFI-0000094 — ARPA-E eXCHANGE
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "Link normalizado já visto nesta auditoria.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_link"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 804;

-- id_edital=803 | hidden_historical | FAST
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 803;

-- id_edital=802 | review_missing_deadline | News and Events
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 802;

-- id_edital=801 | hidden_institutional | Frequently Asked Questions
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 801;

-- id_edital=800 | review_missing_deadline | Funding Opportunities
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 800;

-- id_edital=799 | review_missing_deadline | Data Resources
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 799;

-- id_edital=798 | hidden_historical | Data Resources
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 798;

-- id_edital=797 | review_missing_deadline | Portfolio
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 797;

-- id_edital=796 | review_missing_deadline | Portfolio
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 796;

-- id_edital=795 | hidden_historical | Archived Annual Reports
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 795;

-- id_edital=794 | hidden_historical | Success Stories
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 794;

-- id_edital=793 | hidden_historical | Impact Reports
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 793;

-- id_edital=792 | hidden_historical | Impact, Mission, and Goals
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 792;

-- id_edital=791 | review_missing_deadline | Policy Directives
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 791;

-- id_edital=790 | review_missing_deadline | Participating Federal Agencies
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 790;

-- id_edital=789 | review_missing_deadline | Lab to Market Hub
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 789;

-- id_edital=788 | hidden_historical | Protecting U.S. Space Capabilities: Defense Innovation Unit and U.S. Space Force
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 788;

-- id_edital=787 | review_missing_deadline | To Secure U.S. Energy Dominance, the Department of Defense Selects Eligible Comp
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 787;

-- id_edital=786 | hidden_historical | Defense Innovation Unit Launches First CSO Under New Emerging Technology Portfol
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 786;

-- id_edital=785 | hidden_historical | Defense Innovation Unit and DoD Collaborate To Strengthen Synthetic Media Detect
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 785;

-- id_edital=784 | review_missing_deadline | Department of Defense Expands Geothermal Initiative To Support Mission Assurance
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 784;

-- id_edital=783 | review_missing_deadline | Update: DIU Announces Recognized Assessors to Support Blue UAS NDAA Compliance C
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 783;

-- id_edital=782 | review_missing_deadline | DIU, JIATF-401, USNORTHCOM, US ARMY Announce Winner for C-UAS Low-Cost Sensing C
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 782;

-- id_edital=781 | review_missing_deadline | Defense Innovation Unit Announces New Director, Designation as Defense Field Act
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 781;

-- id_edital=780 | review_missing_deadline | Two Contracts Awarded To Modernize Decision-Making for DoW’s Joint Logistics Ent
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 780;

-- id_edital=779 | review_missing_deadline | Projeto Soldado Cidadão
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 779;

-- id_edital=778 | review_missing_deadline | Programa Forças no Esporte e João do Pulo
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 778;

-- id_edital=777 | review_missing_deadline | Ações subsidiárias
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 777;

-- id_edital=776 | review_missing_deadline | Programas Sociais
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 776;

-- id_edital=775 | review_missing_deadline | Empreendimentos Estratégicos de Defesa
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 775;

-- id_edital=774 | hidden_institutional | Programa de Gestão e Desempenho (PGD)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 774;

-- id_edital=773 | hidden_institutional | Consulta Pública ao Inteiro Teor dos Processos de Licitações e Contratos
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 773;

-- id_edital=772 | review_missing_deadline | Programa de Aquisição de Alimentos (PAA) - Agricultura Familiar
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 772;

-- id_edital=771 | review_missing_deadline | Programa de Gestão e Melhoria da Qualidade (PGMQ)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 771;

-- id_edital=770 | hidden_institutional | Ações e Programas
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 770;

-- id_edital=769 | review_missing_deadline | R&D Opportunities
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 769;

-- id_edital=768 | hidden_duplicate | R&D Opportunities
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 768;

-- id_edital=767 | hidden_duplicate | R&D Opportunities
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 767;

-- id_edital=766 | hidden_duplicate | R&D Opportunities
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 766;

-- id_edital=765 | review_missing_deadline | Usage Policy
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 765;

-- id_edital=764 | review_missing_deadline | Microsystems Technology Office
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 764;

-- id_edital=763 | review_missing_deadline | Defense Sciences Office
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 763;

-- id_edital=762 | review_missing_deadline | About DARPA
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 762;

-- id_edital=761 | review_missing_deadline | Ideas Under Incubation
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 761;

-- id_edital=760 | review_missing_deadline | Small Business
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 760;

-- id_edital=759 | review_missing_deadline | Industry
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 759;

-- id_edital=758 | review_missing_deadline | Academia
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 758;

-- id_edital=757 | review_missing_deadline | Contracts Management Office
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 757;

-- id_edital=756 | hidden_institutional | Offices
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 756;

-- id_edital=755 | hidden_duplicate | R&D Opportunities
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 755;

-- id_edital=754 | hidden_expired | premio confap de ciencia tecnologia inovacao professora niede guidon 5 edicao 20
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 754;

-- id_edital=753 | hidden_institutional | premio confap de boas praticas em fomento a ct i 5 edicao 2025
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 753;

-- id_edital=752 | visible_recent_strong_signal | chamada marie sk odowska curie intercambio de pessoal 2026
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 752;

-- id_edital=751 | visible_current | chamada confap brasillinois 2026
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-05-26).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 751;

-- id_edital=750 | visible_recent_strong_signal | chamada nexbio amazonia 2026
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 750;

-- id_edital=749 | hidden_historical | Compras.gov Defesa - Índice de Licitações
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 749;

-- id_edital=748 | hidden_resultado | Chamada Pública CNPq/MCTI/FNDCT Nº 25/2025 - Transporte Aquaviário e Construção 
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 748;

-- id_edital=747 | hidden_resultado | Chamada CNPq/MS-SCTIE-Decit Nº 30/2025 - Pesquisas Estratégicas em Terapias Avan
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 747;

-- id_edital=746 | hidden_resultado | Chamada CNPq/Decit/SCTIE/MS - Nº 32/2025 - Pesquisas Inovadoras para a Saúde das
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 746;

-- id_edital=745 | hidden_resultado | Chamada CNPq Nº 26/2025 Auxílio à Promoção de Eventos Científicos, Tecnológicos 
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 745;

-- id_edital=744 | hidden_resultado | CHAMADA PÚBLICA CNPq/MPA Nº 03/2026 PROGRAMA JOVEM CIENTISTA DA PESCA ARTESANAL 
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 744;

-- id_edital=743 | hidden_expired | Chamada para Pesquisas Inovadoras em Vacinas CNPq/Decit/SCTIE/MS Nº 31/2025
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 743;

-- id_edital=742 | hidden_expired | CNPq/CAPES/IRD Nº 27/2025 Programa de apoio ao Centro Franco-Brasileiro de Biodi
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 742;

-- id_edital=741 | hidden_resultado | Chamada CNPq/Daevs/SVSA/MS Nº 33/2025 - Pesquisa, Extensão e Formação em Epidemi
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 741;

-- id_edital=740 | hidden_institutional | Chamada pública CNPq/MCTI/MEMP N° 05/2026 - Programa de Iniciação ao Empreendedo
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 740;

-- id_edital=739 | hidden_expired | Chamada Nº 28/2025 - Apoio a Projetos de Cooperação CNPq-TUBITAK
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 739;

-- id_edital=738 | hidden_resultado | Chamada Pública MCTI/CNPq Nº 02/2026 Programa de Cooperação Latino-Americana e C
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 738;

-- id_edital=737 | visible_current | Chamada CNPq/MCTI Nº 11/2026 – RENAMA e NAMs
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-07-03).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 737;

-- id_edital=736 | hidden_institutional | Chamada CNPq/MCTI/FNDCT Nº 12/2026 - Programa PCI
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 736;

-- id_edital=735 | visible_current | Chamada CNPq/SETEC/MCTI N° 13/2026 - Apoio a Eventos de Promoção do Empreendedor
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_current", "reason": "Prazo futuro (2026-05-28).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["future_deadline"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 735;

-- id_edital=734 | visible_recent_strong_signal | Edital de Chamamento Público para Credenciamento 01/2020
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 734;

-- id_edital=733 | visible_recent_strong_signal | 基金委通知：一批国际合作交流项目
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 733;

-- id_edital=732 | visible_recent_strong_signal | 基金委通知：可持续发展国际合作科学计划2026年度项目（第一批）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 732;

-- id_edital=731 | review_missing_deadline | 霍英东教育基金会2026年高等院校青年教师基金项目申报通知
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 731;

-- id_edital=730 | review_missing_deadline | 国家重点研发计划：“政府间国际科技创新合作”重点专项2026年度...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 730;

-- id_edital=729 | review_missing_deadline | 科研类通知
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 729;

-- id_edital=728 | hidden_historical | 中国招标投标公共服务平台
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 728;

-- id_edital=727 | hidden_historical | 问题内容：广安祥瑞物业管理有限公司参与广安市主城区城南片区环卫作业采购服务项目(项目编号:511601202100044)公开招标采购活动并中标，提交的投标文件
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 727;

-- id_edital=726 | hidden_historical | 【山西】吉县苹果全产业链--数智蜂箱采购项目
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 726;

-- id_edital=725 | hidden_historical | 问题内容：武乡县中小学校护眼灯具配备项目 （项目编号： 1404292021AGK000005）的政府采购活动中，该项目招标文件中服务部分3项内容、技术部分2项
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 725;

-- id_edital=724 | hidden_historical | 【四川】存在提供虚假材料谋取中标、成交行为。
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 724;

-- id_edital=723 | hidden_historical | 有效期内公告数量统计
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 723;

-- id_edital=722 | hidden_historical | Guide to Programs
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 722;

-- id_edital=721 | hidden_historical | Application and Review Process
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 721;

-- id_edital=720 | visible_recent_strong_signal | Science Fund for Global Challenges and Sustainability
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 720;

-- id_edital=719 | review_missing_deadline | The Research Fund For International Scientists
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 719;

-- id_edital=718 | review_missing_deadline | 国家自然科学基金申请代码
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 718;

-- id_edital=717 | review_missing_deadline | 2026年度国家自然科学基金改革举措
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 717;

-- id_edital=716 | visible_recent_strong_signal | 国家自然科学基金委员会中德科学中心2026年度中德学生与青年学者短期讲习班项目指南 04-29
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 716;

-- id_edital=715 | review_missing_deadline | 2026年度国家自然科学基金项目指南 01-19
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 715;

-- id_edital=714 | review_missing_deadline | 国家自然科学基金委员会医学科学部青年科学基金项目（A类）（原国家杰出青年科学基金项目）注意事项补充说明 03-12
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 714;

-- id_edital=713 | review_missing_deadline | 科技部召开党组会议 部署开展树立和践行正确政绩观学习教育工作
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 713;

-- id_edital=712 | review_missing_deadline | 科技部2025年法治政府建设情况报告
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 712;

-- id_edital=711 | review_missing_deadline | 中国人民银行 科技部 金融监管总局 中国证监会联合召开科技金融工作交流推进会
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 711;

-- id_edital=710 | visible_recent_strong_signal | 科技部党组书记、部长阴和俊出席国家自然科学基金委员会九届四次全委会
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 710;

-- id_edital=709 | review_missing_deadline | 科技部召开2026年全面从严治党工作会议暨警示教育大会
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 709;

-- id_edital=708 | visible_recent_strong_signal | 中国—黑山科技合作委员会第五届例会成功举行
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 708;

-- id_edital=707 | visible_recent_strong_signal | 科技部党组举办树立和践行正确政绩观学习教育读书班暨理论学习中心组学习（扩大）会议
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 707;

-- id_edital=706 | visible_recent_strong_signal | 中国—乌兹别克斯坦政府间合作委员会科技合作分委会第七次会议成功举行
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 706;

-- id_edital=705 | visible_recent_strong_signal | 科技部组织召开科技监督工作座谈会暨2026年重大项目监督检查启动会
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 705;

-- id_edital=704 | review_missing_deadline | 科技部党组传达学习习近平总书记在加强基础研究座谈会上的重要讲话精神
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 704;

-- id_edital=703 | review_missing_deadline | 科技部工作
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 703;

-- id_edital=702 | review_missing_deadline | 科技政策研究课题申报通知
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 702;

-- id_edital=701 | hidden_historical | 关于征集2026年度科技评估国家标准制修订计划项目的通知
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 701;

-- id_edital=700 | visible_recent_strong_signal | 科技部国际合作司关于征集2026年 “中国—新西兰科学家交流计划” 赴新人选的通知
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 700;

-- id_edital=699 | review_missing_deadline | 国家科技基础条件平台中心2026年高层次人才公开招聘公告
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 699;

-- id_edital=698 | hidden_historical | 富阳华润燃气有限公司杭州区域...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 698;

-- id_edital=697 | hidden_historical | 青海省交通运输厅信息中心信息...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 697;

-- id_edital=696 | hidden_historical | 湖北省国土空间规划条例研究变...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 696;

-- id_edital=695 | hidden_historical | 山县2024年中央自然灾害（低温...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 695;

-- id_edital=694 | hidden_historical | 济南市第二分公司智能立库维保...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 694;

-- id_edital=693 | hidden_historical | 2025年五丰上食第三方代宰年度...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 693;

-- id_edital=692 | hidden_historical | 湖南新华新疆窝依莫克风电电力...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 692;

-- id_edital=691 | hidden_historical | 2025年延安新区抖音话题挑战赛...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 691;

-- id_edital=690 | hidden_historical | 津市市文化旅游广电体育局2025...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 690;

-- id_edital=689 | hidden_historical | 新疆轻工职业技术学院短期培训...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 689;

-- id_edital=688 | hidden_historical | 【采购中心结果公示】北京大学...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 688;

-- id_edital=687 | hidden_historical | 天津市武清区人民法院机关天津...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 687;

-- id_edital=686 | hidden_historical | 国投生物能源（铁岭）有限公司...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 686;

-- id_edital=685 | hidden_historical | 书院学生住宿设施采购项目采购...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 685;

-- id_edital=684 | hidden_historical | 混凝土面板硅基可涂覆型防渗新...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 684;

-- id_edital=683 | hidden_historical | 徐州华润电力有限公司 自锁器...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 683;

-- id_edital=682 | hidden_historical | 发电部电石渣采购变更公告
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 682;

-- id_edital=681 | hidden_historical | 关于体操（含艺术体操）、蹦床...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 681;

-- id_edital=680 | hidden_historical | YXZC2025-G1-00429-HCZB-0035...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 680;

-- id_edital=679 | hidden_historical | 大兴机场周边航延餐食水饼供应...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 679;

-- id_edital=678 | hidden_historical | 中国核建中核二三甘肃矿区项目...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 678;

-- id_edital=677 | hidden_historical | 2025-2026年度国际数字化业务...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 677;

-- id_edital=676 | hidden_historical | 机组拦污栅压差测量机理及影响...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 676;

-- id_edital=675 | hidden_historical | 物业服务项目招标公告
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 675;

-- id_edital=674 | hidden_historical | 【中国邮政集团有限公司昆明市...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 674;

-- id_edital=673 | hidden_historical | [淮安区]淮安区复兴镇2026年村...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 673;

-- id_edital=672 | hidden_historical | 广东茂名合和燃气有限公司电白...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 672;

-- id_edital=671 | hidden_historical | 2026年徐州市分公司新城区邮政...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 671;

-- id_edital=670 | hidden_historical | 【应城市中心】孝感市应城市污...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 670;

-- id_edital=669 | hidden_historical | 赛鼎公司-赛鼎公司-赛鼎公司-...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 669;

-- id_edital=668 | hidden_historical | 天津市宝坻区水利工程服务中心...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 668;

-- id_edital=667 | hidden_historical | 哈尔滨工程大学材化与公共分析...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 667;

-- id_edital=666 | hidden_historical | 南华大学附属第一医院心血管提...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 666;

-- id_edital=665 | hidden_historical | 陵水25-1气田开发工程项目评标...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 665;

-- id_edital=664 | hidden_historical | 辽宁城镇供水安全可持续发展示...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 664;

-- id_edital=663 | hidden_historical | 北京市海淀区稻香湖学校教学楼...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 663;

-- id_edital=662 | hidden_historical | 乌石17-2/23-5油田群联合开发...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 662;

-- id_edital=661 | hidden_historical | 利用德国促进贷款建设宝丰县污...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 661;

-- id_edital=660 | hidden_historical | 法开署贷款凌源市集中供热工程...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 660;

-- id_edital=659 | hidden_historical | 启东市城市生命线安全工程（二...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 659;

-- id_edital=658 | hidden_historical | 华润华光（北京）热电有限公司...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 658;

-- id_edital=657 | hidden_historical | [吉安县]登龙中心幼儿园 2025 ...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 657;

-- id_edital=656 | hidden_historical | 福建分公司-中海壳牌惠州三期...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 656;

-- id_edital=655 | hidden_historical | YNQYJ2-2025035：2025年玉溪市...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 655;

-- id_edital=654 | hidden_historical | 宝鸡市陈仓区疾病预防控制中心...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 654;

-- id_edital=653 | hidden_historical | 南京江北新区中央商务区浦滨路...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 653;

-- id_edital=652 | hidden_historical | 2025年度大洼区特殊困难老年人...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 652;

-- id_edital=651 | hidden_historical | 国家发展改革委法规司负责同志就《评标专家和评标专...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 651;

-- id_edital=650 | hidden_historical | 公平竞争审查条例实施办法
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 650;

-- id_edital=649 | hidden_historical | 文山州中医医院利用德国促进贷...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 649;

-- id_edital=648 | hidden_historical | 法开署贷款中法武汉生态示范城...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 648;

-- id_edital=647 | hidden_historical | 利用法开署贷款淄博市供热管网...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 647;

-- id_edital=646 | hidden_historical | 湖南省林业局欧洲投资银行贷款...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 646;

-- id_edital=645 | hidden_historical | 世行贷款中国塑料垃圾减量项目...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 645;

-- id_edital=644 | hidden_historical | 世界银行贷款湖北省低碳农业和...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 644;

-- id_edital=643 | hidden_historical | 长春师范大学易地新建项目（一...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 643;

-- id_edital=642 | hidden_historical | 海东城乡供水安全与保障工程植...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 642;

-- id_edital=641 | hidden_historical | 医疗辅助操作外包服务项目第二...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 641;

-- id_edital=640 | hidden_historical | 大连润滑油研究开发中心API台架试验标包1撤项公告
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 640;

-- id_edital=639 | hidden_historical | 株洲中车时代半导体股份有限公司投影式光刻机采购项...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 639;

-- id_edital=638 | hidden_historical | 宜兴中车时代半导体有限公司自动化硬件设备采购项目...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 638;

-- id_edital=637 | hidden_historical | 博戈橡胶塑料(无锡)有限公司悬置三轴疲劳试验系统采...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 637;

-- id_edital=636 | hidden_historical | 阵列曝光机采购中标结果公告(1)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 636;

-- id_edital=635 | hidden_historical | 真空泵采购中标结果公告(1)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 635;

-- id_edital=634 | hidden_historical | 高温工艺炉采购中标结果公告(1)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 634;

-- id_edital=633 | hidden_historical | 京东方合肥8.5代线模组智能制造项目重新招标澄清或...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 633;

-- id_edital=632 | hidden_historical | 浙江创芯设备采购项目国际招标澄清或变更公告(2)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 632;

-- id_edital=631 | hidden_historical | 上海积塔半导体有限公司特色工艺生产线建设项目国际...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 631;

-- id_edital=630 | hidden_historical | 数控滚齿机重新招标澄清或变更公告(1)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 630;

-- id_edital=629 | hidden_historical | 滚插齿加工机重新招标澄清或变更公告(1)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 629;

-- id_edital=628 | hidden_historical | 窄脉冲vcsel晶圆测试系统采购重新招标澄清或变更公...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 628;

-- id_edital=627 | hidden_historical | 上海立得单中心茂金属聚乙烯催化剂研究开发项目气相...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 627;

-- id_edital=626 | hidden_historical | 珠海京东方晶芯科技有限公司Mini/Micro LED COB显示...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 626;

-- id_edital=625 | hidden_duplicate | 珠海京东方晶芯科技有限公司Mini/Micro LED COB显示...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 625;

-- id_edital=624 | hidden_duplicate | 珠海京东方晶芯科技有限公司Mini/Micro LED COB显示...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 624;

-- id_edital=623 | hidden_duplicate | 珠海京东方晶芯科技有限公司Mini/Micro LED COB显示...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 623;

-- id_edital=622 | hidden_historical | 国务院办公厅关于在政府采购中实施本国产品标准及相关政策的通知
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 622;

-- id_edital=621 | hidden_historical | 关于加快推广远程异地评标的通知(发改办法规〔2025〕807号)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 621;

-- id_edital=620 | hidden_historical | 国家发展改革委新闻发言人就《招标人主体责任履行指引》答记者问
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 620;

-- id_edital=619 | hidden_historical | 国家发展改革委等部门关于印发《招标人主体责任履行指引》的通知
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 619;

-- id_edital=618 | visible_recent_strong_signal | 中广核山东招远核电1号机组核岛顺利浇筑第一罐混凝土 2025-11-18
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 618;

-- id_edital=617 | visible_recent_strong_signal | 中广核浙江三澳核电项目3号机组核岛顺利浇筑第一罐混凝土 2025-11-19
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 617;

-- id_edital=616 | review_missing_deadline | 两会时刻|《学习时报》刊发杨长利署名文章：加快推动清洁能源绿色创新融合发展
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 616;

-- id_edital=615 | review_missing_deadline | 中广核建立了核与辐射安全信息报告和公开制度，各在运核电站均开通核电厂运营安全信息公开平台...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 615;

-- id_edital=614 | review_missing_deadline | “十五五”开新局|20000人齐奋斗！中广核三澳核电项目刷...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 614;

-- id_edital=613 | review_missing_deadline | 新闻直播间：20000人齐奋斗！中广核三澳核电项目刷新进度...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 613;

-- id_edital=612 | review_missing_deadline | 人民日报：中广核辽宁红沿河核电2025年上网电量创历史新...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 612;

-- id_edital=611 | review_missing_deadline | 庞松涛带队参加第二届核能峰会
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 611;

-- id_edital=610 | review_missing_deadline | 中广核浙江三澳核电项目1号机组首次并网发电
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 610;

-- id_edital=609 | review_missing_deadline | 年度上网电量超2326亿千瓦时！中广核电力公布2025年度业...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 609;

-- id_edital=608 | review_missing_deadline | 2026年4·15全民国家安全教育日核安全主场活动首次在粤港...
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 608;

-- id_edital=607 | review_missing_deadline | 中广核宁德核电5号机组核岛安装工程全面开工
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 607;

-- id_edital=606 | review_missing_deadline | 中广核陆丰核电5号机组圆满完成冷试
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 606;

-- id_edital=605 | review_missing_deadline | 中广核三澳核电2号机组热试完成
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 605;

-- id_edital=604 | visible_recent_strong_signal | Research News
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 604;

-- id_edital=603 | review_missing_deadline | First Quarter 2026: Editors'' News Choice Scientists from the Chinese Academy of 
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 603;

-- id_edital=602 | hidden_duplicate | Research News
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 602;

-- id_edital=601 | review_missing_deadline | 关于进一步强调2025年中国科学院院士增选工作纪律的通知
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 601;

-- id_edital=600 | review_missing_deadline | 关于公布2025年中国科学院院士增选有效候选人名单的公告
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 600;

-- id_edital=599 | review_missing_deadline | 关于公布2025年中国科学院院士增选当选院士名单的公告
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 599;

-- id_edital=598 | review_missing_deadline | 以正确政绩观引领关键核心技术攻关 奋力抢占集成电路科技制高点
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 598;

-- id_edital=597 | review_missing_deadline | “驯核师”蔡军
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 597;

-- id_edital=596 | review_missing_deadline | 【新闻联播】丁薛祥在调研基础研究时强调 深入贯彻落实加强基础研究座谈会精神 全面提升基础研究水平和原始创新能力 2026年05月08日
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 596;

-- id_edital=595 | review_missing_deadline | 2026年全国行星科学大会通知（第三号）
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 595;

-- id_edital=594 | review_missing_deadline | 近代物理所举办“基于HIAF前沿核物理国际研讨会”
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 594;

-- id_edital=593 | review_missing_deadline | 汪克强出席第四届中国（安徽）科技创新成果转化交易会及“融合点”行动安徽专场对接会
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 593;

-- id_edital=592 | review_missing_deadline | 【中国科学报】“悟空”号发现宇宙射线加速能量极限的电荷依赖规律
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 592;

-- id_edital=591 | review_missing_deadline | 【新华社】“拉索”在银河系捕捉到新的超级粒子加速器
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 591;

-- id_edital=590 | review_missing_deadline | 【中国科学报】不再单打独斗，“拉索”把做宇宙线的人“拉”到一起
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 590;

-- id_edital=589 | review_missing_deadline | “悟空”号发现宇宙射线加速能量极限的电荷依赖规律
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 589;

-- id_edital=588 | review_missing_deadline | 科研进展|
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 588;

-- id_edital=587 | review_missing_deadline | 丁薛祥在调研基础研究时强调 深入贯彻落实加强基础研究座谈会精神 全面提升基础研究水平和原始创新能力
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 587;

-- id_edital=586 | review_missing_deadline | 卫星创新院举办“卫星筑梦・航天报国”职工演讲比赛
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 586;

-- id_edital=585 | review_missing_deadline | 近代物理所专题学习习近平总书记在加强基础研究座谈会上的重要讲话精神
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 585;

-- id_edital=584 | review_missing_deadline | 物理所研究员靳常青获国际超导材料探索领域最高奖
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 584;

-- id_edital=583 | review_missing_deadline | 电工所承担的国家重点研发计划项目“陆上风电场群全直流发电系统及协同控制技术”通过验收
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 583;

-- id_edital=582 | review_missing_deadline | 工程热物理所等在压缩空气储能压缩机研发方面取得突破
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 582;

-- id_edital=581 | review_missing_deadline | 东莞材料所自研高频软磁纳米晶合金量产交付
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 581;

-- id_edital=580 | review_missing_deadline | 过程工程所安全氢基能源供热示范项目完成工况运行验证
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 580;

-- id_edital=579 | review_missing_deadline | 理化所燃气吸收式空气源热泵供热示范项目实现高效低碳供热
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 579;

-- id_edital=578 | review_missing_deadline | 科技创新发展局
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 578;

-- id_edital=577 | hidden_duplicate | 科研进展
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 577;

-- id_edital=576 | review_missing_deadline | 通知公告
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 576;

-- id_edital=575 | review_missing_deadline | Chamada Pública
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 575;

-- id_edital=574 | review_missing_deadline | CAPES - Página de Editais e Programas
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 574;

-- id_edital=573 | review_missing_deadline | Regulamento
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 573;

-- id_edital=572 | hidden_duplicate | Regulamento
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 572;

-- id_edital=571 | hidden_duplicate | Fundos de investimento em empresas e projetos
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 571;

-- id_edital=570 | hidden_duplicate | Chamada Pública BNDES Fundo Mercado de Acesso
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 570;

-- id_edital=569 | hidden_duplicate | Fundos da série Criatec
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 569;

-- id_edital=568 | hidden_duplicate | Seleção de Gestor do Fundo Nordeste
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 568;

-- id_edital=567 | hidden_duplicate | Seleção de Fundo nos setores aeroespacial, aeronáutico, de defesa e de segurança
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 567;

-- id_edital=566 | hidden_duplicate | Primeira Chamada Multissetorial para a Seleção de Fundos de Investimento
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 566;

-- id_edital=565 | hidden_duplicate | Seleção de Gestor Nacional do Fundo Criatec III
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 565;

-- id_edital=564 | hidden_duplicate | Segunda Chamada Multissetorial para a Seleção de Fundos de Investimento
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 564;

-- id_edital=563 | hidden_duplicate | Seleção de fundos de crédito para Pequenas e Médias Empresas Inovadoras
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 563;

-- id_edital=562 | hidden_duplicate | Seleção de gestor do Fundo de Energia Sustentável
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 562;

-- id_edital=561 | hidden_duplicate | Seleção de gestor do FIDC Debêntures de Infraestrutura
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 561;

-- id_edital=560 | hidden_duplicate | Seleção de Instituição Financeira para Coordenar, Estruturar e Distribuir as cot
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 560;

-- id_edital=559 | hidden_duplicate | Seleção de Fundo de Investimento em Participações no setor de Internet das Coisa
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 559;

-- id_edital=558 | hidden_duplicate | Chamada Pública para seleção de fundos de investimento em participações – Capita
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 558;

-- id_edital=557 | hidden_duplicate | Chamada Pública para Seleção de Gestor para Fundo de Investimento em Participaçõ
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 557;

-- id_edital=556 | hidden_duplicate | Chamada Pública para Seleção de Fundo de Investimento em Participações no Comple
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 556;

-- id_edital=555 | hidden_duplicate | Chamada Pública para Seleção de Fundos com Foco em Mitigação Climática - Chamada
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 555;

-- id_edital=554 | hidden_duplicate | Chamada Pública para Seleção de Fundos de Investimento em Índice de Mercado – Fu
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 554;

-- id_edital=553 | hidden_duplicate | Chamada Pública para Seleção de Fundo de Investimento em Participações de Startu
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 553;

-- id_edital=484 | review_missing_deadline | Responsible supply chain | BAE Systems UK suppliers
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 484;

-- id_edital=483 | review_missing_deadline | Login to your account
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 483;

-- id_edital=482 | review_missing_deadline | New supplier registration (HICX)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 482;

-- id_edital=481 | review_missing_deadline | RETIFICADO Edital Subvenção para Proj Sociais
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 481;

-- id_edital=480 | review_missing_deadline | AVISO - RETIFICAÇÃO EDITAL DE SELEÇÃO PÚBLICA
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 480;

-- id_edital=479 | visible_recent_strong_signal | Inscrições abertas - Edital de Subvenção+Social
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 479;

-- id_edital=478 | review_missing_deadline | Edital Subvenção Econ. Projetos de Impacto Social
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 478;

-- id_edital=477 | review_missing_deadline | Resultado - Seleção Pública de Subvenção Econômica
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 477;

-- id_edital=476 | review_missing_deadline | Lista de entidades inscritas
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 476;

-- id_edital=475 | review_missing_deadline | Badesul divulga projetos contemplados
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 475;

-- id_edital=474 | hidden_expired | Exporta Mais Brasil - E-commerce 2026
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 474;

-- id_edital=473 | review_missing_deadline | Exporta Mais Brasil | Alimentos Funcionais e Suplementos Alimentares 2026
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 473;

-- id_edital=472 | hidden_expired | Consultas e Audiências Públicas
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 472;

-- id_edital=471 | hidden_resultado | Edital de Chamada Pública
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 471;

-- id_edital=470 | review_missing_deadline | ANEEL - dd projetos de pd em energia eletrica
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 470;

-- id_edital=469 | visible_recent_strong_signal | Desenvolvimento, cuidados e educação pré-escolar
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 469;

-- id_edital=468 | hidden_resultado | Demais Projetos
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 468;

-- id_edital=467 | hidden_institutional | 2ª Chamada Pública
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 467;

-- id_edital=466 | hidden_institutional | 1ª Chamada Pública
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 466;

-- id_edital=465 | review_missing_deadline | Pesquisa e Desenvolvimento e Eficiência Energética
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 465;

-- id_edital=464 | visible_recent_strong_signal | Revista de Pesquisa e Desenvolvimento (P&D)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 464;

-- id_edital=463 | visible_recent_strong_signal | Procedimentos dos Programas de Eficiência Energética e de Pesquisa e Desenvolvim
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 463;

-- id_edital=462 | review_missing_deadline | PDI ANEEL
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 462;

-- id_edital=461 | review_missing_deadline | Pesquisa e Desenvolvimento e Eficiência Energética
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 461;

-- id_edital=460 | hidden_duplicate | PDI ANEEL
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 460;

-- id_edital=459 | review_missing_deadline | Programa de Pesquisa, Desenvolvimento e Inovação da ANEEL
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 459;

-- id_edital=458 | visible_recent_strong_signal | Plano de Desenvolvimento da Distribuição
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 458;

-- id_edital=457 | hidden_institutional | Programas Setoriais
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 457;

-- id_edital=456 | hidden_resultado | Programa de Pesquisa, Desenvolvimento e Inovação (PDI)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 456;

-- id_edital=455 | visible_recent_strong_signal | Programa de Eficiência Energética
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 455;

-- id_edital=454 | hidden_institutional | Planejamento de Tecnologia da Informação
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 454;

-- id_edital=453 | visible_recent_strong_signal | Temas Estratégicos do PEQuI
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 453;

-- id_edital=452 | review_missing_deadline | Sandboxes Tarifários
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 452;

-- id_edital=451 | hidden_duplicate | PDI ANEEL
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 451;

-- id_edital=450 | visible_recent_strong_signal | Prêmio ANEEL de Inovação
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 450;

-- id_edital=449 | visible_recent_strong_signal | Guia de Comunicação dos Programas de PDI e EE ANEEL
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 449;

-- id_edital=448 | visible_recent_strong_signal | Guia de Avaliação da Maturidade Tecnológica da ANEEL
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 448;

-- id_edital=447 | hidden_institutional | Chamadas de Projetos de PDI Estratégicos
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 447;

-- id_edital=446 | hidden_historical | Sistemas de Armazenamento de Energia
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 446;

-- id_edital=445 | review_missing_deadline | ANEEL - Call for Projects H2 PDI
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 445;

-- id_edital=444 | review_missing_deadline | ANEEL - adsp2024778 2
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 444;

-- id_edital=443 | hidden_historical | Health And Wellness
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 443;

-- id_edital=442 | hidden_historical | Inclusive Growth
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 442;

-- id_edital=441 | hidden_historical | Nature And Biodiversity
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 441;

-- id_edital=440 | hidden_historical | Sustainable Agriculture
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 440;

-- id_edital=439 | hidden_historical | Circular Economy
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 439;

-- id_edital=438 | hidden_historical | Climate
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 438;

-- id_edital=437 | hidden_historical | Water Stewardship
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Sem prazo futuro, fluxo contínuo ou sinal forte recente.", "confidence": "baixa", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["fallback_hidden"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 437;

-- id_edital=436 | hidden_resultado | Dispensa de Licitação por Valor 04/2023
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 436;

-- id_edital=435 | hidden_institutional | Dispensa de Licitação por Valor 02/2023
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 435;

-- id_edital=434 | hidden_resultado | Dispensa de Licitação por Valor 01/2023
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 434;

-- id_edital=433 | review_missing_deadline | Dispensa de Licitação por valor 04/2024
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 433;

-- id_edital=432 | review_missing_deadline | Dispensa de Licitação por Valor 06/2024
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 432;

-- id_edital=431 | hidden_duplicate | Dispensa de Licitação por Valor 04/2024
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 431;

-- id_edital=430 | hidden_resultado | Dispensa de Licitação por Valor 07/2025
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 430;

-- id_edital=429 | hidden_institutional | Dispensa de Licitação por Valor 06/2025
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 429;

-- id_edital=428 | hidden_institutional | Dispensa de Licitação por Valor 05/2025
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 428;

-- id_edital=427 | hidden_institutional | Dispensa de Licitação por Valor 04/2025
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 427;

-- id_edital=426 | hidden_institutional | Dispensa de Licitação por Valor 03/2025
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 426;

-- id_edital=425 | hidden_resultado | Dispensa de Licitação por Valor 02/2025
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 425;

-- id_edital=424 | hidden_resultado | Dispensa de Licitação por Valor 01/2025
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 424;

-- id_edital=423 | hidden_resultado | Dispensa de Licitação por Valor 05/2026
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 423;

-- id_edital=422 | hidden_historical | Dispensa de Licitação 05/2024
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 422;

-- id_edital=421 | hidden_institutional | Dispensa de Licitação 02/2024
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 421;

-- id_edital=420 | hidden_resultado | Dispensa de Licitação 01/2024
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 420;

-- id_edital=419 | hidden_expired | Dispensa de Licitação 06/2025
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Prazo de envio/inscrição encerrado sem fluxo contínuo.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["expired_deadline"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 419;

-- id_edital=418 | hidden_institutional | Dispensa de Licitação 01/2026
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 418;

-- id_edital=417 | review_missing_deadline | SAGE Fellowship Program
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 417;

-- id_edital=416 | review_missing_deadline | Augmentee Program
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 416;

-- id_edital=415 | review_missing_deadline | Risk-Based Analysis
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 415;

-- id_edital=414 | hidden_historical | Phase III
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 414;

-- id_edital=413 | review_missing_deadline | STRATFI/TACFI
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 413;

-- id_edital=412 | review_missing_deadline | Specific Topic
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 412;

-- id_edital=411 | review_missing_deadline | Open Topic
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 411;

-- id_edital=410 | review_missing_deadline | SBIR/STTR Overview
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 410;

-- id_edital=409 | visible_continuous_flow | INOVA MES (SESI)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_continuous_flow", "reason": "Fluxo contínuo ou chamada permanente.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["continuous_flow"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 409;

-- id_edital=408 | visible_recent_strong_signal | Linhas de Cuidado na Saúde Suplementar SESI e ANS (SESI)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 408;

-- id_edital=407 | hidden_historical | Estudos e Pesquisas em Saúde e Segurança na Indústria (SESI)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_historical", "reason": "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["historical_year"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 407;

-- id_edital=406 | visible_recent_strong_signal | Ecossistemas de Inovação em Saúde – Hubs Regionais (SESI)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 406;

-- id_edital=405 | hidden_institutional | Smart Factory- FINEP (SENAI)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 405;

-- id_edital=404 | hidden_institutional | Smart Factory (SENAI)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 404;

-- id_edital=403 | visible_recent_strong_signal | Rota 2030 Hands-on: Recupera RS (SENAI)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 403;

-- id_edital=402 | visible_recent_strong_signal | MOVER Hands-on: Aprendendo Fazendo (SENAI)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 402;

-- id_edital=401 | visible_recent_strong_signal | Rota 2030 - Projetos Estruturantes (FUNDEP e SENAI)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 401;

-- id_edital=400 | visible_recent_strong_signal | MOVER - Projetos Estruturantes (EMBRAPII e SENAI)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 400;

-- id_edital=399 | visible_recent_strong_signal | MOVER - Aliança de Startups, Pequenas e/ou Médias Empresas (SENAI)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 399;

-- id_edital=398 | visible_recent_strong_signal | MOVER - Aliança Industrial (SENAI)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 398;

-- id_edital=397 | hidden_resultado | Missão Industrial (SENAI)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 397;

-- id_edital=396 | hidden_resultado | Habitats de Inovação (SENAI)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 396;

-- id_edital=395 | visible_recent_strong_signal | Empreendedorismo Industrial - Startup.Tech (SENAI)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 395;

-- id_edital=394 | visible_recent_strong_signal | Empreendedorismo Industrial - Desafio Instituição Âncora (SENAI)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 394;

-- id_edital=393 | visible_recent_strong_signal | Aliança Educacional (SENAI)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 393;

-- id_edital=392 | visible_recent_strong_signal | Saúde Conectada (SESI)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 392;

-- id_edital=391 | visible_recent_strong_signal | Aliança Industrial (SENAI)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 391;

-- id_edital=390 | visible_recent_strong_signal | Projeto Semente (SENAI)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 390;

-- id_edital=389 | review_missing_deadline | Chamada Regional (SENAI) [SENAI/RJ] CONCURSO DE INOVAÇÃO PARA SOLUÇÕES EM EFICIÊ
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 389;

-- id_edital=388 | review_missing_deadline | Agenda.Tech (SENAI) 2026 Chamada: Mapeamento de Oportunidades e Tencologias para
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 388;

-- id_edital=387 | visible_recent_strong_signal | Smart Factory- BNDES (SENAI)
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 387;

-- id_edital=156 | hidden_resultado | Conte com taxas e prazos exclusivos para seu negócio ir mais longe.
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 156;

-- id_edital=155 | hidden_duplicate | Conte com taxas e prazos exclusivos para seu negócio ir mais longe.
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 155;

-- id_edital=154 | hidden_duplicate | Conte com taxas e prazos exclusivos para seu negócio ir mais longe.
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 154;

-- id_edital=153 | hidden_duplicate | Conte com taxas e prazos exclusivos para seu negócio ir mais longe.
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 153;

-- id_edital=152 | hidden_resultado | Cartilha de projeto 2024
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 152;

-- id_edital=151 | hidden_resultado | Regulamento das Linhas Permanentes de Financiamento Municipal
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 151;

-- id_edital=150 | hidden_institutional | Linhas Permanentes de Financiamento Municipal
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 150;

-- id_edital=149 | hidden_duplicate | Linhas Permanentes de Financiamento Municipal
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 149;

-- id_edital=148 | hidden_duplicate | Linhas Permanentes de Financiamento Municipal
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 148;

-- id_edital=147 | hidden_duplicate | Linhas Permanentes de Financiamento Municipal
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 147;

-- id_edital=145 | hidden_institutional | Agronegócio Para empresas e cooperativas que exercem as mais diversas atividades
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 145;

-- id_edital=140 | hidden_institutional | Webinar – Applying to Eurostars: What to consider when writing a proposal
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 140;

-- id_edital=138 | hidden_institutional | 2025 Eurostars call 9 experts list
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 138;

-- id_edital=137 | visible_recent_strong_signal | Eurostars Call 11 for projects – deadline September 2026
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 137;

-- id_edital=135 | review_missing_deadline | Open funding opportunities
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 135;

-- id_edital=134 | review_missing_deadline | Open funding opportunities
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 134;

-- id_edital=133 | review_missing_deadline | Fundo Constitucional de Financiamento do Norte FNOUm fundo do Governo Federal pa
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 133;

-- id_edital=132 | review_missing_deadline | Open funding opportunities
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 132;

-- id_edital=131 | visible_recent_strong_signal | Open call for Network Projects applications
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 131;

-- id_edital=129 | visible_recent_strong_signal | Biotech call – September 2026
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 129;

-- id_edital=128 | visible_recent_strong_signal | Globalstars call with Taiwan 2026
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 128;

-- id_edital=126 | visible_recent_strong_signal | Canada call for projects number 7
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 126;

-- id_edital=124 | visible_recent_strong_signal | Fast Track to the EIC Accelerator ‒ Call 4
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 124;

-- id_edital=123 | visible_recent_strong_signal | Open funding opportunities
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 123;

-- id_edital=122 | visible_recent_strong_signal | Open funding opportunities
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 122;

-- id_edital=120 | visible_recent_strong_signal | Open funding opportunities
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 120;

-- id_edital=119 | visible_recent_strong_signal | Open funding opportunities
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 119;

-- id_edital=117 | hidden_duplicate | Open funding opportunities
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "Link normalizado já visto nesta auditoria.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_link"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 117;

-- id_edital=116 | visible_recent_strong_signal | Investment Readiness
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 116;

-- id_edital=115 | review_missing_deadline | Globalstars
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 115;

-- id_edital=113 | visible_recent_strong_signal | Fast Track to the EIC Accelerator
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 113;

-- id_edital=112 | visible_recent_strong_signal | Network Projects
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 112;

-- id_edital=110 | review_missing_deadline | Innowwide
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 110;

-- id_edital=109 | visible_recent_strong_signal | EIC Business Acceleration Services
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 109;

-- id_edital=107 | visible_recent_strong_signal | EIC Accelerator Open
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 107;

-- id_edital=105 | visible_recent_strong_signal | EIC Accelerator Challenges 2026
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 105;

-- id_edital=104 | visible_recent_strong_signal | EIC Funding opportunities
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 104;

-- id_edital=102 | review_missing_deadline | Data protection notice - EIC Accelerator
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 102;

-- id_edital=101 | visible_recent_strong_signal | EIC STEP Scale Up
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 101;

-- id_edital=99 | visible_recent_strong_signal | EIC Accelerator 2026
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 99;

-- id_edital=98 | visible_recent_strong_signal | The European Capital of Innovation Awards
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 98;

-- id_edital=96 | visible_recent_strong_signal | Advanced Innovation Challenges- Pilot
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 96;

-- id_edital=94 | visible_recent_strong_signal | EIC Pre-Accelerator
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 94;

-- id_edital=93 | visible_recent_strong_signal | STEP Scale Up
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 93;

-- id_edital=91 | visible_recent_strong_signal | EIC Accelerator
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 91;

-- id_edital=89 | visible_recent_strong_signal | EIC Transition
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 89;

-- id_edital=88 | visible_recent_strong_signal | EIC Pathfinder
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 88;

-- id_edital=77 | hidden_resultado | Piscicultura – atividades financiadas – Banco do Nordeste
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 77;

-- id_edital=76 | visible_recent_strong_signal | Pesca – atividades financiadas – Banco do Nordeste
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 76;

-- id_edital=75 | visible_recent_strong_signal | Ovinocaprinocultura – atividades financiadas – Banco do Nordeste
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 75;

-- id_edital=74 | visible_recent_strong_signal | Meio Ambiente – atividades financiadas – Banco do Nordeste
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 74;

-- id_edital=73 | visible_recent_strong_signal | Industrial – atividades financiadas – Banco do Nordeste
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 73;

-- id_edital=72 | hidden_resultado | Grãos – atividades financiadas – Banco do Nordeste
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 72;

-- id_edital=71 | hidden_resultado | Fruticultura – atividades financiadas – Banco do Nordeste
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 71;

-- id_edital=70 | hidden_resultado | Floricultura - Atividades Financiadas - Banco do Nordeste
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 70;

-- id_edital=69 | visible_recent_strong_signal | Educação – atividades financiadas – Banco do Nordeste
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 69;

-- id_edital=68 | visible_recent_strong_signal | Comércio – atividades financiadas – Banco do Nordeste
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 68;

-- id_edital=67 | hidden_resultado | Carcinicultura – atividades financiadas – Banco do Nordeste
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 67;

-- id_edital=66 | visible_recent_strong_signal | Bovinocultura – atividades financiadas – Banco do Nordeste
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 66;

-- id_edital=65 | visible_recent_strong_signal | Apicultura – atividades financiadas – Banco do Nordeste
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 65;

-- id_edital=64 | hidden_resultado | Agricultura Familiar – atividades financiadas – Banco do Nordeste
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 64;

-- id_edital=63 | hidden_resultado | Publicações para Agricultura Familiar - Setor Rural - Produtos e Serviços
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 63;

-- id_edital=62 | review_missing_deadline | Tutorial Cliente - Solicite seu Crédito.pdf
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 62;

-- id_edital=61 | visible_recent_strong_signal | Crédito para Poder Público – financiamento de projetos – Banco do Nordeste
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 61;

-- id_edital=60 | visible_recent_strong_signal | Miniprodutor Rural – crédito e soluções para o campo – Banco do Nordeste
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 60;

-- id_edital=59 | visible_recent_strong_signal | Micro e Pequenas Empresas - Crédito e soluções para o seu negócio - Banco do Nor
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 59;

-- id_edital=58 | visible_recent_strong_signal | Crédito Consignado – empréstimo com desconto em folha para conveniados – Banco d
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 58;

-- id_edital=57 | hidden_resultado | Empréstimos e Financiamentos - Soluções para você - Banco do Nordeste
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 57;

-- id_edital=56 | hidden_resultado | Atividades Financiadas – setores apoiados – Banco do Nordeste
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 56;

-- id_edital=55 | visible_recent_strong_signal | Microcrédito – soluções para pequenos negócios – Banco do Nordeste
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 55;

-- id_edital=54 | visible_recent_strong_signal | Rural – crédito e soluções para o campo – Banco do Nordeste
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 54;

-- id_edital=53 | hidden_resultado | Linhas Permanentes Saiba mais sobre as linhas de financiamento para os município
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 53;

-- id_edital=52 | hidden_expired | Entre em contato
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Registro marcado ativo=false.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["ativo_false"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 52;

-- id_edital=51 | hidden_institutional | Não apenas prover o crédito, mas mensurar o seu impacto
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 51;

-- id_edital=50 | visible_recent_strong_signal | Se é novo para sua empresa, é inovação para o BDMG.
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 50;

-- id_edital=49 | hidden_resultado | No BDMG, você tem mais vantagens.
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 49;

-- id_edital=48 | hidden_resultado | Financie o desenvolvimento de sua Grande Empresa com opções de crédito diferenci
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 48;

-- id_edital=47 | hidden_resultado | Financie o desenvolvimento de sua Média Empresa com opções de crédito diferencia
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 47;

-- id_edital=46 | hidden_resultado | Conte com taxas e prazos exclusivos para seu negócio ir mais longe.
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 46;

-- id_edital=45 | hidden_duplicate | Conte com taxas e prazos exclusivos para seu negócio ir mais longe.
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 45;

-- id_edital=44 | hidden_institutional | Documentação BDMG
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 44;

-- id_edital=43 | visible_recent_strong_signal | Eventos
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 43;

-- id_edital=42 | visible_recent_strong_signal | Notícias
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 42;

-- id_edital=41 | visible_recent_strong_signal | Sala de Imprensa
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 41;

-- id_edital=40 | hidden_institutional | Licitações e Contratos
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 40;

-- id_edital=39 | hidden_duplicate | Licitações e Contratos
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 39;

-- id_edital=38 | visible_recent_strong_signal | Licitações e Contratos
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 38;

-- id_edital=37 | hidden_institutional | Trabalhe no BDMG e construa o futuro de Minas Gerais!
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 37;

-- id_edital=36 | visible_recent_strong_signal | Conhecimento
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 36;

-- id_edital=35 | visible_recent_strong_signal | Proteção de dados e Privacidade
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 35;

-- id_edital=34 | visible_recent_strong_signal | Segurança da Informação e Cibernética
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 34;

-- id_edital=33 | visible_recent_strong_signal | Responsabilidade Social, Ambiental e Climática
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 33;

-- id_edital=32 | visible_recent_strong_signal | Nossa Essência
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 32;

-- id_edital=31 | visible_recent_strong_signal | Atuação
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 31;

-- id_edital=30 | visible_recent_strong_signal | Sobre o BDMG
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "visible_recent_strong_signal", "reason": "Publicação recente (12m) com sinal forte de oportunidade.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["recent_strong"], "source_recommendation": "manter_ativa"}'::jsonb), atualizado_em = now() WHERE id_edital = 30;

-- id_edital=29 | hidden_institutional | O LabAgroMinas é um Programa desenvolvido em parceria entre o BDMG e a Embrapa C
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 29;

-- id_edital=28 | review_missing_deadline | English
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 28;

-- id_edital=27 | hidden_institutional | Correspondentes Bancários
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 27;

-- id_edital=26 | review_missing_deadline | Programa Nacional de Fortalecimento da Agricultura Familiar
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 26;

-- id_edital=25 | hidden_institutional | PRONAF A
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 25;

-- id_edital=24 | review_missing_deadline | Renegociação de Dívidas
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 24;

-- id_edital=23 | hidden_institutional | Financiamento de Veículo Produtor Rural
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 23;

-- id_edital=22 | review_missing_deadline | Máquinas e Equipamentos
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 22;

-- id_edital=21 | review_missing_deadline | Energia Verde
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 21;

-- id_edital=20 | review_missing_deadline | FNO Biodiversidade
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 20;

-- id_edital=19 | review_missing_deadline | Giro Produtor Rural
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 19;

-- id_edital=18 | review_missing_deadline | Crédito e Financiamentos
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 18;

-- id_edital=17 | review_missing_deadline | Energia Verde - Não Rural
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 17;

-- id_edital=16 | hidden_duplicate | Giro Produtor Rural
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 16;

-- id_edital=15 | review_missing_deadline | Antecipação de Cartão
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 15;

-- id_edital=14 | review_missing_deadline | Fundo da Marinha Mercante
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 14;

-- id_edital=13 | review_missing_deadline | Amazônia Rural Verde
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 13;

-- id_edital=12 | hidden_duplicate | Renegociação de Dívidas
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_duplicate", "reason": "hash_deduplicacao duplicado.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["duplicate_hash"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 12;

-- id_edital=11 | review_missing_deadline | Capital de Giro
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 11;

-- id_edital=10 | hidden_institutional | Relatórios do FNO
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_institutional", "reason": "Sinais de página institucional (home, conduta, governança, etc.).", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["institutional"], "source_recommendation": "precisa_melhoria_crawler"}'::jsonb), atualizado_em = now() WHERE id_edital = 10;

-- id_edital=9 | review_missing_deadline | Plano Safra
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 9;

-- id_edital=8 | review_missing_deadline | BNDES Automático - Projeto de Investimento Não Rural
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 8;

-- id_edital=7 | hidden_resultado | BNDES Automático - Linha Projeto deInvestimento Rural
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_resultado", "reason": "Resultado/homologação/ata sem chamada ativa associada.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["resultado"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 7;

-- id_edital=6 | review_missing_deadline | BNDES Finame
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 6;

-- id_edital=5 | review_missing_deadline | FUNGENTUR
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 5;

-- id_edital=4 | review_missing_deadline | PRONAF
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 4;

-- id_edital=3 | review_missing_deadline | Crédito e financiamento
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 3;

-- id_edital=2 | hidden_expired | Conta PJ
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "hidden_expired", "reason": "Registro marcado ativo=false.", "confidence": "alta", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["ativo_false"], "source_recommendation": "latente"}'::jsonb), atualizado_em = now() WHERE id_edital = 2;

-- id_edital=1 | review_missing_deadline | Empréstimo e microcrédito
-- UPDATE public.edital SET extras = jsonb_set(COALESCE(extras, '{}'::jsonb), '{curadoria_front}', '{"visibility": "review_missing_deadline", "reason": "Oportunidade plausível sem prazo_envio/data_fim registrados.", "confidence": "media", "checked_at": "2026-05-20T22:39:57Z", "rule_version": "editais_visibility_v1", "signals": ["missing_deadline"], "source_recommendation": "manter_com_curadoria"}'::jsonb), atualizado_em = now() WHERE id_edital = 1;
