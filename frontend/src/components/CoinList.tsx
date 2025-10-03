import React, { useEffect, useState } from "react";
import { fetchBalances, type Coin } from "../lib/api";
import { useUser } from "../context/UserContext";


const logoFor = (symbol: string) => {
  switch (symbol.toUpperCase()) {
    case "BTC": return "/assets/btc.svg";
    case "BCH": return "/assets/bch.svg";
    case "ETH": return "/assets/eth.svg";
    case "LTC": return "/assets/ltc.svg";
    case "XLM": return "/assets/xlm.svg";
    default:    return undefined;
  }
};

const usd = (n: number) =>
  n.toLocaleString("en-US", { style: "currency", currency: "USD", minimumFractionDigits: 2, maximumFractionDigits: 2 });

const amt = (n: number) =>
  n.toLocaleString("en-US", { minimumFractionDigits: 8, maximumFractionDigits: 8 });

export const CoinList: React.FC = () => {
  const { userId } = useUser();
  const [data, setData] = useState<Coin[] | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchBalances(userId)
      .then(setData)
      .catch((e) => setErr(e.message || "Failed to load"))
      .finally(() => setLoading(false));
  }, [userId]);

  if (loading) return <p className="muted">Loading…</p>;
  if (err) return <p className="error">Error: {err}</p>;
  if (!data) return null;

  return (
    <div className="coins sampleTheme">
      {data.map((c) => {
        const hasHoldings = c.amount > 0;
        const actionLabel = hasHoldings ? "Trade" : "Buy";
        return (
          <article key={c.symbol} className="sampleCard">
            <div className="left">
              <div className="sampleLogoWrap">
                {logoFor(c.symbol) ? (
                  <img className="sampleLogo" alt={c.name} src={logoFor(c.symbol)!} />
                ) : (
                  <div className="sampleLogoFallback">{c.symbol[0]}</div>
                )}
              </div>
              <div className="sampleMeta">
                <div className="sampleName">{c.name}</div>
                <div className="samplePrice">{usd(c.price)}</div>
              </div>
            </div>

            <div className="right">
              <div className="sampleValue">{usd(c.value)}</div>
              <div className="sampleAmount">{amt(c.amount)} {c.symbol}</div>
            </div>

            <button className={`sampleCta ${hasHoldings ? "trade" : "buy"}`}>
              {actionLabel}
            </button>
          </article>
        );
      })}
    </div>
  );
};
