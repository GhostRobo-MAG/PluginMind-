"use client";
import { useRouter } from "next/navigation";

export const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const router = useRouter();
  const token = localStorage.getItem('token');
  if (!token) {
    router.push('/login');
    return <div style={{ color: "#fff", textAlign: "center", marginTop: "20vh" }}>Loading...</div>;
  }
  return children;
};