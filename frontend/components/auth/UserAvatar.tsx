"use client";

import { useState } from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { UserDropdown } from "./UserDropdown";

interface UserAvatarProps {
  user: {
    email?: string;
    sub?: string;
    picture?: string;
    name?: string;
  };
  onLogout: () => void;
}

export function UserAvatar({ user, onLogout }: UserAvatarProps) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

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

  return (
    <div className="relative">
      <button
        onClick={() => setIsDropdownOpen(!isDropdownOpen)}
        className="relative focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 rounded-full transition-all duration-200 hover:ring-2 hover:ring-purple-300 hover:ring-offset-2"
        aria-label="User menu"
      >
        <Avatar className="w-8 h-8 border-2 border-white shadow-sm">
          <AvatarImage 
            src={user.picture} 
            alt={user.name || user.email || "User avatar"} 
          />
          <AvatarFallback className="bg-gradient-to-br from-purple-500 to-cyan-400 text-white text-sm font-medium">
            {initials}
          </AvatarFallback>
        </Avatar>
      </button>

      {isDropdownOpen && (
        <UserDropdown
          user={user}
          onLogout={onLogout}
          onClose={() => setIsDropdownOpen(false)}
        />
      )}
    </div>
  );
}