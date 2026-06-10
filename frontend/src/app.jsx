// Aurora front-end · single full-page direction wired to data/data.json,
// which is generated from the repo CSVs by `python -m src.build_frontend_data`.

const ACCENT = "#5EEAD4";

function App() {
  const { data, err } = useScaleData();
  const [showAbout, setShowAbout] = React.useState(false);

  React.useEffect(() => {
    // wire footer "about" link
    const handler = (e) => {
      const a = e.target.closest('a[href="#about"]');
      if (a) { e.preventDefault(); setShowAbout(true); }
    };
    document.addEventListener("click", handler);
    return () => document.removeEventListener("click", handler);
  }, []);

  if (err) return (
    <div style={{ padding: 40, color: "#F87171", fontFamily: "monospace" }}>
      Failed to load data.json: {err}
      <div style={{ color: "#888", marginTop: 8 }}>Serve the frontend folder via http — the app fetches data/data.json.</div>
    </div>
  );

  return (
    <AuroraDashboard
      data={data}
      scenario="current"
      region={data ? data.region : ""}
      accent={ACCENT}
      showAbout={showAbout}
      setShowAbout={setShowAbout}
    />
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
