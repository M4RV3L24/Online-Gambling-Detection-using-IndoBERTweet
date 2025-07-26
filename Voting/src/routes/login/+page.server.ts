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

        // Basic validation
        if (!email || !password) {
            return fail(400, {
                message: "Email and password are required.",
                success: false,
                errors: {
                    email: !email ? "Email is required" : "",
                    password: !password ? "Password is required" : ""
                }
            });
        }

        // Email format validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            return fail(400, {
                message: "Please enter a valid email address.",
                success: false,
                errors: {
                    email: "Invalid email format"
                }
            });
        }

        const { error } = await supabase.auth.signInWithPassword({
            email,
            password,
        });

        if (error) {
            // Handle different types of auth errors
            let message = "Login failed. Please try again.";
            if (error.message.includes("Invalid login credentials")) {
                message = "Invalid email or password. Please check your credentials.";
            } else if (error.message.includes("Email not confirmed")) {
                message = "Please check your email and click the confirmation link before signing in.";
            } else if (error.message.includes("Too many requests")) {
                message = "Too many login attempts. Please wait a moment and try again.";
            }

            return fail(400, {
                message,
                success: false,
                errors: {
                    general: message
                }
            });
        }

        redirect(303, "/");
    },
};
