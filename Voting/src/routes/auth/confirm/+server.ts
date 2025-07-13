// src/routes/auth/confirm/+server.ts

import { redirect } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";

export const GET: RequestHandler = async ({ url, locals: { supabase } }) => {
    const token_hash = url.searchParams.get("token_hash");
    const type = url.searchParams.get("type");
    const next = url.searchParams.get("next") ?? "/";

    if (token_hash && type) {
        const { error } = await supabase.auth.verifyOtp({ token_hash, type });
        if (!error) {
            redirect(303, `/${next.slice(1)}`);
        }
    }

    // Arahkan ke halaman error jika token tidak valid
    redirect(303, "/auth/auth-code-error");
};
