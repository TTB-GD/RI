# Experimental Standard Player — Bundle + Risk

## FACT

- P0 reste la baseline de production inchangée.
- Les politiques standard évaluent des bundles complets; EV énumère exactement les issues de premier bust, MOD filtre les risques individuels à 15/25/40 %.
- Recherche: largeur de beam déterministe 1024 lorsque la borne combinatoire dépasse 50000.

## OBSERVATION

- P0_CURRENT: énergie effective 81.531 %, CTL final 235.24, qualité 23.65, risques 0, busts 0, fatigue finale -8.00, OT 0.0 %.
- P_STD_EV: énergie effective 97.993 %, CTL final 304.16, qualité 43.99, risques 2, busts 0, fatigue finale -6.83, OT 0.0 %.
- P_STD_MOD15: énergie effective 98.018 %, CTL final 304.07, qualité 43.97, risques 0, busts 0, fatigue finale -6.83, OT 0.0 %.
- P_STD_MOD25: énergie effective 97.993 %, CTL final 304.18, qualité 43.99, risques 5, busts 0, fatigue finale -6.82, OT 0.0 %.
- P_STD_MOD40: énergie effective 97.993 %, CTL final 304.18, qualité 43.99, risques 5, busts 0, fatigue finale -6.82, OT 0.0 %.

## INTERPRETATION

- Le raisonnement bundle augmente l'utilisation de capacité et la qualité sans produire Q ni overtraining dans cette campagne.
- L'ouverture RPE reste marginalement sélectionnée; les seuils 25 % et 40 % coïncident dans les états rencontrés.

## LIMITS

- Instrument comportemental, pas modèle validé de joueur humain; pas de course finale; fonction de valeur et seuils non calibrés.

## DESIGN QUESTIONS

- Faut-il représenter le risque par valeur espérée, seuil simple, ou un autre comportement?
- La valeur des SL doit-elle être portée par un objectif distinct?
