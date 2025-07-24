// src/routes/auth/callback/+server.ts

import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ url, locals: { supabase } }) => {
    const code = url.searchParams.get('code');
    const token_hash = url.searchParams.get('token_hash');
    const type = url.searchParams.get('type');
    const next = url.searchParams.get('next') ?? '/';

    // Handle new PKCE flow
    if (code) {
        const { error } = await supabase.auth.exchangeCodeForSession(code);
        
        if (!error) {
            redirect(303, `/${next.slice(1)}`);
        }
    }

    // Handle legacy email confirmation flow
    if (token_hash && type === 'email') {
        const { error } = await supabase.auth.verifyOtp({
            token_hash,
            type: 'email'
        });
        
        if (!error) {
            redirect(303, '/');
        }
    }

    // Return the user to an error page with instructions
    redirect(303, '/auth/auth-code-error');
};
