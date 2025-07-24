// src/routes/register/+page.server.ts

import { fail, redirect } from "@sveltejs/kit";
import type { Actions } from "./$types";

export const actions: Actions = {
    default: async ({ request, locals: { supabase } }) => {
        const formData = await request.formData();
        const email = formData.get("email") as string;
        const password = formData.get("password") as string;
        const confirmPassword = formData.get("confirm_password") as string;

        // Enhanced validation
        if (!email || !password || !confirmPassword) {
            return fail(400, {
                message: "Semua field harus diisi.",
                success: false,
                errors: {
                    email: !email ? "Email harus diisi" : "",
                    password: !password ? "Password harus diisi" : "",
                    confirmPassword: !confirmPassword ? "Konfirmasi password harus diisi" : ""
                }
            });
        }

        // Email format validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            return fail(400, {
                message: "Format email tidak valid.",
                success: false,
                errors: {
                    email: "Format email tidak valid"
                }
            });
        }

        // Password strength validation
        if (password.length < 6) {
            return fail(400, {
                message: "Password harus minimal 6 karakter.",
                success: false,
                errors: {
                    password: "Password harus minimal 6 karakter"
                }
            });
        }

        // Password confirmation validation
        if (password !== confirmPassword) {
            return fail(400, {
                message: "Password dan konfirmasi password tidak cocok.",
                success: false,
                errors: {
                    confirmPassword: "Password tidak cocok"
                }
            });
        }

        // Sign up with Supabase
        const requestUrl = new URL(request.url);
        const { error } = await supabase.auth.signUp({
            email,
            password,
            options: {
                emailRedirectTo: `${requestUrl.origin}/auth/confirm`,
                // data: {
                //     full_name: name
                // }
            },
        });

        // Handle errors from Supabase
        if (error) {
            // Common Supabase auth errors
            let message = error.message;
            if (error.message.includes("already registered")) {
                message = "Email sudah terdaftar. Silakan gunakan email lain atau login.";
            } else if (error.message.includes("weak password")) {
                message = "Password terlalu lemah. Gunakan kombinasi huruf, angka, dan simbol.";
            } else if (error.message.includes("invalid email")) {
                message = "Format email tidak valid.";
            }

            return fail(400, { 
                message, 
                success: false,
                errors: {
                    general: message
                }
            });
        }

        // Registration successful - redirect to check email page
        redirect(303, "/check-email");
    },
};
