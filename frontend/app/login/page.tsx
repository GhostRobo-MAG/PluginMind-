"use client";
import { CredentialResponse, GoogleLogin, GoogleOAuthProvider } from '@react-oauth/google';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();

  const handleSuccess = (credentialResponse: CredentialResponse) => {
    if (!credentialResponse.credential) {
      alert('Login Failed!');
      return;
    }
    // Save the Google ID token (JWT) to localStorage
    localStorage.setItem('token', credentialResponse.credential);
    // Redirect to /analyze
    router.push('/analyze');
  };

  return (
    <GoogleOAuthProvider clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID!}>
        <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-dark-navy via-darker-navy to-dark-navy">
        <h1 className="text-2xl mb-4 text-white">Sign in to CoinGrok</h1>
        <GoogleLogin
            onSuccess={handleSuccess}
            onError={() => alert('Login Failed')}
            useOneTap
        />
        </div>
    </GoogleOAuthProvider>  
  );
}