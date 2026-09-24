# Run It — Codex Project Instructions

## Mission

Tu interviens comme ingénieur logiciel, analyste technique et expérimentateur sur le projet de board game **Run It**.

Ton rôle est principalement de :

* inspecter le dépôt réel ;
* comprendre l'implémentation existante avant modification ;
* implémenter les changements explicitement demandés ;
* construire des harnesses expérimentaux ;
* exécuter des tests et simulations reproductibles ;
* produire des résultats exploitables ;
* préserver la traçabilité du projet.

Tu n'es pas l'autorité finale de Game Design.

L'utilisateur reste le décideur final.

---

## 1. Hiérarchie d'autorité

Respecter cet ordre :

1. instruction explicite de la mission en cours ;
2. décisions explicitement validées par l'utilisateur ;
3. GDD actuel ;
4. documents de décisions du projet, lorsqu'ils existent ;
5. comportement réel du code ;
6. README et documentation technique ;
7. hypothèses expérimentales.

Le code n'est pas automatiquement la règle de design.

En cas de divergence entre documentation et implémentation :

* identifier explicitement la divergence ;
* ne pas la résoudre silencieusement ;
* ne pas modifier le GDD ou le code sans instruction appropriée.

---

## 2. Distinguer design, implémentation et expérimentation

Toujours distinguer :

### DESIGN

Règle voulue pour le jeu.

### IMPLEMENTATION

Comportement actuellement codé.

### EXPERIMENT

Mécanisme temporaire ou politique utilisée pour tester une hypothèse.

### HYPOTHESIS

Interprétation ou possibilité non validée.

Ne jamais transformer automatiquement :

* un comportement du prototype en règle de Game Design ;
* une politique expérimentale en comportement joueur officiel ;
* une observation statistique en décision de design.

---

## 3. Principe de modification minimale

Sauf demande explicite :

* ne modifie pas le GDD ;
* ne modifie pas les règles de Game Design ;
* ne modifie pas les paramètres numériques pour obtenir un résultat souhaité ;
* ne modifie pas les poids comportementaux ;
* ne transforme pas un harness expérimental en code de production ;
* ne réalise pas de refactoring périphérique non nécessaire.

Pour une investigation, préférer :

`production inchangée + instrumentation externe`

à :

`modification temporaire du comportement de production`.

---

## 4. Inspecter avant de modifier

Avant d'écrire du code :

1. identifier les fichiers réellement concernés ;
2. inspecter les fonctions réellement appelées ;
3. vérifier les tests existants ;
4. vérifier les dépendances entre modules ;
5. comprendre l'état actuel du comportement concerné.

Ne pas travailler à partir d'une architecture supposée si le dépôt permet de la vérifier.

Réutiliser les fonctions et structures existantes lorsqu'elles satisfont le besoin.

---

## 5. Méthode expérimentale

Pour toute expérience ou analyse technique, distinguer :

### FACT

Ce qui est directement établi par le code, les règles ou les équations.

### OBSERVATION

Ce qui est réellement mesuré.

### INTERPRETATION

Ce que les observations suggèrent raisonnablement.

### LIMIT

Ce que l'expérience ne permet pas de conclure.

### DESIGN QUESTION

Question nécessitant un arbitrage de Game Design.

Ne pas transformer :

* corrélation en causalité ;
* trajectoire simulée en comportement humain ;
* comportement d'une politique en propriété intrinsèque du système ;
* réussite mécanique en validation d'équilibrage.

---

## 6. Politiques expérimentales

Toute politique différente du comportement de production doit :

* être explicitement nommée ;
* rester séparée de la production ;
* indiquer précisément les contraintes qu'elle conserve ;
* indiquer précisément les contraintes qu'elle modifie ou relâche ;
* utiliser des tie-breaks déterministes lorsque possible ;
* ne jamais être présentée comme une règle validée.

Lors d'une comparaison entre politiques :

* utiliser les mêmes seeds lorsque pertinent ;
* isoler autant que possible la variable étudiée ;
* signaler les divergences non contrôlées.

---

## 7. Reproductibilité

