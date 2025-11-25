import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const socket = io('http://localhost:5000');

function App() {
  const [connected, setConnected] = useState(false); // Server connection
  const [ethercatConnected, setEthercatConnected] = useState(false); // EtherCAT connection
  const [motorData, setMotorData] = useState({});
  const [history, setHistory] = useState({});
  const [showParamVis, setShowParamVis] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    socket.on('connect', () => {
      console.log('Connected to server');
      setConnected(true);
    });

    socket.on('disconnect', () => {
      console.log('Disconnected from server');
      setConnected(false);
      setEthercatConnected(false);
    });

    socket.on('status_update', (data) => {
      setMotorData(data);
      updateHistory(data);
    });

    socket.on('ethercat_connected', (response) => {
      if (response.status === 'error') {
        setError(response.message);
        setEthercatConnected(false);
      } else {
        setEthercatConnected(true);
      }
    });

    return () => {
      socket.off('connect');
      socket.off('disconnect');
      socket.off('status_update');
      socket.off('ethercat_connected');
    };
  }, []);

  const updateHistory = (data) => {
    setHistory(prev => {
      const newHistory = { ...prev };
      Object.keys(data).forEach(key => {
        if (!newHistory[key]) newHistory[key] = [];
        newHistory[key].push({
          time: new Date().toLocaleTimeString(),
          velocity: data[key].velocity || 0,
          position: data[key].position || 0,
          load: data[key].load || 0,
          torque: data[key].torque || 0
        });
        if (newHistory[key].length > 50) newHistory[key].shift();
      });
      return newHistory;
    });
  };

  const handleStart = () => {
    socket.emit('connect_ethercat');
  };

  const handleSliderChange = (type, index, value) => {
    socket.emit('set_motor_command', { type, index, value });
  };

  const handleSwitch = (type, state) => {
    socket.emit('toggle_switch', { type, state });
  };

  return (
    <div style={{
      backgroundColor: '#111827',
      height: '100vh',
      width: '100vw',
      color: 'white',
      fontFamily: 'sans-serif',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      {/* Menu Bar */}
      <div style={{
        backgroundColor: '#1F2937',
        padding: '5px 15px',
        borderBottom: '1px solid #374151',
        display: 'flex',
        alignItems: 'center',
        height: '35px',
        fontSize: '13px'
      }}>
        <div style={{ position: 'relative', cursor: 'pointer', marginRight: '15px' }}
          onClick={() => setShowParamVis(true)}>
          <span style={{ color: '#D1D5DB' }}>Parameter View</span>
        </div>
        <div style={{ color: '#6B7280' }}>Help</div>
      </div>

      {/* Header */}
      <header style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '10px 20px',
        borderBottom: '1px solid #374151',
        backgroundColor: '#111827'
      }}>
        <h1 style={{ fontSize: '20px', fontWeight: 'bold', color: '#EF4444', margin: 0 }}>EtherCAT Control</h1>
        <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
          {/* Server Status */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: connected ? '#10B981' : '#EF4444' }}></div>
            <span style={{ fontSize: '11px', color: '#9CA3AF' }}>Server</span>
          </div>

          {/* EtherCAT System Status */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: ethercatConnected ? '#10B981' : '#EF4444' }}></div>
            <span style={{ fontSize: '11px', color: '#9CA3AF' }}>System</span>
          </div>

          <button
            onClick={handleStart}
            disabled={ethercatConnected}
            style={{
              backgroundColor: ethercatConnected ? '#059669' : '#2563EB',
              color: 'white',
              padding: '6px 16px',
              borderRadius: '4px',
              border: 'none',
              cursor: ethercatConnected ? 'default' : 'pointer',
              fontWeight: '600',
              fontSize: '13px',
              transition: 'background 0.2s',
              opacity: ethercatConnected ? 0.8 : 1
            }}
          >
            {ethercatConnected ? 'System Running' : 'Start System'}
          </button>
        </div>
      </header>

      {/* Main Content Grid */}
      <div style={{
        flex: 1,
        padding: '10px',
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gridTemplateRows: 'repeat(2, 1fr)',
        gap: '10px',
        overflow: 'hidden'
      }}>
        {[1, 2, 3, 4].map(i => (
          <SystemPanel
            key={i}
            index={i}
            data={motorData}
            history={history}
            onSliderChange={handleSliderChange}
            onSwitch={handleSwitch}
          />
        ))}
      </div>

      {/* Parameter Visualisation Modal */}
      {showParamVis && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.7)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: '#1F2937',
            width: '95%',
            height: '95%',
            borderRadius: '8px',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            border: '1px solid #374151'
          }}>
            <div style={{
              padding: '10px 15px',
              borderBottom: '1px solid #374151',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              backgroundColor: '#111827'
            }}>
              <h2 style={{ margin: 0, fontSize: '16px', fontWeight: 'bold' }}>Parameter Visualisation</h2>
              <button
                onClick={() => setShowParamVis(false)}
                style={{ background: 'none', border: 'none', color: '#9CA3AF', cursor: 'pointer', fontSize: '18px' }}
              >×</button>
            </div>
            <div style={{ flex: 1, padding: '10px', overflow: 'hidden' }}>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gridTemplateRows: 'repeat(2, 1fr)',
                gap: '10px',
                height: '100%'
              }}>
                {/* Velocity Motors 1-4 */}
                {[1, 2, 3, 4].map(i => (
                  <DetailedPanel key={`vel_${i}`} type="velocity" index={i} data={motorData} history={history} />
                ))}
                {/* Position Motors 1-4 */}
                {[1, 2, 3, 4].map(i => (
                  <DetailedPanel key={`pos_${i}`} type="position" index={i} data={motorData} history={history} />
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error Modal */}
      {error && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.8)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 2000
        }}>
          <div style={{
            backgroundColor: '#1F2937',
            padding: '20px',
            borderRadius: '8px',
            border: '1px solid #EF4444',
            maxWidth: '400px',
            width: '100%',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)'
          }}>
            <h3 style={{ color: '#EF4444', marginTop: 0, display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '24px' }}>⚠️</span> Error
            </h3>
            <p style={{ color: '#D1D5DB', marginBottom: '20px' }}>{error}</p>
            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button
                onClick={() => setError(null)}
                style={{
                  backgroundColor: '#374151',
                  color: 'white',
                  border: 'none',
                  padding: '8px 16px',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontWeight: 'bold'
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const SystemPanel = ({ index, data, history, onSliderChange, onSwitch }) => {
  const velKey = `velocity_${index}`;
  const posKey = `position_${index}`;
  const velData = data[velKey] || {};
  const posData = data[posKey] || {};
  const velHistory = history[velKey] || [];
  const posHistory = history[posKey] || [];

  return (
    <div style={{
      backgroundColor: '#1F2937',
      borderRadius: '8px',
      padding: '10px',
      border: '1px solid #374151',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      overflow: 'hidden'
    }}>
      <h2 style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '5px', color: '#D1D5DB' }}>SYSTEM-{index}</h2>

      <div style={{ display: 'flex', gap: '10px', marginBottom: '5px' }}>
        <ControlPanel
          title="VELOCITY"
          type="velocity"
          index={index}
          min={-500}
          max={500}
          data={velData}
          onSliderChange={onSliderChange}
          onSwitch={onSwitch}
        />

        <ControlPanel
          title="POSITION"
          type="position"
          index={index}
          min={-180}
          max={180}
          data={posData}
          onSliderChange={onSliderChange}
          onSwitch={onSwitch}
        />
      </div>

      <div style={{ flex: 1, display: 'flex', gap: '5px', minHeight: 0 }}>
        <div style={{ flex: 1, backgroundColor: '#111827', borderRadius: '4px', padding: '5px', display: 'flex', flexDirection: 'column' }}>
          <span style={{ fontSize: '10px', color: '#9CA3AF', marginBottom: '2px' }}>Velocity Graph</span>
          <div style={{ flex: 1, minHeight: 0 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={velHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="time" hide />
                <YAxis stroke="#9CA3AF" fontSize={8} domain={['auto', 'auto']} width={25} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', color: 'white', fontSize: '10px' }} />
                <Line type="monotone" dataKey="velocity" stroke="#3B82F6" dot={false} strokeWidth={1.5} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div style={{ flex: 1, backgroundColor: '#111827', borderRadius: '4px', padding: '5px', display: 'flex', flexDirection: 'column' }}>
          <span style={{ fontSize: '10px', color: '#9CA3AF', marginBottom: '2px' }}>Position Graph</span>
          <div style={{ flex: 1, minHeight: 0 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={posHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="time" hide />
                <YAxis stroke="#9CA3AF" fontSize={8} domain={['auto', 'auto']} width={25} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', color: 'white', fontSize: '10px' }} />
                <Line type="monotone" dataKey="position" stroke="#10B981" dot={false} strokeWidth={1.5} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

const ControlPanel = ({ title, type, index, min, max, data, onSliderChange, onSwitch }) => {
  const [val, setVal] = useState(0);
  const [enabled, setEnabled] = useState(true);

  return (
    <div style={{ flex: 1, backgroundColor: 'rgba(55, 65, 81, 0.5)', borderRadius: '6px', padding: '6px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2px' }}>
        <span style={{ fontWeight: 'bold', fontSize: '10px', color: '#9CA3AF' }}>{title}</span>
        <input
          type="checkbox"
          checked={enabled}
          onChange={(e) => {
            setEnabled(e.target.checked);
            onSwitch(`${type}_motor_${index}`, e.target.checked ? 'on' : 'off');
          }}
          style={{ cursor: 'pointer' }}
        />
      </div>

      <div style={{ marginBottom: '2px' }}>
        <input
          type="range"
          min={min}
          max={max}
          value={val}
          onChange={(e) => {
            setVal(e.target.value);
            onSliderChange(type, index, e.target.value);
          }}
          style={{ width: '100%', cursor: 'pointer', height: '4px' }}
        />
        <div style={{ textAlign: 'right', fontSize: '9px', fontFamily: 'monospace' }}>{val}</div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1px', fontSize: '9px', color: '#9CA3AF' }}>
        <div>Vel: <span style={{ color: 'white' }}>{data.velocity?.toFixed(0) || 0}</span></div>
        <div>Pos: <span style={{ color: 'white' }}>{data.position || 0}</span></div>
        <div>Load: <span style={{ color: 'white' }}>{data.load?.toFixed(0) || 0}%</span></div>
        <div>Trq: <span style={{ color: 'white' }}>{data.torque?.toFixed(1) || 0}</span></div>
      </div>
    </div>
  );
};

const DetailedPanel = ({ type, index, data, history }) => {
  const key = `${type}_${index}`;
  const sysHistory = history[key] || [];
  const itemData = data[key] || {};

  return (
    <div style={{
      backgroundColor: '#111827',
      padding: '8px',
      borderRadius: '6px',
      border: '1px solid #374151',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      <h3 style={{ marginTop: 0, marginBottom: '5px', fontSize: '12px', color: '#D1D5DB', fontWeight: 'bold' }}>
        {type.toUpperCase()} {index}
      </h3>
      <div style={{ flex: 1, minHeight: 0, marginBottom: '5px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={sysHistory}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="time" hide />
            <YAxis stroke="#9CA3AF" fontSize={8} width={25} />
            <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', fontSize: '10px' }} />
            <Line type="monotone" dataKey="velocity" stroke="#3B82F6" dot={false} strokeWidth={1} isAnimationActive={false} />
            <Line type="monotone" dataKey="position" stroke="#10B981" dot={false} strokeWidth={1} isAnimationActive={false} />
            <Line type="monotone" dataKey="load" stroke="#EF4444" dot={false} strokeWidth={1} isAnimationActive={false} />
            <Line type="monotone" dataKey="torque" stroke="#F59E0B" dot={false} strokeWidth={1} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <table style={{ width: '100%', fontSize: '10px', borderCollapse: 'collapse', color: '#D1D5DB' }}>
        <tbody>
          <tr><td style={{ padding: '1px' }}>V-Ctrl</td><td style={{ textAlign: 'right' }}>{itemData.voltage_control || 0} V</td></tr>
          <tr><td style={{ padding: '1px' }}>V-Out</td><td style={{ textAlign: 'right' }}>{itemData.output_voltage || 0} V</td></tr>
          <tr><td style={{ padding: '1px' }}>I-Out</td><td style={{ textAlign: 'right' }}>{itemData.output_current || 0} A</td></tr>
          <tr><td style={{ padding: '1px' }}>Temp</td><td style={{ textAlign: 'right' }}>{itemData.drive_temp || 0} °C</td></tr>
        </tbody>
      </table>
    </div>
  );
};

export default App;
