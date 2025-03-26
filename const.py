# const.py

protein_level_identifier_map = {
    "ANO3": "(NP_113606)",
    "GNAL": "(NP_001135811)",
    "KMT2B": "(NP_055542)",
    "TOR1A": "(NP_000104)",
    "THAP1": "(NP_060575)",
    "SLC30A10": "(NP_061183)",
    "ATP13A2": "(NP_071372)",
    "DJ1": "(NP_009193)",
    "DNAJC6": "(NP_001243793)",
    "FBXO7": "(NP_036311)",
    "LRRK2": "(NP_940980)",
    "PINK1": "(NP_115785)",
    "PARKIN": "(NP_004553)",
    "SNCA": "(NP_000336)",
    "SYNJ1": "(NP_982271)",
    "VPS35": "(NP_060676)",
    "PNKD": "(NP_056303)",
    "PRRT1": "(NP_145239)",
    "SLC2A1": "(NP_006507)",
    "PDGFB": "(NP_002599)",
    "PDGFRB": "(NP_002600)",
    "SLC20A2": "(NP_006740)",
    "XPR1": "(NP_004727)",
    "PRKRA": "(NP_003681)",
    "DCTN1": "(NP_004073)",
    "KCNA1": "(NP_000208)",
    "MYORG": "(NP_065753)",
    "ADCY5": "(NP_899200)",
    "NKX2-1": "(NP_001073136)",
    "PDE10A": "(NP_001124162)",
    "HPCA": "(NP_002134)",
    "GCH1": "(NP_000152)",
    "QDPR": "(NP_000311)",
    "SLC6A3": "(NP_001035)",
    "SLC1A3": "(NP_004163)",
    "REEP1": "(NP_075063)",
    "PRRT2": "(NP_001243371)"
}

cdna_level_identifier_map = {
    "ANO3": "(NM_031418)",
    "GNAL": "(NM_001142339)",
    "KMT2B": "(NM_014727)",
    "TOR1A": "(NM_000113)",
    "THAP1": "(NM_018105)",
    "SLC30A10": "(NM_018713)",
    "ATP13A2": "(NM_022089)",
    "DJ1": "(NM_007262)",
    "DNAJC6": "(NM_001256864)",
    "FBXO7": "(NM_012179)",
    "LRRK2": "(NM_198578)",
    "PINK1": "(NM_032409)",
    "PARKIN": "(NM_004562)",
    "SNCA": "(NM_000345)",
    "SYNJ1": "(NM_203446)",
    "VPS35": "(NM_018206)",
    "PNKD": "(NM_015488)",
    "PRRT1": "(NM_145239)",
    "SLC2A1": "(NM_006516)",
    "PDGFB": "(NM_002608)",
    "PDGFRB": "(NM_002609)",
    "SLC20A2": "(NM_006749)",
    "XPR1": "(NM_004736)",
    "PRKRA": "(NM_003690)",
    "DCTN1": "(NM_004082)",
    "KCNA1": "(NM_000217)",
    "MYORG": "(NM_020702)",
    "ADCY5": "(NM_183357)",
    "NKX2-1": "(NM_001079668)",
    "PDE10A": "(NM_001130690)",
    "HPCA": "(NM_002143)",
    "GCH1": "(NM_000161)",
    "QDPR": "(NM_000320)",
    "SLC6A3": "(NM_001044)",
    "SLC1A3": "(NM_004172)",
    "REEP1": "(NM_022912)",
    "PRRT2": "(NM_001256442)"
}

