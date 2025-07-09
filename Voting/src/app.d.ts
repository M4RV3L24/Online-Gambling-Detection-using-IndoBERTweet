import type { SupabaseClient, Session, User } from '@supabase/supabase-js';
import type { Database } from '$lib/database.types'; // Anda perlu membuat ini nanti


// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
// declare global {
// 	namespace App {
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
// 	}
// }

// export {};

declare global {
  namespace App {
    interface Locals {
      supabase: SupabaseClient<Database>;
      safeGetSession(): Promise<{ session: Session | null; user: User | null }>;
      session: Session | null;
      user: User | null;
    }
    interface PageData {
      session: Session | null;
    }
    // interface Error {}
    // interface Platform {}
  }
}
