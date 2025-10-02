import React from "react";
import { useUser } from "../context/UserContext";

export const UserSwitcher: React.FC = () => {
  const { userId, setUserId } = useUser();
  return (
    <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
      <span>User:</span>
      <select
        value={userId}
        onChange={(e) => setUserId(e.target.value)}
        aria-label="Select user"
      >
        <option value="1">User 1</option>
        <option value="2">User 2</option>
      </select>
    </div>
  );
};
