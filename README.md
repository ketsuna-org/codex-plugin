# Bot Creator — plugin Codex

Version **0.1.0**, identifiant technique `codex-plugin`.

Ce plugin aide les utilisateurs de [Bot Creator](https://bot-creator.fr) à consulter les guides et références officiels et à préparer des exemples de commandes ou workflows **Blocks, BDFD et JavaScript**. Il répond dans la langue demandée et cite les documents consultés.

Il réutilise le [service MCP documentaire public](https://bot-creator.fr/api/mcp) en HTTP Streamable, sans authentification. Aucun nouveau serveur ni compte Bot Creator n'est nécessaire. Les documents restent sur le service public pour suivre ses mises à jour.

## Capacités et limites

- Rechercher les fonctions et guides, lire leurs signatures, exemples et statuts de compatibilité.
- Préparer une solution avec `plan_solution` et consulter les références appropriées au mode choisi.
- Valider la structure des actions Blocks avec `validate_actions` avant de proposer le JSON.
- Expliquer les étapes manuelles à effectuer dans Bot Creator.

Cette V1 ne crée ni ne modifie de bots, commandes ou workflows. Elle n'accède pas à l'API Manager, aux comptes ou aux secrets. Une validation Blocks ne prouve pas l'exécution sur Discord ; les exemples BDFD et JavaScript ne sont pas exécutés par ce service. Le plugin ne demande aucun token Discord.

En cas d'indisponibilité du service, le skill indique que la documentation n'a pas pu être consultée et propose le site officiel. Il ne prétend pas avoir validé un exemple ou effectué une modification. Certains guides sont uniquement en anglais : ils peuvent être expliqués en français.

## Installation pour le développement

Le catalogue `.agents/plugins/marketplace.json` est une source locale de test, nommée `bot-creator-local`. Son chemin `./` désigne la racine de ce dépôt, où se trouve le plugin ; il n'est pas relatif au dossier `.agents/plugins`.

Cloner le dépôt, puis enregistrer explicitement cette source et installer le plugin :

```bash
git clone git@github.com:ketsuna-org/codex-plugin.git
cd codex-plugin
codex plugin marketplace add "$PWD"
codex plugin list --marketplace bot-creator-local --available
codex plugin add codex-plugin@bot-creator-local
```

Redémarrer Codex desktop, puis ouvrir une **nouvelle conversation**. Vérifier que le plugin « Bot Creator » et son serveur `bot-creator-docs` sont disponibles. Dans les versions qui proposent les sources locales dans le répertoire des plugins, sélectionner la source « Bot Creator — développement » pour consulter le plugin.

Le skill `bot-creator-docs` peut être choisi automatiquement pour une demande concernant Bot Creator. Pour un test explicite, sélectionner ce skill dans le sélecteur de compétences de Codex.

Après une modification, actualiser la source et le plugin avec les commandes de marketplace proposées par la version installée de Codex, puis redémarrer l'application et recommencer dans une nouvelle conversation.

La création de ce dépôt n'installe pas le plugin dans votre configuration personnelle. Le catalogue sert au développement et à la distribution privée ; ce dépôt n'est pas une publication dans le répertoire public OpenAI.

## Vérifications reproductibles

Python 3.9+ suffit pour les vérifications locales. Les vérifications réseau nécessitent aussi `curl` et une connexion au service public :

```bash
python3 scripts/check_plugin.py
python3 scripts/check_plugin.py --live
```

Le script vérifie les manifestes, chemins, découverte du skill et catalogue. Avec `--live`, il vérifie l'initialisation MCP, les outils disponibles, une recherche et une référence avec sa source, le modèle d'exécution, un guide, la planification en français pour BDFD et Blocks, ainsi que la validation d'un exemple Blocks et le rejet d'une action inconnue. Il ne modifie aucun bot et échoue explicitement si le service est indisponible.

Ces contrôles testent le paquet et le service, pas les réponses d'un modèle. Après installation, vérifier dans une nouvelle conversation :

| Demande | Résultat attendu |
| --- | --- |
| « Explique en français comment répondre à une commande slash dans Bot Creator. » | Références consultées, explication en français et liens officiels. |
| « Propose une commande BDFD qui répond Bonjour. » | Appel à `plan_solution`, lecture du modèle d'exécution et des références nécessaires ; proposition sans prétendre à une exécution. |
| « Propose les actions Blocks pour répondre Bonjour en privé. » | Schéma consulté, liste complète passée à `validate_actions`, aucune erreur avant livraison ; validation structurelle clairement distinguée d'un test Discord. |
| Serveur documentaire désactivé pour la conversation, puis même question | Indisponibilité annoncée, lien vers le site, aucune signature ou validation inventée. |
| « Crée ce bot sur mon compte Bot Creator. » | Limite de la V1 expliquée et étapes manuelles documentées, sans demande de secret ni annonce de création. |

Le test dans une conversation après installation reste nécessaire pour vérifier la découverte et le comportement du modèle dans la version de Codex utilisée.

## Structure

- `.codex-plugin/plugin.json` : manifeste Codex compatible, version et interface du plugin.
- `.mcp.json` : connexion publique au service documentaire.
- `skills/bot-creator-docs/SKILL.md` : recherche, citations, modes et limites.
- `.agents/plugins/marketplace.json` : catalogue local, sans activation automatique.
- `scripts/check_plugin.py` : contrôles du paquet et du service.

Le format suit la [documentation officielle OpenAI sur les plugins](https://developers.openai.com/plugins/build/plugins).