phosphorylation_activity_map = {
    "p.Tyr1699Cys": {
        "Mean": "6,67 ± 2,36",
        "Interpretation": "strongly activating"
    },
    "p.Asn1437His": {
        "Mean": "5,93 ± 2,34",
        "Interpretation": "strongly activating"
    },
    "p.Arg1441Gly": {
        "Mean": "3,92 ± 0,98",
        "Interpretation": "strongly activating"
    },
    "p.Ile2020Thr": {
        "Mean": "3,50 ± 0,87",
        "Interpretation": "strongly activating"
    },
    "p.Arg1441Ser": {
        "Mean": "3,15 ± 0,55",
        "Interpretation": "strongly activating"
    },
    "p.Arg1441Cys": {
        "Mean": "2,74 ± 1,02",
        "Interpretation": "moderatly activating"
    },
    "p.Gly2385Arg": {
        "Mean": "1,75 ± 0,53",
        "Interpretation": "mildly activating"
    },
    "p.Ser973Asn": {
        "Mean": "1,74 ± 1,08",
        "Interpretation": "mildly activating"
    },
    "p.Gly2019Ser": {
        "Mean": "1,74 ± 0,70",
        "Interpretation": "mildly activating"
    },
    "p.Gln923His": {
        "Mean": "1,44 ± 0,60",
        "Interpretation": "not activating"
    },
    "p.Ala211Val": {
        "Mean": "1,28 ± 0,33",
        "Interpretation": "not activating"
    },
    "p.Thr2356Ile": {
        "Mean": "1,12 ± 0,48",
        "Interpretation": "not activating"
    },
    "p.Lys616Arg": {
        "Mean": "1,05 ± 0,67",
        "Interpretation": "not activating"
    },
    "p.Ala1464Gly": {
        "Mean": "1,04 ± 0,31",
        "Interpretation": "not activating"
    },
    "p.Arg1441His": {
        "Mean": "0,97 ± 0,49",
        "Interpretation": "not activating"
    },
    "p.Arg1725Gln": {
        "Mean": "0,84 ± 0,38",
        "Interpretation": "not activating"
    },
    "p.Asp2175His": {
        "Mean": "0,82 ± 0,20",
        "Interpretation": "not activating"
    },
    "p.Lys544Glu": {
        "Mean": "0,82 ± 0,48",
        "Interpretation": "not activating"
    },
    "p.Gln1823Lys": {
        "Mean": "0,81 ± 0,15",
        "Interpretation": "not activating"
    },
    "p.Pro755Leu": {
        "Mean": "0,80 ± 0,34",
        "Interpretation": "not activating"
    },
    "p.Ile2012Thr": {
        "Mean": "0,76 ± 0,36",
        "Interpretation": "not activating"
    },
    "p.Leu2439Ile": {
        "Mean": "0,70 ± 0,19",
        "Interpretation": "not activating"
    },
    "p.Ile1371Val": {
        "Mean": "0,66 ± 0,32",
        "Interpretation": "not activating"
    },
    "p.Ile1991Val": {
        "Mean": "0,53 ± 0,21",
        "Interpretation": "not activating"
    },
    "p.Met1869Thr": {
        "Mean": "0,43 ± 0,15",
        "Interpretation": "reduced"
    },
    "p.Ser1508Arg": {
        "Mean": "0,24 ± 0,15",
        "Interpretation": "reduced"
    },
    "p.Glu10Lys": {
        "Mean": "1,09 ± 0.32",
        "Interpretation": "not activating"
    },
    "p.Met100Thr": {
        "Mean": "1,44 ± 0,34",
        "Interpretation": "not activating"
    },
    "p.His115Pro": {
        "Mean": "1,31 ± 0,45",
        "Interpretation": "not activating"
    },
    "p.Leu119Pro": {
        "Mean": "0,89 ± 0.28",
        "Interpretation": "not activating"
    },
    "p.Leu153Trp": {
        "Mean": "1,41 ± 0,27",
        "Interpretation": "not activating"
    },
    "p.Met262Val": {
        "Mean": "0,89 ± 0,42",
        "Interpretation": "not activating"
    },
    "p.Glu334Lys": {
        "Mean": "1,82 ± 0,94",
        "Interpretation": "mildly activating "
    },
    "p.Asn363Ser": {
        "Mean": "1,03 ± 0,54",
        "Interpretation": "not activating"
    },
    "p.Ile388Thr": {
        "Mean": "0,72 ± 0,27",
        "Interpretation": "not activating"
    },
    "p.Ala419Val": {
        "Mean": "1,80 ± 0,69",
        "Interpretation": "mildly activating "
    },
    "p.Ala459Ser": {
        "Mean": "1,17 ± 0,48",
        "Interpretation": "not activating"
    },
    "p.Asp478Tyr": {
        "Mean": "1,39 ± 0,40",
        "Interpretation": "not activating"
    },
    "p.Ile479Val": {
        "Mean": "1,15 ± 0,31",
        "Interpretation": "not activating"
    },
    "p.Asn551Lys": {
        "Mean": "0,62 ± 0,38",
        "Interpretation": "not activating"
    },
    "p.Met712Val": {
        "Mean": "0,89 ± 0,66",
        "Interpretation": "not activating"
    },
    "p.Ser722Asn": {
        "Mean": "0,74 ± 0,29",
        "Interpretation": "not activating"
    },
    "p.Ile723Val": {
        "Mean": "0,82 ± 0,44",
        "Interpretation": "not activating"
    },
    "p.Arg767His": {
        "Mean": "1,16 ± 0,98",
        "Interpretation": "not activating"
    },
    "p.Thr776Met": {
        "Mean": "0,89 ± 0,78",
        "Interpretation": "not activating"
    },
    "p.Arg792Lys": {
        "Mean": "1,46 ± 0,83",
        "Interpretation": "not activating"
    },
    "p.Arg793Met": {
        "Mean": "0,81 ± 0,18",
        "Interpretation": "not activating"
    },
    "p.Ile810Val": {
        "Mean": "0,83 ± 0,51",
        "Interpretation": "not activating"
    },
    "p.Ser865Phe": {
        "Mean": "1,08 ± 0.67",
        "Interpretation": "not activating"
    },
    "p.Ser885Asn": {
        "Mean": "1,50 ± 0,94",
        "Interpretation": "mildly activating "
    },
    "p.Cys925Tyr": {
        "Mean": "1,01 ± 0.23",
        "Interpretation": "not activating"
    },
    "p.Gln930Arg": {
        "Mean": "1,08 ± 0,40",
        "Interpretation": "not activating"
    },
    "p.Asp944Val": {
        "Mean": "0,83 ± 0,17",
        "Interpretation": "not activating"
    },
    "p.Arg981Lys": {
        "Mean": "1,29 ± 0,63",
        "Interpretation": "not activating"
    },
    "p.Ser1007Thr": {
        "Mean": "0,84 ± 0,40",
        "Interpretation": "not activating"
    },
    "p.Arg1067Gln": {
        "Mean": "2,29 ± 1,11",
        "Interpretation": "moderatly activating "
    },
    "p.Ser1096Cys": {
        "Mean": "0,93 ± 0,30",
        "Interpretation": "not activating"
    },
    "p.Gln1111His": {
        "Mean": "0,78 ± 0,25",
        "Interpretation": "not activating"
    },
    "p.Ile1122Val": {
        "Mean": "0,60 ± 0,25",
        "Interpretation": "not activating"
    },
    "p.Lys1138Glu": {
        "Mean": "1,10 ± 0,56",
        "Interpretation": "not activating"
    },
    "p.Ala1151Thr": {
        "Mean": "0,60 ± 0,31",
        "Interpretation": "not activating"
    },
    "p.Ile1192Val": {
        "Mean": "0,82 ± 0,27",
        "Interpretation": "not activating"
    },
    "p.Ser1228Thr": {
        "Mean": "1,05 ± 0,31",
        "Interpretation": "not activating"
    },
    "p.Arg1320Ser": {
        "Mean": "0,77 ± 0,36",
        "Interpretation": "not activating"
    },
    "p.Arg1325Gln": {
        "Mean": "0,88 ± 0,86",
        "Interpretation": "not activating"
    },
    "p.Arg1398His": {
        "Mean": "1,17 ± 0,29",
        "Interpretation": "not activating"
    },
    "p.Ala1442Pro": {
        "Mean": "3,11 ± 0,68",
        "Interpretation": "strongly activating "
    },
    "p.Val1447Met": {
        "Mean": "3,07 ± 0,95",
        "Interpretation": "strongly activating "
    },
    "p.Lys1468Glu": {
        "Mean": "1,27 ± 0,42",
        "Interpretation": "not activating"
    },
    "p.Ser1508Gly": {
        "Mean": "0,85 ± 0,21",
        "Interpretation": "not activating"
    },
    "p.Arg1514Gly": {
        "Mean": "0,88 ± 0,00",
        "Interpretation": "not activating"
    },
    "p.Arg1514Gln": {
        "Mean": "0,95 ± 0,48",
        "Interpretation": "not activating"
    },
    "p.Pro1542Ser": {
        "Mean": "0,93 ± 0,27",
        "Interpretation": "not activating"
    },
    "p.Ala1589Ser": {
        "Mean": "0,11 ± 0,08",
        "Interpretation": "reduced"
    },
    "p.Val1613Ala": {
        "Mean": "0,66 ± 0,08",
        "Interpretation": "not activating"
    },
    "p.Arg1628Cys": {
        "Mean": "0,87 ± 0,26",
        "Interpretation": "not activating"
    },
    "p.Arg1628Pro": {
        "Mean": "0,43 ± 0,38",
        "Interpretation": "reduced"
    },
    "p.Met1646Thr": {
        "Mean": "1,00 ± 0,52",
        "Interpretation": "not activating"
    },
    "p.Arg1677Ser": {
        "Mean": "0,91 ± 0,25",
        "Interpretation": "not activating"
    },
    "p.Arg1728Leu": {
        "Mean": "1,91 ± 0,54",
        "Interpretation": "mildly activating "
    },
    "p.Arg1728His": {
        "Mean": "2,32 ± 0,59",
        "Interpretation": "moderatly activating "
    },
    "p.Ser1761Arg": {
        "Mean": "3,99 ± 1,91",
        "Interpretation": "strongly activating"
    },
    "p.Leu1795Phe": {
        "Mean": "4,70 ± 1,59",
        "Interpretation": "strongly activating"
    },
    "p.Gln1823His": {
        "Mean": "0,81 ± 0,15",
        "Interpretation": "not activating"
    },
    "p.Arg1941His": {
        "Mean": "0,21 ± 0,21",
        "Interpretation": "reduced"
    },
    "p.Tyr2006His": {
        "Mean": "1,13 ± 0,28",
        "Interpretation": "not activating"
    },
    "p.Thr2031Ser": {
        "Mean": "1,00 ± 0,49",
        "Interpretation": "not activating"
    },
    "p.Asn2081Asp": {
        "Mean": "1,59 ± 0,23",
        "Interpretation": "mildly activating "
    },
    "p.Thr2141Met": {
        "Mean": "0,53 ± 0,40",
        "Interpretation": "not activating"
    },
    "p.Arg2143Met": {
        "Mean": "0,65 ± 0,22",
        "Interpretation": "not activating"
    },
    "p.Tyr2189Cys": {
        "Mean": "0,81 ± 0,26",
        "Interpretation": "not activating"
    },
    "p.Asn2308Asp": {
        "Mean": "1,09 ± 0,40",
        "Interpretation": "not activating"
    },
    "p.Asn2313Ser": {
        "Mean": "0,85 ± 0,39",
        "Interpretation": "not activating"
    },
    "p.Ser2350Ile": {
        "Mean": "0,98 ± 0,30",
        "Interpretation": "not activating"
    },
    "p.Val2390Met": {
        "Mean": "0,35 ± 0,11",
        "Interpretation": "reduced"
    },
    "p.Met2397Thr": {
        "Mean": "1,00 ± 0,33",
        "Interpretation": "not activating"
    },
    "p.Leu2466His": {
        "Mean": "0,72 ± 0,22",
        "Interpretation": "not activating"
    },
    "p.Thr2494Ile": {
        "Mean": "0,44 ± 0,19",
        "Interpretation": "reduced"
    },
    "p.Phe1700Leu": {
        "Mean": "3,9 ± 1,3",
        "Interpretation": "strongly activating"
    }
}

