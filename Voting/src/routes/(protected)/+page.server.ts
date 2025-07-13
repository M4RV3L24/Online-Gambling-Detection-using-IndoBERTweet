// src/routes/(protected)/+page.server.ts
import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({
    locals: { supabase, safeGetSession },
}) => {
    const { session } = await safeGetSession();
    if (!session) {
        // Ini seharusnya sudah ditangani oleh layout, tapi sebagai pengaman tambahan
        error(401, { message: "Unauthorized" });
    }

    const { data: unvotedText, error: rpcError } = await supabase
        .rpc("get_unvoted_text", { p_user_id: session.user.id })
        .single(); //.single() untuk mengambil satu baris saja

    if (rpcError) {
        console.error("Error fetching unvoted text:", rpcError);
        error(500, { message: "Failed to fetch new text to label." });
    }

    return {
        unvotedText,
    };
};

// Di dalam src/routes/(protected)/+page.server.ts
import { fail } from '@sveltejs/kit';
import type { Actions } from './$types';

export const actions: Actions = {
    vote: async ({ request, locals: { supabase, safeGetSession } }) => {
        const { session } = await safeGetSession();
        if (!session) {
            return fail(401, { message: "You must be logged in to vote." });
        }

        const formData = await request.formData();
        const textId = formData.get("text_id");
        const decision = formData.get("decision");

        if (!textId || !decision) {
            return fail(400, { message: "Invalid vote submission." });
        }

        const voteValue = decision === "yes";

        const { error } = await supabase.from("votes").insert({
            text_id: Number(textId),
            user_id: session.user.id,
            vote: voteValue,
        });

        if (error) {
            // Tangani kemungkinan error duplikat di sini jika perlu
            if (error.code === "23505") {
                // Kode error untuk pelanggaran unique constraint
                return { success: true, message: "Vote already recorded." };
            }
            return fail(500, { message: "Failed to record vote." });
        }

        return { success: true, message: "Vote recorded successfully!" };
    },
};
