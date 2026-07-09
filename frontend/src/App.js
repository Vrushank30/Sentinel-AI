import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import axios from 'axios';
import 'leaflet/dist/leaflet.css';

const API = 'https://web-production-f4b5e.up.railway.app';

const DISASTER_TYPES = [
  { label: '🌋 Earthquake', affected: [10, 11], description: 'Hospitals collapse' },
  { label: '🌊 Flood', affected: [20, 21], description: 'Water supply contaminated' },
  { label: '⚡ Power Failure', affected: [12, 13], description: 'Critical facilities down' },
];

function App() {
  const [nodes, setNodes] = useState([]);
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [simulationResult, setSimulationResult] = useState(null);
  const [failedIds, setFailedIds] = useState([]);
  const [selectedDisaster, setSelectedDisaster] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => { fetchNodes(); }, []);

  const fetchNodes = async () => {
    const res = await axios.get(`${API}/nodes`);
    setNodes(res.data);
  };

  const login = async () => {
    try {
      const res = await axios.post(`${API}/login`, { username, password });
      setToken(res.data.access_token);
      localStorage.setItem('token', res.data.access_token);
    } catch {
      alert('Invalid credentials');
    }
  };

  const register = async () => {
    try {
      await axios.post(`${API}/register`, { username, password });
      alert('Registered successfully! You can now login.');
    } catch {
      alert('Username already exists or registration failed.');
    }
  };

  const logout = () => {
    setToken('');
    localStorage.removeItem('token');
    setSimulationResult(null);
    setFailedIds([]);
  };

  const runSimulation = async () => {
    setLoading(true);
    try {
      const disaster = DISASTER_TYPES[selectedDisaster];
      const res = await axios.post(
        `${API}/simulate`,
        {
          affected_node_ids: disaster.affected,
          disaster_type: disaster.label
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setSimulationResult(res.data);
      setFailedIds(res.data.failed_nodes.map(n => n.id));
    } catch {
      alert('Simulation failed. Token may have expired. Please login again.');
      logout();
    }
    setLoading(false);
  };

  const reset = () => {
    setSimulationResult(null);
    setFailedIds([]);
  };

  const getColor = (nodeId) => failedIds.includes(nodeId) ? '#ff4444' : '#00cc44';

  const styles = {
    app: { fontFamily: 'Arial', background: '#0f1117', minHeight: '100vh', color: 'white', padding: '0' },
    header: { background: '#1a1d2e', padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #2d2f3e' },
    title: { margin: 0, fontSize: '24px' },
    subtitle: { margin: 0, color: '#888', fontSize: '13px' },
    body: { display: 'flex', height: 'calc(100vh - 65px)' },
    sidebar: { width: '280px', background: '#1a1d2e', padding: '20px', borderRight: '1px solid #2d2f3e', overflowY: 'auto' },
    map: { flex: 1 },
    card: { background: '#252837', borderRadius: '8px', padding: '12px', marginBottom: '12px' },
    cardTitle: { fontSize: '12px', color: '#888', textTransform: 'uppercase', marginBottom: '8px' },
    stat: { fontSize: '28px', fontWeight: 'bold' },
    nodeItem: { display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 0', borderBottom: '1px solid #2d2f3e', fontSize: '13px' },
    dot: (color) => ({ width: '10px', height: '10px', borderRadius: '50%', background: color, flexShrink: 0 }),
    select: { width: '100%', padding: '8px', background: '#252837', color: 'white', border: '1px solid #3d3f4e', borderRadius: '6px', marginBottom: '10px' },
    btn: (color) => ({ width: '100%', padding: '10px', background: color, color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', marginBottom: '8px' }),
    loginBox: { display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#0f1117' },
    loginCard: { background: '#1a1d2e', padding: '40px', borderRadius: '12px', width: '320px' },
    input: { width: '100%', padding: '10px', background: '#252837', color: 'white', border: '1px solid #3d3f4e', borderRadius: '6px', marginBottom: '12px', boxSizing: 'border-box' },
  };

  if (!token) {
    return (
      <div style={styles.loginBox}>
        <div style={styles.loginCard}>
          <h2 style={{ textAlign: 'center', marginBottom: '24px' }}>🛡️ Sentinel AI</h2>
          <p style={{ color: '#888', textAlign: 'center', marginBottom: '24px' }}>Disaster Infrastructure Simulation</p>
          <input style={styles.input} placeholder="Username" onChange={e => setUsername(e.target.value)} />
          <input style={styles.input} placeholder="Password" type="password" onChange={e => setPassword(e.target.value)} />
          <button style={styles.btn('#3b82f6')} onClick={login}>Login</button>
          <button style={styles.btn('#28a745')} onClick={register}>Register</button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.app}>
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>🛡️ Sentinel AI</h1>
          <p style={styles.subtitle}>Disaster Infrastructure Simulation Platform</p>
        </div>
        <button onClick={logout} style={{ background: 'transparent', border: '1px solid #3d3f4e', padding: '6px 14px', borderRadius: '6px', cursor: 'pointer', color: 'white' }}>
          Logout
        </button>
      </div>

      <div style={styles.body}>
        <div style={styles.sidebar}>
          <div style={styles.card}>
            <div style={styles.cardTitle}>Total Nodes</div>
            <div style={styles.stat}>{nodes.length}</div>
          </div>

          {simulationResult && (
            <>
              <div style={{ ...styles.card, borderLeft: '3px solid #ff4444' }}>
                <div style={styles.cardTitle}>Failed</div>
                <div style={{ ...styles.stat, color: '#ff4444' }}>{simulationResult.failed_count}</div>
              </div>
              <div style={{ ...styles.card, borderLeft: '3px solid #00cc44' }}>
                <div style={styles.cardTitle}>Operational</div>
                <div style={{ ...styles.stat, color: '#00cc44' }}>{simulationResult.operational_count}</div>
              </div>
            </>
          )}

          <div style={styles.card}>
            <div style={styles.cardTitle}>Infrastructure Nodes</div>
            {nodes.map(node => (
              <div key={node.id} style={styles.nodeItem}>
                <div style={styles.dot(failedIds.includes(node.id) ? '#ff4444' : '#00cc44')} />
                <div>
                  <div>{node.name}</div>
                  <div style={{ color: '#888', fontSize: '11px' }}>{node.type}</div>
                </div>
              </div>
            ))}
          </div>

          <div style={styles.card}>
            <div style={styles.cardTitle}>Disaster Scenario</div>
            <select style={styles.select} onChange={e => setSelectedDisaster(parseInt(e.target.value))}>
              {DISASTER_TYPES.map((d, i) => (
                <option key={i} value={i}>{d.label}</option>
              ))}
            </select>
            <p style={{ color: '#888', fontSize: '12px', marginBottom: '12px' }}>
              {DISASTER_TYPES[selectedDisaster].description}
            </p>
            <button style={styles.btn('#dc3545')} onClick={runSimulation} disabled={loading}>
              {loading ? 'Simulating...' : '▶ Run Simulation'}
            </button>
            {simulationResult && (
              <button style={styles.btn('#6c757d')} onClick={reset}>
                🔄 Reset
              </button>
            )}
          </div>
        </div>

        <div style={styles.map}>
          <MapContainer key={failedIds.join(',')} center={[12.9716, 77.5946]} zoom={13}
            style={{ height: '100%', width: '100%' }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            {nodes.map(node => (
              <CircleMarker key={node.id} center={[node.latitude, node.longitude]}
                radius={18} color={getColor(node.id)} fillColor={getColor(node.id)} fillOpacity={0.8}>
                <Popup>
                  <b>{node.name}</b><br />
                  Type: {node.type}<br />
                  Status: {failedIds.includes(node.id) ? '❌ Failed' : '✅ Operational'}
                </Popup>
              </CircleMarker>
            ))}
          </MapContainer>
        </div>
      </div>
    </div>
  );
}

export default App;