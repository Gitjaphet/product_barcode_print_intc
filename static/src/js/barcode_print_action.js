import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

const TOKEN_KEY = "intc_bridge_token";

async function send(url, bytes, token) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/octet-stream",
            "X-Bridge-Token": token || "",
        },
        body: bytes,
    });
    let result = {};
    try {
        result = await response.json();
    } catch {
        // réponse sans JSON : on garde le statut HTTP
    }
    return { response, result };
}

/**
 * Action client : envoie les octets ESC/POS (reçus en base64) au pont d'impression local.
 * Le jeton du pont est mémorisé par poste (navigateur), demandé à la première impression.
 */
async function printBarcodes(env, action) {
    const { url, data } = action.params;
    const bytes = Uint8Array.from(atob(data), (c) => c.charCodeAt(0));
    try {
        let token = localStorage.getItem(TOKEN_KEY) || "";
        let { response, result } = await send(url, bytes, token);
        if (response.status === 401) {
            token = (window.prompt(
                _t("Première impression sur ce poste : collez le jeton affiché dans INTC Print Bridge (bouton « Copier »).")
            ) || "").trim();
            if (!token) {
                throw new Error(_t("jeton non fourni"));
            }
            ({ response, result } = await send(url, bytes, token));
            if (response.ok) {
                localStorage.setItem(TOKEN_KEY, token);
            }
        }
        if (!response.ok || result.status !== "ok") {
            throw new Error(result.message || response.statusText);
        }
        env.services.notification.add(_t("Étiquettes envoyées à l'imprimante."), {
            type: "success",
        });
    } catch (error) {
        const message = error instanceof TypeError
            ? _t("pont injoignable. Vérifiez qu'INTC Print Bridge est installé et « En marche » sur ce poste.")
            : error.message;
        env.services.notification.add(
            `${_t("Impossible d'imprimer via le pont")} (${url}) : ${message}`,
            { type: "danger", sticky: true }
        );
    }
    return { type: "ir.actions.act_window_close" };
}

registry.category("actions").add("product_barcode_print_intc.print", printBarcodes);
