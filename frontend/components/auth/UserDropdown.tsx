"use client";

import { useEffect, useRef } from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { Settings, LogOut } from "lucide-react";

interface UserDropdownProps {
  user: {
    email?: string;
    sub?: string;
    picture?: string;
    name?: string;
  };
  onLogout: () => void;
  onClose: () => void;
}

export function UserDropdown({ user, onLogout, onClose }: UserDropdownProps) {
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        onClose();
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [onClose]);

  // Get user's initials for fallback
  const getInitials = (email?: string, name?: string) => {
    if (name) {
      const names = name.split(" ");
      return names.length > 1 
        ? `${names[0][0]}${names[names.length - 1][0]}`.toUpperCase()
        : names[0][0].toUpperCase();
    }
    if (email) {
      return email[0].toUpperCase();
    }
    return "U";
  };

  const initials = getInitials(user.email, user.name);
  const displayName = user.name || user.email?.split("@")[0] || "User";
  const displayEmail = user.email || "";

  const handleManageAccount = () => {
    // Future feature - placeholder for now
    alert("Account management coming soon!");
    onClose();
  };

  const handleLogout = () => {
    onLogout();
    onClose();
  };

  return (
    <div 
      ref={dropdownRef}
      className="absolute right-0 top-12 w-72 bg-white rounded-lg shadow-xl border border-gray-200 py-2 z-50 animate-in fade-in-0 zoom-in-95 duration-200"
      style={{ transformOrigin: "top right" }}
    >
      {/* User Info Section */}
      <div className="px-4 py-3">
        <div className="flex items-center space-x-3">
          <Avatar className="w-10 h-10 border border-gray-200">
            <AvatarImage 
              src={user.picture} 
              alt={user.name || user.email || "User avatar"} 
            />
            <AvatarFallback className="bg-gradient-to-br from-purple-500 to-cyan-400 text-white font-medium">
              {initials}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-semibold text-gray-900 truncate">
              {displayName}
            </div>
            {displayEmail && (
              <div className="text-xs text-gray-500 truncate">
                {displayEmail}
              </div>
            )}
          </div>
        </div>
      </div>

      <Separator />

      {/* Menu Items */}
      <div className="py-1">
        <button
          onClick={handleManageAccount}
          className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors duration-150"
        >
          <Settings className="w-4 h-4 mr-3 text-gray-500" />
          Manage account
        </button>
        
        <button
          onClick={handleLogout}
          className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors duration-150"
        >
          <LogOut className="w-4 h-4 mr-3 text-gray-500" />
          Sign out
        </button>
      </div>

      <Separator />

      {/* Footer */}
      <div className="px-4 py-2">
        <div className="flex items-center justify-center space-x-2">
          <img 
            src="/google-g-logo.svg" 
            alt="Google"
            className="w-3 h-3"
            aria-hidden="true"
          />
          <p className="text-xs text-gray-400">Signed in with Google</p>
        </div>
      </div>
    </div>
  );
}