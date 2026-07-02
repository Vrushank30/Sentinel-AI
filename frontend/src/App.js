import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import axios from 'axios';
import 'leaflet/dist/leaflet.css';

const API = 'http://localhost:8000';

function App() {
  const [nodes, setNodes] = useState([]);
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [simulationResult, setSimulationResult] = useState(null);
  const [failedIds, setFailedIds] = useState([]);

  useEffect(() => {
    fetchNodes();
  }, []);

  const fetchNodes = async () => {
    const res = await axios.get(`${API}/nodes`);
    setNodes(res.data);
  };

  const login = async () => {
    const res = await axios.post(`${API}/login`, { username, password });
    setToken(res.data.access_token);
    localStorage.setItem('token', res.data.access_token);
    alert('Logged in successfully!');
  };

  const runSimulation = async () => {
    const edges = [
      { from_node: 1, to_node: 2 },
      { from_node: 2, to_node: 3 },
      { from_node: 2, to_node: 4 },
    ];
    const res = await axios.post(
      `${API}/simulate`,
      { affected_node_ids: [2], edges },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    setSimulationResult(res.data);
    setFailedIds(res.data.failed_nodes.map(n => n.id));
  };

  const getColor = (nodeId) => failedIds.includes(nodeId) ? 'red' : 'green';

  return (
    <div style={{ fontFamily: 'Arial', padding: '20px' }}>
      <h1>🛡️ Sentinel AI</h1>
      <p>Disaster Infrastructure Simulation Platform</p>

      {!token && (
        <div style={{ marginBottom: '20px' }}>
          <input placeholder="Username" onChange={e => setUsername(e.target.value)}
            style={{ marginRight: '10px', padding: '8px' }} />
          <input placeholder="Password" type="password" onChange={e => setPassword(e.target.value)}
            style={{ marginRight: '10px', padding: '8px' }} />
          <button onClick={login} style={{ padding: '8px 16px', background: '#007bff', color: 'white', border: 'none', cursor: 'pointer' }}>
            Login
          </button>
        </div>
      )}

      {token && (
        <button onClick={runSimulation}
          style={{ marginBottom: '20px', padding: '10px 20px', background: '#dc3545', color: 'white', border: 'none', cursor: 'pointer', fontSize: '16px' }}>
          🌋 Simulate Earthquake on Power Station
        </button>
      )}

      {simulationResult && (
        <div style={{ marginBottom: '20px', padding: '10px', background: '#f8f9fa', borderRadius: '8px' }}>
          <p>❌ Failed nodes: {simulationResult.failed_count}</p>
          <p>✅ Operational nodes: {simulationResult.operational_count}</p>
        </div>
      )}

      <MapContainer key={failedIds.join(',')} center={[12.9716, 77.5946]} zoom={13}
        style={{ height: '500px', width: '100%', borderRadius: '8px' }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {nodes.map(node => (
          <CircleMarker key={node.id} center={[node.latitude, node.longitude]}
            radius={15} color={getColor(node.id)} fillOpacity={0.8}>
            <Popup>
              <b>{node.name}</b><br />
              Type: {node.type}<br />
              Status: {failedIds.includes(node.id) ? '❌ Failed' : '✅ Operational'}
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}

export default App;