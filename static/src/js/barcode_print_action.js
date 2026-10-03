import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

/**
 * Action client : envoie les octets ESC/POS (reçus en base64) au pont d'impression local.
 */
async function printBarcodes(env, action) {
    const { url, data } = action.params;
    const bytes = Uint8Array.from(atob(data), (c) => c.charCodeAt(0));
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/octet-stream" },
            body: bytes,
        });
        const result = await response.json();
        if (!response.ok || result.status !== "ok") {
            throw new Error(result.message || response.statusText);
        }
        env.services.notification.add(_t("Étiquettes envoyées à l'imprimante."), {
            type: "success",
        });
    } catch (error) {
        env.services.notification.add(
            `${_t("Impossible d'imprimer via le pont")} (${url}) : ${error.message}`,
            { type: "danger", sticky: true }
        );
    }
    return { type: "ir.actions.act_window_close" };
}

registry.category("actions").add("product_barcode_print_intc.print", printBarcodes);
