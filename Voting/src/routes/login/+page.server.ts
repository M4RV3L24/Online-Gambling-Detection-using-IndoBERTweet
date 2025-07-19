// src/routes/login/+page.server.ts
import { fail, redirect } from "@sveltejs/kit";
import type { Actions } from "./$types";

import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ locals: { supabase } }) => {
    const { data: { session } } = await supabase.auth.getSession();
    if (session) {
        throw redirect(303, "/");
    }
    return {};
};

export const actions: Actions = {
    default: async ({ request, locals: { supabase } }) => {
        const formData = await request.formData();
        const email = formData.get("email") as string;
        const password = formData.get("password") as string;

        const { error } = await supabase.auth.signInWithPassword({
            email,
            password,
        });

        if (error) {
            return fail(400, {
                message: "Invalid login credentials.",
                success: false,
            });
        }

        redirect(303, "/");
    },
};
