"use client";

import { useState } from "react";
import { CredentialResponse, GoogleLogin } from "@react-oauth/google";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Loader2 } from "lucide-react";

interface SignInModalProps {
  onSuccess: (credentialResponse: CredentialResponse) => void;
  onError?: () => void;
  isLoading?: boolean;
}

export function SignInModal({ onSuccess, onError, isLoading = false }: SignInModalProps) {
  const [email, setEmail] = useState("");
  const [emailLoading, setEmailLoading] = useState(false);

  const handleEmailContinue = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    
    setEmailLoading(true);
    // Email flow not fully implemented yet - placeholder
    setTimeout(() => {
      setEmailLoading(false);
      alert("Email authentication not yet implemented. Please use Google Sign In.");
    }, 1000);
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-md p-8 space-y-6 animate-in fade-in-0 zoom-in-95 duration-300">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-gray-900">Sign in to CoinGrok</h1>
        </div>

        {/* Google Sign In */}
        <div className="space-y-4">
          <div className="flex justify-center">
            {isLoading ? (
              <div className="flex items-center justify-center w-full h-12 border border-gray-300 rounded-lg bg-gray-50">
                <Loader2 className="w-4 h-4 animate-spin text-gray-500" />
              </div>
            ) : (
              <div className="w-full [&>div]:w-full [&>div>div]:!w-full [&>div>div>div]:!w-full [&_button]:!w-full [&_button]:!h-12 [&_button]:!border [&_button]:!border-gray-300 [&_button]:!rounded-lg [&_button]:!shadow-none [&_button]:!bg-white [&_button]:hover:!bg-gray-50 [&_button]:!transition-colors [&_button]:!duration-200">
                <GoogleLogin
                  onSuccess={onSuccess}
                  onError={onError}
                  text="signin_with"
                  theme="outline"
                  size="large"
                  width="100%"
                />
              </div>
            )}
          </div>

          {/* Divider */}
          <div className="relative">
            <Separator />
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="bg-white px-2 text-sm text-gray-500">or</span>
            </div>
          </div>

          {/* Email Form */}
          <form onSubmit={handleEmailContinue} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email" className="sr-only">
                Email
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="h-12 border-gray-300"
                disabled={emailLoading}
              />
            </div>
            <Button
              type="submit"
              className="w-full h-12 bg-gray-900 hover:bg-gray-800 text-white"
              disabled={!email || emailLoading}
            >
              {emailLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Please wait...
                </>
              ) : (
                "Continue"
              )}
            </Button>
          </form>
        </div>

        {/* Footer */}
        <div className="text-center">
          <p className="text-sm text-gray-600">
            Don&apos;t have an account?{" "}
            <button className="text-gray-900 hover:underline font-medium">
              Sign up
            </button>
          </p>
        </div>

        {/* Google Attribution Footer - Compliant with Google Brand Guidelines */}
        <div className="flex items-center justify-center pt-4 border-t border-gray-100 space-x-2">
          <img 
            src="/google-g-logo.svg" 
            alt="Google"
            className="w-4 h-4"
            aria-hidden="true"
          />
          <p className="text-xs text-gray-500">
            Authentication uses Google OAuth
          </p>
        </div>
        <div className="text-center">
          <p className="text-xs text-gray-400 mt-1">
            Google is a trademark of Google LLC
          </p>
        </div>
      </div>
    </div>
  );
}