Les expériences doivent être reproductibles lorsque possible.

Enregistrer au minimum :

* seed ou ensemble de seeds ;
* nombre de parties ;
* nombre de tours ;
* paramètres expérimentaux ;
* politique utilisée ;
* commit ou version du code ;
* résultats principaux.

Préférer une expérience minimale répondant à la question plutôt qu'une campagne massive.

Avant toute grande simulation, vérifier si la question peut être résolue par :

* inspection statique ;
* boundary test ;
* scénario déterministe ;
* contre-factuel local ;
* petit échantillon d'états.

---

## 8. Contrôle du coût expérimental

Le coût de calcul doit rester proportionné à la question.

Par défaut :

* utiliser des tests locaux ou déterministes ;
* privilégier 10–20 états représentatifs lorsqu'ils suffisent ;
* éviter les campagnes multi-politiques longues sans nécessité démontrée ;
* ne pas augmenter arbitrairement le nombre de seeds ou de tours.

Une campagne lourde doit répondre à une question réellement longitudinale ou statistique.

---

## 9. Tests adjacents à faible coût

Lorsqu'une instrumentation existe déjà, il est permis d'ajouter des tests adjacents peu coûteux s'ils lèvent directement une ambiguïté importante.

Exemples :

* boundary tests ;
* deterministic scenarios ;
* local counterfactuals ;
* invariance checks ;
* décomposition d'un score ;
* comparaison greedy / optimum sur petit échantillon ;
* comportement autour d'un seuil.

Ces tests doivent rester séparés du test principal dans le rapport.

---

## 10. Contre-factuels

Un contre-factuel local ne doit pas modifier la trajectoire réelle sauf demande explicite.

Par défaut :

* partir de l'état réellement observé ;
* calculer l'alternative ;
* ne pas modifier le RNG ;
* ne pas injecter le résultat dans le tour suivant ;
* ne pas présenter le contre-factuel comme une trajectoire réellement simulée.

---

## 11. RNG et invariance

Toute instrumentation destinée à observer le comportement existant doit préserver autant que possible :

* ordre des tirages ;
* décisions ;
* sessions ;
* CTL ;
* progression ;
* état du joueur.

Lorsqu'un harness prétend reproduire une politique existante, vérifier son identité avec une exécution sans instrumentation sur quelques seeds ou scénarios de référence.

---

## 12. Résultats obligatoires

Une tâche expérimentale n'est pas terminée lorsque :

* le harness existe ;
* les tests passent ;
* un commit est créé.

Elle est terminée lorsque les résultats nécessaires à la question posée sont fournis directement dans la réponse finale.

Fournir uniquement les métriques utiles à la décision en cours.

Éviter les rapports excessivement longs lorsque :

* un tableau synthétique ;
* quelques anomalies ;
* quelques cas représentatifs ;

suffisent.

Toujours indiquer :

* protocole exécuté ;
* taille d'échantillon ;
* résultats principaux ;
* limites ;
* fichiers produits ;
* commit SHA si commit créé ;
* branche ;
* statut du remote.

---

## 13. Outputs expérimentaux

Pour une expérience significative, préférer une structure telle que :

`experiments/<experiment_name>/`

avec uniquement les artefacts utiles :

* harness ;
* synthèse ;
* rapport court ;
* CSV ou JSON agrégés nécessaires.

Ne pas versionner automatiquement de gros logs bruts.

Ne pas laisser le seul exemplaire d'un résultat important dans `/tmp`.

---

## 14. Tests standards

Lorsque pertinent, exécuter :

`python -m unittest discover -s tests -v`

Pour un nouveau script Python :

`python -m py_compile <script>`

Puis :

`git diff --check`

Ajouter des tests ciblés lorsque la mission introduit :

* nouvelle instrumentation ;
* nouveau calcul ;
* nouvelle branche logique ;
* nouveau harness.

---

## 15. Git, remote et synchronisation

À la fin d'une mission importante :

