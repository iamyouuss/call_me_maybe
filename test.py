#!/usr/bin/env python3
""" def name_filter(tokens: list[str], logits: list[float]) -> list[float]:
    logits_to_mod = logits.copy()
    
    for i in range(len(logits_to_mod)):
        if not tokens[i].startswith("fn_"):
            logits_to_mod[i] = -float('inf')
    return logits_to_mod

if __name__ == "__main__":
    tokens = ["fn_greet", "Bonjour", "fn_add_numbers", "42"]
    scores = [2.5, 8.0, 1.2, 5.0]

    nouveaux_scores = name_filter(tokens, scores)

    print("Anciens scores :", scores)
    print("Nouveaux scores :", nouveaux_scores)  """

def determiner_tokens_autorises(texte_genere: str, noms_fonctions: list[str]) -> list[str]:
    """
    Analyse le texte déjà généré pour déduire l'étape actuelle
    et renvoyer uniquement les tokens autorisés.
    """
    # État 0 : Le texte est vide, on doit commencer l'objet JSON
    if texte_genere == "":
        return ["{"]
        
    # État 1 : Le JSON est ouvert, on force la première clé à être "name"
    elif texte_genere == "{":
        return ['"name"']
        
    # État 2 : La clé est écrite, on attend le séparateur JSON ":"
    elif texte_genere == '{"name"':
        return [":"]
        
    # État 3 : Le séparateur est là, on attend la valeur (le nom de la fonction)
    elif texte_genere == '{"name":':
        # On autorise uniquement les noms de fonctions définis dans notre schéma,
        # formatés avec des guillemets car c'est une valeur JSON (ex: '"fn_greet"')
        return [f'"{nom}"' for nom in noms_fonctions]
        
    # État de sécurité (si on a dépassé ce qu'on sait gérer dans ce mini-exemple)
    else:
        return []

# --- TESTS POUR VOIR COMMENT ÇA RÉAGIT ---
fonctions_disponibles = ["fn_greet", "fn_add_numbers"]

print("Au tout début :", determiner_tokens_autorises("", fonctions_disponibles))
# Résultat : ['{']

print("Après avoir ouvert :", determiner_tokens_autorises("{", fonctions_disponibles))
# Résultat : ['"name"']

print("Avant de choisir la fonction :", determiner_tokens_autorises('{"name":', fonctions_disponibles))
# Résultat : ['"fn_greet"', '"fn_add_numbers"']