


const formulaire = document.getElementById("formCredit");
const zoneResultat = document.getElementById("resultat");

function afficherApercu(idChamp, idApercu) {
    const champ = document.getElementById(idChamp);
    const apercu = document.getElementById(idApercu);
    champ.addEventListener("input", function () {
        apercu.textContent = champ.value ? Number(champ.value).toLocaleString("fr-FR") : "";
    });
}
afficherApercu("revenu_demandeur", "apercu_revenu_demandeur");
afficherApercu("revenu_codemmandeur", "apercu_revenu_codemmandeur");
afficherApercu("montant_pret", "apercu_montant_pret");

function ligneVerification(libelle, valide) {
    const icone = valide ? "" : "";
    const couleur = valide ? "text-emerald-400" : "text-red-400";
    return "<p class='" + couleur + "'>" + icone + " " + libelle + "</p>";
}

formulaire.addEventListener("submit", async function (event) {
    event.preventDefault();

    const donnees = new FormData(formulaire);

    const payload = {
        genre: donnees.get("genre"),
        marrie: donnees.get("marrie"),
        travailleur_indep: donnees.get("travailleur_indep"),
        revenu_demandeur: parseFloat(donnees.get("revenu_demandeur")),
        revenu_codemmandeur: parseFloat(donnees.get("revenu_codemmandeur")),
        montant_pret: parseFloat(donnees.get("montant_pret")),
        pers_en_charge: parseInt(donnees.get("pers_en_charge")),
        credit_historique: donnees.get("credit_historique"),
        zone_residence: donnees.get("zone_residence"),
        duree_pret: parseFloat(donnees.get("duree_pret")),
        Education: donnees.get("Education")
    };

    const champsNumeriques = ["revenu_demandeur", "revenu_codemmandeur", "montant_pret", "pers_en_charge", "duree_pret"];
    for (const champ of champsNumeriques) {
        if (Number.isNaN(payload[champ])) {
            alert("Le champ '" + champ + "' doit contenir un nombre valide.");
            return;
        }
        if (payload[champ] < 0){
            alert("le champ '"+champ+ "'doit contenir un nombre valide.");
        }
    }

    try {
        const reponse = await fetch("/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const resultat = await reponse.json();

        if (!reponse.ok) {
            throw new Error(resultat.detail ? JSON.stringify(resultat.detail) : "Erreur inconnue");
        }

        const accorde = resultat.decision === "Accordé";

        zoneResultat.className = accorde
            ? "bg-emerald-950 border border-emerald-800 rounded-2xl p-6 shadow-xl"
            : "bg-red-950 border border-red-800 rounded-2xl p-6 shadow-xl";

        zoneResultat.innerHTML =
            "<div class='text-center mb-4'>" +
                "<p class='text-sm text-slate-400 uppercase tracking-wide'>Décision</p>" +
                "<p class='text-3xl font-bold " + (accorde ? "text-emerald-400" : "text-red-400") + "'>" + resultat.decision + "</p>" +
            "</div>" +
            "<div class='text-center mb-4'>" +
                "<p class='text-sm text-slate-400'>Probabilité de risque</p>" +
                "<p class='text-xl font-semibold'>" + (resultat.probabilite * 100).toFixed(2) + " %</p>" +
            "</div>" +
            "<div class='space-y-1 mb-4'>" +
                ligneVerification("Modèle ML : " + resultat.decision_modele, resultat.decision_modele === "Accordé") +
                ligneVerification("Politique métier : " + resultat.decision_metier, resultat.decision_metier === "Accordé") +
            "</div>" +
            "<div class='border-t border-slate-700 pt-3 space-y-1 text-sm text-slate-300'>" +
                "<p>Ratio d'endettement : " + resultat.ratio_endettement + "</p>" +
                "<p>Ratio d'endettement (ménage) : " + resultat.ratio_endettement_menage + "</p>" +
                "<p class='text-slate-400 mt-2'>" + resultat.motif + "</p>" +
            "</div>";

    } catch (erreur) {
        zoneResultat.className = "bg-red-950 border border-red-800 rounded-2xl p-6 shadow-xl";
        zoneResultat.innerHTML = "<p class='text-red-400 text-center'>Une erreur est survenue : " + erreur.message + "</p>";
    }
});