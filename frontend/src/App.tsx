import React from "react";
import "./App.css";
import { UserProvider } from "./context/UserContext";
import { UserSwitcher } from "./components/UserSwitcher";
import { CoinList } from "./components/CoinList";

export default function App() {
  return (
    <UserProvider>
      <main className="page">
        <div className="container">
          <h1>Available Coins</h1>
          <div className="headerRow">
            <UserSwitcher />
          </div>
          <CoinList />
        </div>
      </main>
    </UserProvider>
  );
}
