import { json } from '@sveltejs/kit';
import type { RequestHandler } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ request, locals }) => {
    try {
        const { excludeIds, limit = 500 } = await request.json();
        
        // Get the current user session
        const { session } = await locals.safeGetSession();
        if (!session?.user) {
            return json({ error: 'Unauthorized' }, { status: 401 });
        }
        
        console.log('API: Loading more texts for user:', session.user.id);
        console.log('API: Excluding IDs:', excludeIds.length);
        
        // Query based on your actual table structure
        let query = locals.supabase
            .from('texts_to_label')
            .select(`
                id,
                text_content,
                original_id,
                votes (
                    user_id,
                    vote,
                    skip
                )
            `)
            .order('id', { ascending: true })
            .limit(limit);
            
        // Exclude already loaded texts if there are any
        if (excludeIds && excludeIds.length > 0) {
            query = query.not('id', 'in', `(${excludeIds.join(',')})`);
        }
            
        const { data: texts, error } = await query;
        
        if (error) {
            console.error('Database error:', error);
            return json({ error: 'Database error' }, { status: 500 });
        }
        
        console.log('API: Found', texts?.length || 0, 'new texts');
        return json({ texts: texts || [] });
    } catch (error) {
        console.error('API error:', error);
        return json({ error: 'Internal server error' }, { status: 500 });
    }
};