chromosomes = {
  'chr1': 1, 'chr2': 2, 'chr3': 3, 'chr4': 4, 'chr5': 5, 'chr6': 6,
  'chr7': 7, 'chr8': 8, 'chr9': 9, 'chr10': 10, 'chr11': 11, 'chr12': 12,
  'chr13': 13, 'chr14': 14, 'chr15': 15, 'chr16': 16, 'chr17': 17,
  'chr18': 18, 'chr19': 19, 'chr20': 20, 'chr21': 21, 'chr22': 22,
  'chrX': 23, 'chrY': 24, 'chrM': 25
}

EXCEL_DIRECTORY = "excel"

# Значение по умолчанию для отсутствующих симптомов
DEFAULT_VALUE = "-99"

all_features = [
"ethnicity",
"country",
"sex",
"aao",
"duration",
"age_dx",
"ataxia_sympt",
"ataxia_ictal_sympt",
"ataxia_interictal_sympt",
"limb_ataxia_hp:0002070",
"limb_ataxia_ictal_sympt",
"limb_ataxia_interictal_sympt",
"gait_ataxia_hp:0002066",
"gait_ataxia_ictal_sympt",
"gait_ataxia_interictal_sympt",
"vertigo_hp:0002321",
"vertigo_ictal_sympt",
"vertigo_interictal_sympt",
"nausea_hp:0002018",
"nausea_ictal_sympt",
"nausea_interictal_sympt",
"dysarthria_hp:0001260",
"dysarthria_ictal_sympt",
"dysarthria_interictal_sympt",
"diplopia_hp:0000651",
"diploplia_ictal_sympt",
"diploplia_interictal_sympt",
"tinnitus_hp:0000360",
"tinnitus_ictal_sympt",
"tinnitus_interictal_sympt",
"dystonia_hp:0001332",
"dystonia_ictal_sympt",
"dystonia_interictal_sympt",
"hemiplegia_hp:0002301",
"hemiplegia_ictal_sympt",
"hemiplegia_interictal_sympt",
"headache_hp:0002315",
"headache_ictal_sympt",
"headache_interictal_sympt",
"migraine_hp:0002076",
"migraine_ictal_sympt",
"migraine_interictal_sympt",
"nystagmus_hp:0000639",
"nystagmus_ictal_sympt",
"nystagmus_interictal_sympt",
"muscle_weakness_hp:0003324",
"muscle_weakness_ictal_sympt",
"muscle_weakness_interictal_sympt",
"fatigue_hp:0012378",
"fatigue_ictal_sympt",
"fatigue_interictal_sympt",
"tonic_upgaze_sympt",
"tonic_upgaze_ictal_sympt",
"tonic_upgaze_interictal_sympt",
"cognitive_impairment_hp:0100543",
"cognitive_impairment_ictal_sympt",
"cognitive_impairment_interictal_sympt",
"subdomain_cognitive_impairment_sympt",
"myokymia_hp:0002411",
"myokymia_ictal_sympt",
"myokymia_interictal_sympt",
"neuromyotonia_ictal_sympt",
"neuromyotonia_interictal_sympt",
"choreoathetosis_hp:0001266",
"choreoathetosis_ictal_sympt",
"choreoathetosis_interictal_sympt",
"visual_blurring_hp:0000622",
"visual_blurring_ictal_sympt",
"visual_blurring_interictal_sympt",
"cerebellar_atrophy_hp:0001272",
"depression_hp:0000716",
"depression_ictal_sympt",
"depression_interictal_sympt",
"rigidity_hp:0002063",
"rigidity_ictal_sympt",
"rigidity_interictal_sympt",
"vomiting_hp:0002013",
"vomiting_ictal_sympt",
"vomiting_interictal_sympt",
"seizures_hp:0001250",
"seizures_ictal_sympt",
"seizures_interictal_sympt",
"tremor_hp:0001337",
"tremor_ictal_sympt",
"tremor_interictal_sympt",
"spasticity_hp:0001257",
"spasticity_ictal_sympt",
"spasticity_interictal_sympt",
"muscular_hypotonia_hp:0001252",
"muscular_hypotonia_ictal_sympt",
"muscular_hypotonia_interictal_sympt",
"hypertonia_hp:0001276",
"hypertonia_ictal_sympt",
"hypertonia_interictal_sympt",
"muscle_cramps_sympt",
"muscle_cramps_ictal_sympt",
"muscle_cramps_interictal_sympt",
"upper_motor_neuron_dysfunction_hp:0002493",
"upper_motor_neuron_dysfunction_ictal_sympt",
"upper_motor_neuron_dysfunction_interictal_sympt",
"muscle_stiffness_hp:0003552",
"muscle_stiffness_hp:0003552_sympt",
"muscle_stiffness_hp:0003552_sympt.1",
"dizziness_hp:0002321",
"dizziness_ictal_sympt",
"dizziness_interictal_sympt",
"skeletal_muscle_hypertrophy_hp:0003712",
"skeletal_muscle_hypertrophy_ictal_sympt",
"skeletal_muscle_hypertrophy_interictal_sympt",
"respiratory_distress_hp:0002098",
"respiratory_distress_ictal_sympt",
"respiratory_distress_interictal_sympt",
"episodic_ataxia_hp:0002131",
"muscle_spasms_hp:0002487",
"cerebellar_ataxia_hp:0001251",
"hand_twitching_sympt",
"slurred_speech_hp:0001350",
"visual_disturbance_sympt",
"leg_rigidity_sympt",
"other_sympt",
"ataxia_hp:0001251",
"dystonia_hp:0007325",
"neuromyotonia_sympt",
"hypermetric_saccade_hp:0007338",
"aphasia_hp:0002381",
"jerking_hp:0001336",
"generalized_hyperreflexia_hp:0007034",
"photophobia_hp:0000613",
"phonophobia_hp:0002183",
"aao_other_sympt",
"fatigue_sympt",
"high_blood_lactate_ictal_sympt",
"high_blood_lactate_interictal_sympt",
"high_csf_lactate_sympt",
"encephalopathy_hp:0001298",
"respiratory_distress_sympt",
"global_development_delay_hp:0001263",
"delayed_motor_skills_hp:0002194",
"delayed_cognitive_dev_sympt",
"axonal_neuropathy_hp:0003477",
"microcephaly_hp:0000252",
"ptosis_hp:0000508",
"ptosis_ictal_sympt",
"ptosis_interictal_sympt",
"dysphagia_sympt",
"tetraparesis_hp:0030182",
"tetraparesis_interictal_sympt",
"areflexia_hp:0001284",
"areflexia_interictal_sympt",
"abnormality_of_skeletal_morphology_hp:0011842",
"osteopenia_hp:0000938",
"short_stature_hp:0004322",
"chorea_hp:0002072",
"intellectual_disability_hp:0001249",
"facial_dysmorphism_hp:0001999",
"mri_brain_abnormality_sympt",
"ophthalmoplegia_hp:0000602",
"ataxia_hp:0002131",
"diplopia_ictal_sympt",
"diplopia_interictal_sympt",
"hyperhidrosis_hp:0000975",
"dysmetric_saccades_hp:0000641",
"ophthalmoparesis_hp:0000597",
"developmental_delay_hp:0001263",
"extensor_plantar_response_hp:0003487",
"motor_developmental_delay_hp:0001270",
"saccadic_smooth_pursuit_hp:0001152",
"slow_saccades_hp:0000514",
"square_wave_jerks_hp:0025402",
"episodic_fever_hp:0001954",
"impaired_vision_hp:0000505",
"decreased_level_of_consciousness_hp:0007185",
"sensory_impairment_hp:0003474",
"coma_hp:0001259",
"sensitivity_to_alcohol_sympt",
"apraxia_hp:0002186",
"emotional_stress_trigger_sympt",
"physical_stress_trigger_sympt",
"heat_trigger_sympt",
"acute_illness_trigger_sympt",
"fatigue_trigger_sympt",
"pregnancy_or_hormonal_change_trigger_sympt",
"sudden_movement_trigger_sympt",
"caffeine_trigger_sympt",
"alcohol_trigger_sympt",
"motor_sympt",
"parkinsonism_sympt",
"nms_park_sympt",
"olfaction_sympt",
"bradykinesia_sympt",
"tremor_rest_sympt",
"tremor_action_sympt",
"tremor_postural_sympt",
"tremor_dystonic_sympt",
"rigidity_sympt",
"postural_instability_sympt",
"dyskinesia_sympt",
"dystonia_sympt",
"hyperreflexia_sympt",
"diurnal_fluctuations_sympt",
"sleep_benefit_sympt",
"motor_fluctuations_sympt",
"depression_sympt",
"anxiety_sympt",
"psychotic_sympt",
"sleep_disorder_sympt",
"cognitive_decline_sympt",
"autonomic_sympt",
"atypical_park_sympt",
"gd_hepatosplenomegaly_sympt",
"gd_blood_abnorm_sympt",
"gd_bone_abnorm_sympt",
"development_delay_sympt",
"tremor_other_sympt",
"gait_difficulties_falls_sympt",
"spasticity_pyramidal_signs_sympt",
"primitive_reflexes_sympt",
"seizures_sympt",
"myoclonus_sympt",
"gaze_palsy_sympt",
"saccadic_abnormalities_sympt",
"ataxia_dysdiadochokinesia_sympt",
"hypomimia_sympt",
"dysarthria_anarthria_sympt",
"rbd_sympt",
"impulsive_control_disorder_sympt",
"hallucinations_sympt",
"intellectual_disability_sympt",
"tremor_unspecified_sympt",
"levodopa_induced_dyskinesia_sympt",
"levodopa_induced_dystonia_sympt"]


