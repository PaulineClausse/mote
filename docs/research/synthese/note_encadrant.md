# Note de cadrage : 3DGS temps réel pour la XR

*Point d'étape du 29/09/2026, après la revue de littérature (34 papiers lus et fichés, plus une vérification d'antériorité 2025–2026).*

## 1. Constat : la cible du sujet est déjà atteinte sur PC

- **« ≥ 30 fps en 1080p » est acquis sur GPU desktop** : 134 à 197 fps pour le 3DGS original, jusqu'à 311 à 694 fps pour les rasteriseurs optimisés (Kerbl 2023, FlashGS 2024).
- **La VR sur PC tient 72 à 90 Hz** avec une RTX 4090 (VRSplat, VR-Splatting).
- **L'entraînement n'est plus le verrou** : 7 à 11 min sous budget de Gaussiennes (Taming 3DGS).

La vraie difficulté est de rendre **en stéréo, à la résolution et à la fréquence d'un casque autonome** (Quest 3 : 72 à 90 Hz, ≈ 11 à 14 ms par image), **sur des scènes réelles**.

## 2. Le manque dans la littérature

- **Sur Quest 3 natif, les résultats publiés plafonnent à ≈ 0,2 M Gaussiennes** (Kleinbeck 2024 : 38 à 98 fps en stéréo sur 57k à 196k Gaussiennes). La recommandation officielle de Meta est de rester sous 150k, et les meilleurs chiffres annoncés sont d'environ 400 à 500k à 72 Hz. Or une scène réelle compte **1 à 6 M** de Gaussiennes.
- **Aucun papier ne mesure la latence motion-to-photon** en 3DGS.
- Les leviers qualité/coût existent (LOD, budget, élagage, fovéation, tri partagé entre les yeux), mais **ils sont tous réglés à la main**.

## 3. Proposition de contribution

**P6, banc de mesure sur casque réel.** 3DGS stéréo natif sur Quest 3, sur des **scènes réelles** (Mip-NeRF 360), à budgets contrôlés (150k à 1M Gaussiennes rendues). Mesures :
- temps d'image p50/p95 et images perdues ;
- puissance et régime thermique ;
- qualité (LPIPS, FLIP temporel) ;
- **motion-to-photon**.

**Antériorité directe :** Ghanbari, Amirpour et Timmerer (IEEE VCIP 2026, Quest 3). Ils ne mesurent ni le nombre absolu de splats, ni le motion-to-photon, ni la qualité.

**P3′, contrôleur QoS/QoE côté casque.** Une boucle fermée qui ajuste **conjointement plusieurs leviers** pour tenir une cible de temps d'image, de motion-to-photon ou d'énergie : *render scale*, budget de Gaussiennes, LOD, rayon fovéal, fréquence et partage du tri. Le contrôleur est formalisé comme une instance en ligne de l'**éq. 1 de Kamdjou et al. (2024)**.

**Antériorité à citer :** MoQSplat (MMSP 2026) règle un seul levier, le budget de splats, sur desktop à 24 fps. GaussAnything (Pico 4 Ultra) règle le débit de mises à jour, pas le coût de rendu. **La combinaison « côté casque, stéréo, multi-leviers, cible motion-to-photon ou énergie » reste nouvelle**, mais l'équipe ATHENA/AAU publie activement sur ce créneau : il faut avancer vite.

**Pourquoi l'un amène l'autre :** P6 fournit la cartographie des coûts dont P3′ a besoin. Les premières données publiques (VCIP 2026) montrent déjà qu'aucun levier ne suffit seul : la résolution domine le coût, et la densité de splats n'agit qu'à l'approche du budget.

## 4. Plan à court terme

1. **Semaine 1** : Unity 6 + UnityGaussianSplatting sur le PC de l'école, avec les modèles pré-entraînés de l'INRIA. **Premier test sur le Quest 3 de l'école**, avec un point de contrôle : reproduire les chiffres de Kleinbeck.
2. **Semaines 2 à 3** : instrumentation (Gaussiennes visibles, overdraw, pixels traités) et génération de variantes de scènes à budget exact avec Taming 3DGS sur le GPU du PC (étape 2 du sujet).
3. **Ensuite** : campagne de mesure sur Quest 3 natif et en PC-VR (Link), avec OVR Metrics, Perfetto et un protocole motion-to-photon à définir.

Détail : `synthese/plan_environnement.md`.

## 5. Questions à trancher

1. **Matériel :** je prévois d'emprunter **un Quest 3 et un PC équipé d'un GPU NVIDIA** à l'école. Peut-on avoir un **créneau régulier** plutôt qu'un prêt ponctuel ? Le mode développeur est-il activable sur le casque ?
2. **Cible :** casque autonome (ma proposition) ou PC-VR ? 1080p **par œil** ou total ? 30 fps est-il un minimum, sachant que le casque impose 72 Hz ?
3. **Périmètre :** P6 + P3′ comme cœur, ou P6 seul ? Scènes statiques uniquement ? Je prévois les **scènes de référence INRIA** (Mip-NeRF 360, T&T, Deep Blending). Faut-il aussi une **scène « maison »** proche du contexte industriel de LINEACT (atelier, machine), par exemple pour un démonstrateur ?
4. **Mesure motion-to-photon :** le labo a-t-il du matériel (photodiode, caméra rapide) ou un protocole existant ?
5. **Valorisation :** vise-t-on une publication ? Vu la concurrence d'ATHENA/AAU en 2026, le calendrier compte.
