// src/routes/(protected)/dashboard/+page.server.ts
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ locals: { supabase } }) => {
    const { count: totalTexts } = await supabase
        .from("texts_to_label")
        .select("*", { count: "exact", head: true });

    const { count: totalVotes } = await supabase
        .from("votes")
        .select("*", { count: "exact", head: true });

    const { count: yesVotes } = await supabase
        .from("votes")
        .select("*", { count: "exact", head: true })
        .eq("vote", true);

    const noVotes = (totalVotes || 0) - (yesVotes || 0);

    return {
        stats: {
            totalTexts: totalTexts || 0,
            labeledTexts: totalVotes || 0,
            yesVotes: yesVotes || 0,
            noVotes: noVotes,
        },
    };
};
