// src/routes/register/+page.server.ts

import { fail, redirect } from "@sveltejs/kit";
import type { Actions } from "./$types";

export const actions: Actions = {
    default: async ({ request, locals: { supabase } }) => {
        const formData = await request.formData();
        const email = formData.get("email") as string;
        const password = formData.get("password") as string;

        // Validasi sederhana
        if (!email || !password) {
            return fail(400, {
                message: "Email dan password harus diisi.",
                success: false,
            });
        }

        // Memanggil fungsi signUp dari Supabase
        const { error } = await supabase.auth.signUp({
            email,
            password,
            // Opsi ini akan mengarahkan pengguna setelah mereka mengklik link konfirmasi
            options: {
                emailRedirectTo: `/`,
            },
        });

        // Jika ada error (misalnya, pengguna sudah terdaftar atau password lemah)
        if (error) {
            return fail(400, { message: error.message, success: false });
        }

        // Jika pendaftaran berhasil, arahkan pengguna ke halaman untuk memeriksa email
        redirect(303, "/check-email");
    },
};