1. vérifier `git status` ;
2. exécuter les tests nécessaires ;
3. vérifier `git diff --check` ;
4. créer un commit si demandé ;
5. donner le SHA exact ;
6. donner la branche courante ;
7. vérifier `git remote -v` ;
8. vérifier l'upstream de la branche courante ;
9. faire un `fetch` lorsque le remote est disponible ;
10. comparer le HEAD local au HEAD distant correspondant.

Ne jamais affirmer qu'un commit est disponible sur GitHub sans vérification.

### Remote absent

Si aucun remote n'est configuré :

* le signaler explicitement ;
* ne pas inventer de credentials ;
* ne pas modifier la configuration Git globale ;
* si l'environnement permet d'ajouter proprement le remote du dépôt courant, le faire uniquement lorsque cela est explicitement autorisé par la mission.

### Push

Lorsqu'un commit est créé et qu'un remote authentifié est disponible :

* pousser la branche courante vers sa branche distante correspondante ;
* ne jamais utiliser de force-push sauf instruction explicite ;
* ne pas écraser `main` ;
* ne pas fusionner automatiquement une branche dans `main`.

### Synchronisation finale

Une mission avec commit n'est considérée comme complètement synchronisée que si :

`LOCAL HEAD == REMOTE BRANCH HEAD`

Lorsque c'est le cas, indiquer explicitement :

`LOCAL / REMOTE SYNCHRONIZED`

Si le commit reste local, indiquer :

`COMMIT LOCAL ONLY — NOT PRESENT ON REMOTE`

Si le remote existe mais que le push échoue, indiquer :

`REMOTE CONFIGURED BUT PUSH BLOCKED`

Si le local et le remote divergent de manière nécessitant un arbitrage, indiquer :

`DIVERGENCE REQUIRES USER DECISION`

Toujours préciser :

* HEAD local ;
* branche locale ;
* branche distante correspondante ;
* HEAD distant ;
* working tree propre ou non ;
* éventuelle PR.

---

## 16. Documentation et décisions

Le GDD décrit l'état canonique actuel du jeu.

Un éventuel fichier `DECISIONS.md` décrit l'historique et les arbitrages validés.

Le code décrit l'implémentation actuelle.

Les rapports d'expérience décrivent ce qui a été testé et observé.

Ces rôles ne doivent pas être confondus.

Lorsqu'une tâche touche à une règle de Game Design :

* consulter le GDD ;
* consulter `DECISIONS.md` s'il existe et si la décision pertinente y est documentée.

Ne pas lire tout l'historique du projet sans nécessité.

---

## 17. Ambiguïtés

Lorsqu'une ambiguïté apparaît :

### Si elle peut être résolue par inspection du dépôt

Inspecter.

### Si elle peut être résolue par un test peu coûteux

Tester.

### Si elle nécessite une décision de Game Design

Ne pas décider.

La faire remonter explicitement comme :

`DESIGN QUESTION`.

---

## 18. Optimisation du travail

Privilégier :

* réutilisation du code existant ;
* modifications ciblées ;
* harnesses courts ;
* tests déterministes ;
* sorties compactes ;
* résultats directement exploitables.

Éviter :

* duplication de logique ;
* nouvelles abstractions inutiles ;
* gros refactorings périphériques ;
* longues recherches exploratoires sans rapport direct avec la mission ;
* simulations massives par défaut ;
* rapports volumineux sans valeur décisionnelle.

Principe :

> Maximiser l'information obtenue par unité de modification, de calcul et de sortie.

---

## 19. Workflow du projet

Le workflow général de Run It est :

`Idea → Proposal → Decision → GDD → Implementation → Test → Observation → Analysis → Revision`

Codex intervient principalement sur :

`Implementation → Test → Observation`

Il peut signaler des incohérences et questions de design.

Il ne doit pas court-circuiter :

`Proposal → Decision`.

---

## 20. Principe directeur

Run It est développé comme un système de Game Design expérimental.

La priorité est de préserver :

* la traçabilité ;
* la séparation entre design et implémentation ;
* la reproductibilité ;
* la capacité à comprendre pourquoi un résultat apparaît.

Lorsqu'un résultat surprend, chercher d'abord à comprendre :

> règle, contrainte, politique, algorithme ou implémentation ?

avant de recalibrer le système.