strings_to_int_dict = {#genes (classes)
            "CACNA1A" : 1,
            "LRRK2" : 2,
            "KCNA1" : 3,
            "PDHA1" : 4,
            "SLC1A3" : 5,
            "GBA1" : 6,
            #unknown value
            "-99" : 0,
            #ethnicity
            "African ancestry" : 1,
            "Arab" : 2,
            "Asian" : 3,
            "Brazilian" : 4,
            "Caucasian" : 5,
            "Hispanic" : 6,
            "Indian ancestry" : 7,
            "Jewish (Ashkenazi)" : 8,
            "Jewish (non-Ashkenazi/undefined)" : 9,
            "kurdish" : 10,
            "other" : 0,
            #sex
            "male" : 1,
            "female" : 2,
            #signs/symptoms
            "yes" : 1,
            "no" : 2,
            "not treated" : 3,
            #countries
            "ARG" : 1,
            "AUS" : 3,
            "AUT" : 5,
            "BEL" : 6,
            "BOL" : 7,
            "BRA" : 8,
            "CAN" : 9,
            "CHE" : 10,
            "CHL" : 11,
            "CHN" : 12,
            "COL" : 13,
            "CUB" : 14,
            "CZE" : 15,
            "DEU" : 16,
            "DNK" : 17,
            "DZA" : 18,
            "EGY" : 19,
            "ESP" : 20,
            "FIN" : 21,
            "FRA" : 22,
            "FSM" : 24,
            "GBR" : 25,
            "GER" : 26,
            "GRC" : 27,
            "IND" : 28,
            "IRL" : 29,
            "IRN" : 30,
            "IRQ" : 31,
            "ISR" : 32,
            "ITA" : 33,
            "JAP" : 34,
            "JOR" : 35,
            "JPN" : 36,
            "KOR" : 37,
            "LKA" : 38,
            "LTU" : 39,
            "MAR" : 40,
            "MEX" : 41,
            "Mixed/other" : 2,
            "NLD" : 43,
            "NOR" : 44,
            "PAK" : 45,
            "PER" : 46,
            "PHL" : 47,
            "PHP" : 48,
            "POL" : 49,
            "PRI" : 50,
            "PRT" : 51,
            "QAT" : 52,
            "RUS" : 53,
            "SAU" : 54,
            "SDN" : 55,
            "SGP" : 56,
            "SPA" : 57,
            "SRB" : 58,
            "SVK" : 59,
            "SWE" : 60,
            "TUN" : 61,
            "TUR" : 62,
            "TWN" : 63,
            "UKR/POL" : 64,
            "USA" : 23,
            "ZAF" : 42,
            "ZMB" : 65}


