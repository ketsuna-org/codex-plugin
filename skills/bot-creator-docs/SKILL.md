---
name: bot-creator-docs
description: Consulter la documentation officielle Bot Creator pour expliquer les fonctions, guider les utilisateurs et préparer des commandes ou workflows Blocks, BDFD ou JavaScript pour leurs bots Discord. Utiliser pour les demandes concernant Bot Creator.
---

# Documentation Bot Creator

Dans ChatGPT ou Codex, utiliser le serveur MCP documentaire `bot-creator-docs` du plugin. Il consulte les documents publics et valide des structures ; il n'accède à aucun compte ni bot. Répondre dans la langue de l'utilisateur, en conservant les identifiants et la syntaxe des fonctions.

## Lire les références et guides

- Pour une fonction, utiliser `search_docs` avec `query` et, si connu, `api_type` (`blocks`, `bdfd`, `javascript` ou `general`), puis `get_doc` avec le slug retourné. Le résultat compact suffit pour les signatures ; demander `full_markdown=true` pour expliquer le comportement, les exemples ou obtenir le lien source.
- Pour un tutoriel, utiliser `search_posts` ou `list_posts`, puis `get_post` avec le slug trouvé. `list_posts` accepte `locale=fr` ou `en` ; si le filtre ne retourne rien, chercher sans filtre et expliquer le guide dans la langue demandée.
- Citer les URL officielles retournées par les documents ou les métadonnées des guides. Ne pas fabriquer de lien à partir du nom d'une fonction. Lire le document avant de lui attribuer une affirmation.
- Distinguer les modes et les statuts de compatibilité retournés : une fonction documentée pour BDFD n'est pas automatiquement une action Blocks ou une API JavaScript. Ne pas présenter une fonction indiquée indisponible comme utilisable.

## Préparer une commande ou un workflow

Identifier le mode demandé ou déjà établi. S'il manque et change la solution, le demander à l'utilisateur. Appeler `plan_solution` avec l'intention et ce mode (`bdfd`, `blocks` ou `javascript`). Son résultat est une aide à la recherche : vérifier que les fonctions proposées répondent réellement au besoin. Respecter les ambiguïtés signalées et consulter les références nécessaires avant de produire l'exemple.

Lire `get_doc` pour `execution-model` avant un premier exemple de code dans la conversation. Respecter la syntaxe Bot Creator, son modèle de réponse aux interactions et les limites du runtime documentées ; ne pas transposer aveuglément un exemple BDFD externe ou Node.js.

Pour Blocks, utiliser `list_actions` et `get_schema_manifest` pour les actions nécessaires ; utiliser le mode `types` si leurs paramètres référencent des objets imbriqués. Générer les actions avec leurs noms exacts et leurs paramètres sous `payload` ; une clé de résultat `key`, si nécessaire, appartient à l'action. Appeler `validate_actions` sur l'intégralité de la liste produite et corriger les erreurs avant de la livrer. Expliquer les avertissements pertinents. Cette validation vérifie la structure, pas l'exécution sur Discord ni l'importation d'un bot complet.

Pour BDFD et JavaScript, consulter les signatures et exemples du mode concerné. Le service documentaire ne fournit pas de test d'exécution BDFD/JavaScript : ne pas annoncer qu'un script a été compilé ou exécuté.

Présenter le code comme une proposition à utiliser dans Bot Creator, avec les paramètres à adapter et les étapes manuelles documentées. Ne pas annoncer une commande installée, un workflow activé ou un bot créé.

## Indisponibilité et demandes de gestion

Si les outils ne sont pas disponibles ou si le service échoue, indiquer que la documentation n'a pas pu être consultée et proposer le site https://bot-creator.fr. Ne pas inventer de signatures, de résultats ou de validation. Un exemple non validé doit être clairement signalé ; ne pas le présenter comme un exemple Blocks validé.

Pour une demande de création ou modification réelle d'un bot, expliquer que cette V1 fournit la documentation et des propositions. Donner les étapes manuelles après consultation des guides pertinents. Ne pas demander de token Discord, d'identifiants Manager ou de clé fournisseur pour ce parcours.
