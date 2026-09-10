import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'WIN4SMEs — Innowacje w miejscu pracy', description: 'Program i pełne scenariusze szkolne ZSZ5.' };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="pl"><body>{children}</body></html>;
}