strings_to_int_dict = {#genes (classes)
            "CACNA1A" : 1,
            "LRRK2" : 2,
            "KCNA1" : 3,
            "PDHA1" : 4,
            "SLC1A3" : 5,
            "GBA1" : 6,
            #unknown value
            "-99" : 0,
            #ethnicity
            "African ancestry" : 1,
            "Arab" : 2,
            "Asian" : 3,
            "Brazilian" : 4,
            "Caucasian" : 5,
            "Hispanic" : 6,
            "Indian ancestry" : 7,
            "Jewish (Ashkenazi)" : 8,
            "Jewish (non-Ashkenazi/undefined)" : 9,
            "kurdish" : 10,
            "other" : 0,
            #sex
            "male" : 1,
            "female" : 2,
            #signs/symptoms
            "yes" : 1,
            "no" : 2,
            "not treated" : 3,
            #countries
            "ARG" : 1,
            "AUS" : 3,
            "AUT" : 5,
            "BEL" : 6,
            "BOL" : 7,
            "BRA" : 8,
            "CAN" : 9,
            "CHE" : 10,
            "CHL" : 11,
            "CHN" : 12,
            "COL" : 13,
            "CUB" : 14,
            "CZE" : 15,
            "DEU" : 16,
            "DNK" : 17,
            "DZA" : 18,
            "EGY" : 19,
            "ESP" : 20,
            "FIN" : 21,
            "FRA" : 22,
            "FSM" : 24,
            "GBR" : 25,
            "GER" : 26,
            "GRC" : 27,
            "IND" : 28,
            "IRL" : 29,
            "IRN" : 30,
            "IRQ" : 31,
            "ISR" : 32,
            "ITA" : 33,
            "JAP" : 34,
            "JOR" : 35,
            "JPN" : 36,
            "KOR" : 37,
            "LKA" : 38,
            "LTU" : 39,
            "MAR" : 40,
            "MEX" : 41,
            "Mixed/other" : 2,
            "NLD" : 43,
            "NOR" : 44,
            "PAK" : 45,
            "PER" : 46,
            "PHL" : 47,
            "PHP" : 48,
            "POL" : 49,
            "PRI" : 50,
            "PRT" : 51,
            "QAT" : 52,
            "RUS" : 53,
            "SAU" : 54,
            "SDN" : 55,
            "SGP" : 56,
            "SPA" : 57,
            "SRB" : 58,
            "SVK" : 59,
            "SWE" : 60,
            "TUN" : 61,
            "TUR" : 62,
            "TWN" : 63,
            "UKR/POL" : 64,
            "USA" : 23,
            "ZAF" : 42,
            "ZMB" : 65}
