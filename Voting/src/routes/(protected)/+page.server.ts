// src/routes/(protected)/+page.server.ts

import { error, fail, redirect } from "@sveltejs/kit";
import type { PageServerLoad, Actions } from "./$types";

export const load: PageServerLoad = async ({
    url,
    locals: { supabase, safeGetSession },
}) => {
    const { session } = await safeGetSession();
    if (!session) {
        throw redirect(303, "/login");
    }

    // Ambil parameter sort dan filter dari URL
    const sortBy = url.searchParams.get("sort") || "id_asc"; // Default sort by id ascending
    const filterBy = url.searchParams.get("filter") || "all"; // Default show all

    // Bangun kueri dasar
    let query = supabase
        .from("texts_to_label")
        .select("*, votes:votes(user_id, vote, skip)")
        .order("id", { ascending: true });

    // Terapkan pengurutan
    // Logika utama: selalu tampilkan yang belum divoting di atas, lalu urutkan sisanya.
    const [sortColumn, sortDirection] = sortBy.split("_");
    query = query
        .order("vote", {
            foreignTable: "votes",
            ascending: true,
            nullsFirst: true,
        })
        .order(sortColumn, { ascending: sortDirection === "asc" });

    // Eksekusi kueri
    const { data: texts, error: dbError } = await query;

    // Server-side filter for current user
    let filteredTexts = texts ?? [];
    if (filterBy === "voted_yes") {
        filteredTexts = filteredTexts.filter((t) =>
            t.votes.some((v) => v.user_id === session.user.id && v.vote === true && (!v.skip || v.skip === 0))
        );
    } else if (filterBy === "voted_no") {
        filteredTexts = filteredTexts.filter((t) =>
            t.votes.some((v) => v.user_id === session.user.id && v.vote === false && (!v.skip || v.skip === 0))
        );
    } else if (filterBy === "all") {
        // Show only texts that are unvoted and not skipped by the current user
        filteredTexts = filteredTexts.filter((t) =>
            !t.votes.some((v) => v.user_id === session.user.id) &&
            !t.votes.some((v) => v.user_id === session.user.id && v.skip === 1)
        );
    } else {
        filteredTexts = filteredTexts.filter((t) => {
            // Filter for unvoted texts (fallback for other filters)
            (!t.votes.some((v) => v.user_id === session.user.id) &&
            !t.votes.some((v) => v.user_id === session.user.id && v.skip === 1)) ||
            t.votes.some((v) => v.user_id === session.user.id && v.skip === 0 && v.vote === null);
        });
    }
    filteredTexts = filteredTexts.slice(0, 200);

    const { count: already_vote_count, error: countError } = await supabase
        .from("votes")
        .select("", { count: "exact", head: true })
        .eq("user_id", session.user.id)
        .or("skip.is.null,skip.eq.0");

    if (countError) {
        console.error("Error counting votes:", countError);
    }

    if (dbError) {
        console.error("Error fetching texts:", dbError);
        error(500, { message: "Failed to fetch texts to label." });
    }

    return {
        already_vote_count: already_vote_count ?? 0,
        texts: filteredTexts ?? [],
        sortBy,
        filterBy,
    };
};

export const actions: Actions = {
    // Aksi untuk memilih 'Yes' atau 'No'
    vote: async ({ request, locals: { supabase, safeGetSession } }) => {
        const { session } = await safeGetSession();
        if (!session) {
            return fail(401, { message: "You must be logged in to vote." });
        }

        const formData = await request.formData();
        const textId = formData.get("text_id");
        const decision = formData.get("vote"); // 'yes' or 'no'

        if (!textId || !decision) {
            return fail(400, { message: "Invalid vote submission." });
        }

        const voteValue = decision === "yes";
        console.log(
            `User ${session.user.id} voted ${voteValue} for text ID ${textId}`
        );
        // Gunakan upsert untuk membuat atau memperbarui vote
        const { error } = await supabase.from("votes").upsert(
            {
                text_id: Number(textId),
                user_id: session.user.id,
                vote: voteValue,
            },
            { onConflict: "text_id, user_id" }
        ); // Kunci unik untuk upsert

        console.log(error);
        if (error) {
            return fail(500, {
                message: "Failed to record vote.",
                success: false,
            });
        }

        return {
            success: true,
            message: `Vote '${decision.toUpperCase()}' recorded!`,
        };
    },
    skip: async ({ request, locals: { supabase, safeGetSession } }) => {
        const { session } = await safeGetSession();
        if (!session) {
            return fail(401, { message: "You must be logged in." });
        }

        const formData = await request.formData();
        const textId = formData.get("text_id");

        if (!textId) {
            return fail(400, { message: "Invalid request." });
        }

        const { error } = await supabase
            .from("votes")
            .upsert({
                text_id: Number(textId),
                user_id: session.user.id,
                skip: 1, // Tandai sebagai skip
            });

        console.log(error);
        if (error) {
            return fail(500, {
                message: "Failed to record vote.",
                success: false,
            });
        }

        // Aksi untuk melewati teks
        return { success: true, message: "Skipped the text." };
    },

    // Aksi baru untuk membatalkan vote
    undoVote: async ({ request, locals: { supabase, safeGetSession } }) => {
        const { session } = await safeGetSession();
        if (!session) {
            return fail(401, { message: "You must be logged in." });
        }

        const formData = await request.formData();
        const textId = formData.get("text_id");

        if (!textId) {
            return fail(400, { message: "Invalid request." });
        }

        const { error } = await supabase
            .from("votes")
            .delete()
            .match({ text_id: Number(textId), user_id: session.user.id });

        if (error) {
            return fail(500, {
                message: "Failed to undo vote.",
                success: false,
            });
        }

        return { success: true, message: "Vote undone!" };
    },

    logout: async ({ locals: { supabase } }) => {
        await supabase.auth.signOut();
        throw redirect(303, "/login");
    },
};
