import React, { createContext, useContext, useState, ReactNode } from "react";

type UserCtx = { userId: string; setUserId: (id: string) => void };
const Ctx = createContext<UserCtx | null>(null);

export const UserProvider = ({ children }: { children: ReactNode }) => {
  const [userId, setUserId] = useState<string>("1");
  return <Ctx.Provider value={{ userId, setUserId }}>{children}</Ctx.Provider>;
};

export const useUser = () => {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useUser must be used within UserProvider");
  return ctx;
};