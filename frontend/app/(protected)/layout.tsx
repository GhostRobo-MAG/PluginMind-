// Note: Authentication is now handled individually by each page using AuthModal
// This layout file is kept for future protected routes that might need it
export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}