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