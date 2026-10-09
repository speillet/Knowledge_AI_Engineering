#!/usr/bin/env python3
"""Atelier local : python3 examples/data-engineering/atelier_sql.py.

SQLite en mémoire, bibliothèque standard seulement, données synthétiques.
Lire chaque hypothèse puis prédire les résultats avant de lancer l'atelier.
Les assertions vérifient les résultats métier, pas les performances d'un moteur.
"""

import sqlite3


def verifier(db, titre, requete, attendu):
    obtenu = db.execute(requete).fetchall()
    if obtenu != attendu:
        raise AssertionError(f"{titre}\nattendu : {attendu}\nobtenu : {obtenu}")
    print(f"OK — {titre} : {obtenu}")


def main():
    db = sqlite3.connect(":memory:")
    try:
        db.executescript("""
            CREATE TABLE commandes (id INTEGER PRIMARY KEY, montant INTEGER);
            CREATE TABLE lignes (commande_id INTEGER, ligne_id INTEGER);
            CREATE TABLE paiements (commande_id INTEGER, montant INTEGER);
            INSERT INTO commandes VALUES (1, 120);
            INSERT INTO lignes VALUES (1, 1), (1, 2), (1, 3);
            INSERT INTO paiements VALUES (1, 60), (1, 60);

            CREATE TABLE clients (id INTEGER PRIMARY KEY);
            CREATE TABLE tickets (id INTEGER, client_id INTEGER, statut TEXT);
            INSERT INTO clients VALUES (1), (2), (3);
            INSERT INTO tickets VALUES (10, 1, 'ouvert'), (20, 2, 'ferme');

            CREATE TABLE mesures (valeur INTEGER);
            INSERT INTO mesures VALUES (10), (20), (NULL);
            CREATE TABLE source (id INTEGER NOT NULL);
            CREATE TABLE destination (id INTEGER);
            INSERT INTO source VALUES (1), (2);
            INSERT INTO destination VALUES (1), (NULL);

            CREATE TABLE changements (
                id INTEGER, valeur TEXT, version INTEGER NOT NULL,
                event_id INTEGER NOT NULL
            );
            INSERT INTO changements VALUES
                (1, 'ancienne', 1, 1), (1, 'candidate', 2, 2),
                (1, 'retenue', 2, 3), (2, 'unique', 1, 4);

            CREATE TABLE ventes (id INTEGER, jour TEXT, montant INTEGER);
            INSERT INTO ventes VALUES
                (1, '2026-01-01', 10), (2, '2026-01-01', 20),
                (3, '2026-01-02', 5);

            CREATE TABLE decisions (
                decision_id INTEGER PRIMARY KEY, client_id INTEGER,
                decision_at TEXT NOT NULL
            );
            CREATE TABLE features (
                client_id INTEGER, version INTEGER,
                event_at TEXT NOT NULL, available_at TEXT NOT NULL,
                valeur INTEGER
            );
            INSERT INTO decisions VALUES
                (1, 1, '2026-01-01T10:05:00Z'),
                (2, 2, '2026-01-01T10:05:00Z'),
                (3, 1, '2026-01-01T10:12:00Z');
            INSERT INTO features VALUES
                (1, 1, '2026-01-01T09:50:00Z', '2026-01-01T09:51:00Z', 10),
                (1, 2, '2026-01-01T09:58:00Z', '2026-01-01T10:12:00Z', 99);

            CREATE TABLE etat (
                id INTEGER PRIMARY KEY, version INTEGER NOT NULL,
                valeur TEXT, supprime INTEGER NOT NULL
            );
        """)

        # 1. Une jointure multiplicative ne conserve pas le grain commande.
        verifier(db, "Jointure naïve : six lignes et montant multiplié", """
            SELECT COUNT(*), SUM(c.montant)
            FROM commandes c
            JOIN lignes l ON l.commande_id = c.id
            JOIN paiements p ON p.commande_id = c.id
        """, [(6, 720)])
        verifier(db, "Préagrégation au grain commande", """
            WITH l AS (
                SELECT commande_id, COUNT(*) AS nb FROM lignes GROUP BY commande_id
            ), p AS (
                SELECT commande_id, SUM(montant) AS paye
                FROM paiements GROUP BY commande_id
            )
            SELECT c.id, c.montant, l.nb, p.paye
            FROM commandes c JOIN l ON l.commande_id = c.id
            JOIN p ON p.commande_id = c.id
        """, [(1, 120, 3, 120)])

        # 2. Le client sans correspondance doit rester présent si le contrat le veut.
        verifier(db, "Filtre dans ON : clients conservés", """
            SELECT c.id, t.id AS ticket_id
            FROM clients c
            LEFT JOIN tickets t
              ON t.client_id = c.id AND t.statut = 'ouvert'
            ORDER BY c.id
        """, [(1, 10), (2, None), (3, None)])
        verifier(db, "Filtre dans WHERE : clients sans ticket ouvert exclus", """
            SELECT c.id, t.id FROM clients c
            LEFT JOIN tickets t ON t.client_id = c.id
            WHERE t.statut = 'ouvert' ORDER BY c.id
        """, [(1, 10)])

        # 3. NULL change le dénominateur et la logique des comparaisons.
        verifier(db, "Agrégats et moyenne avec/sans imputation", """
            SELECT COUNT(*), COUNT(valeur), SUM(valeur), AVG(valeur),
                   AVG(COALESCE(valeur, 0)) FROM mesures
        """, [(3, 2, 30, 15.0, 10.0)])
        verifier(db, "NOT IN avec NULL : aucun absent remonté", """
            SELECT id FROM source WHERE id NOT IN (SELECT id FROM destination)
        """, [])
        verifier(db, "NOT EXISTS : identifiant absent retrouvé", """
            SELECT s.id FROM source s
            WHERE NOT EXISTS (SELECT 1 FROM destination d WHERE d.id = s.id)
            ORDER BY s.id
        """, [(2,)])

        # 4. event_id fournit ici un départage convenu ; il ne prouve pas la vérité.
        verifier(db, "Une version par clé avec ordre total", """
            WITH ranked AS (
                SELECT id, valeur, ROW_NUMBER() OVER (
                    PARTITION BY id ORDER BY version DESC, event_id DESC
                ) AS rn FROM changements
            )
            SELECT id, valeur FROM ranked WHERE rn = 1 ORDER BY id
        """, [(1, 'retenue'), (2, 'unique')])

        # 5. ROWS suit les positions ; RANGE inclut les pairs de la valeur de tri.
        verifier(db, "Cumuls ROWS et RANGE sur des dates égales", """
            SELECT id,
                SUM(montant) OVER (
                    ORDER BY jour, id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ),
                SUM(montant) OVER (
                    ORDER BY jour RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                )
            FROM ventes ORDER BY id
        """, [(1, 10, 30), (2, 30, 30), (3, 35, 35)])

        # 6. États complets, versions croissantes, sans TTL ; timestamps UTC canoniques.
        # Une disponibilité exactement égale à la décision est admise dans cet exercice.
        verifier(db, "Jointure temporelle : disponibilité réelle respectée", """
            WITH candidats AS (
                SELECT d.decision_id, f.valeur, ROW_NUMBER() OVER (
                    PARTITION BY d.decision_id ORDER BY f.version DESC
                ) AS rn
                FROM decisions d LEFT JOIN features f
                  ON f.client_id = d.client_id
                 AND f.event_at <= d.decision_at
                 AND f.available_at <= d.decision_at
            )
            SELECT decision_id, valeur FROM candidats WHERE rn = 1 ORDER BY decision_id
        """, [(1, 10), (2, None), (3, 99)])
        verifier(db, "Date métier seule : fuite de la valeur arrivée tard", """
            SELECT valeur FROM features
            WHERE client_id = 1 AND event_at <= '2026-01-01T10:05:00Z'
            ORDER BY version DESC LIMIT 1
        """, [(99,)])

        # 7. Protocole pédagogique d'états complets ; ce n'est pas un journal de deltas.
        # Des événements contradictoires à version égale doivent être signalés en amont.
        upsert = """
            INSERT INTO etat(id, version, valeur, supprime) VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                version = excluded.version, valeur = excluded.valeur,
                supprime = excluded.supprime
            WHERE excluded.version > etat.version
        """
        for event in [(1, 2, 'actuel', 0), (1, 2, 'actuel', 0), (1, 1, 'ancien', 0)]:
            db.execute(upsert, event)
        verifier(db, "Rejeu et événement ancien sans écrasement", """
            SELECT id, version, valeur, supprime FROM etat
        """, [(1, 2, 'actuel', 0)])
        db.execute(upsert, (1, 3, None, 1))
        db.execute(upsert, (1, 2, 'actuel', 0))
        verifier(db, "Tombstone versionné : absence de résurrection", """
            SELECT id, version, valeur, supprime FROM etat
        """, [(1, 3, None, 1)])
        verifier(db, "Vue active après suppression", """
            SELECT id FROM etat WHERE supprime = 0
        """, [])

        print("\n7 cas, 14 résultats vérifiés. Aucun service externe ni fichier de données créé.")
        print("Cela valide ces exemples SQL locaux, pas un système distribué ni ses performances.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
