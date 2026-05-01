import React, { useState } from 'react';
import IncidentList   from './components/IncidentList';
import IncidentDetail from './components/IncidentDetail';

function App() {
  const [selected, setSelected] = useState(null);

  return (
    <div className="app">
      <nav className="navbar">
        <h1>🚨 SRE Incident Management System</h1>
        <span>Zeotap Assignment</span>
      </nav>
      <main className="main">
        {selected
          ? <IncidentDetail id={selected} onBack={() => setSelected(null)} />
          : <IncidentList onSelect={setSelected} />
        }
      </main>
    </div>
  );
}

export default App;