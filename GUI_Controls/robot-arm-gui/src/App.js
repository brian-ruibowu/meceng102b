import React, { useState } from 'react';
import './App.css';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { Sky } from '@react-three/drei';
import DrawingModal from './DrawingModal';
import Model4 from './model4';
import Model2 from './model2';
import Model1 from './model1';
import Model3 from './model3';
import { WorldPositionProvider } from './WorldPositionContext';

function App() {
  const [angles, setAngles] = useState({ theta1: '', theta2: '', theta3: '', theta4: '' });
  const [coordinates, setCoordinates] = useState({ x: '', y: '', z: '' });
  const [mode, setMode] = useState('forward'); // 'forward' or 'inverse'
  const [targetRotation1, setTargetRotation1] = useState(0);
  const [targetRotation2, setTargetRotation2] = useState(0);
  const [targetRotation3, setTargetRotation3] = useState(0);
  const [targetRotation4, setTargetRotation4] = useState(0);
  const [dragging, setDragging] = useState(false);
  const [result, setResult] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const openModal = () => setShowModal(true);
  const closeModal = () => setShowModal(false);

  const handleAngleChange = (key, value) => {
    const numValue = parseFloat(value); // Convert to number
    if (!isNaN(numValue)) { // Only update if the value is a valid number
      setAngles(prev => ({ ...prev, [key]: numValue }));
    }
  };

  const handleCoordinateChange = (key, value) => {
    const numValue = parseFloat(value); // Convert to number
    if (!isNaN(numValue)) { // Only update if the value is a valid number
      setCoordinates(prev => ({ ...prev, [key]: numValue }));
    }
  };

  const handleMouseDown = (e, key, max) => {
    const progress = e.target;
    setDragging(true);  // Set dragging state to true to enable movement tracking
  
    const moveHandler = (event) => {
      if (!dragging) return;  // If not dragging, do nothing
      const rect = progress.getBoundingClientRect();
      const newRelativeX = event.clientX - rect.left;  // Relative X position of the mouse from the progress start
      const newValue = (newRelativeX / rect.width) * max;
      updateValue(key, newValue);  // Function to update the specific angle or coordinate
    };
  
    const upHandler = () => {
      setDragging(false);
      document.removeEventListener('mousemove', moveHandler);
      document.removeEventListener('mouseup', upHandler);
    };
  
    document.addEventListener('mousemove', moveHandler);
    document.addEventListener('mouseup', upHandler);
  };
  
  const updateValue = (key, newValue) => {
    if (mode === 'forward') {
      setAngles(prev => ({ ...prev, [key]: Math.max(0, Math.min(newValue, 6.28319)) }));  // Ensure values are within range
    } else {
      setCoordinates(prev => ({ ...prev, [key]: Math.max(0, Math.min(newValue, 100)) }));  // Ensure values are within range
    }
  };

  const handleMouseMove = (e, key, max) => {
    if (dragging) {
      const progress = e.target;
      const rect = progress.getBoundingClientRect();
      const newValue = ((e.clientX - rect.left) / rect.width) * max;
      if (mode === 'forward') {
        setAngles({ ...angles, [key]: newValue });
      } else {
        setCoordinates({ ...coordinates, [key]: newValue });
      }
    }
  };

  const handleMouseUp = (key) => {
    setDragging(false);
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  };

  const handleKinematics = async () => {
    const endpoint = mode === 'forward' ? 'api/forward' : 'api/inverse';
    const payload = mode === 'forward' ? { parameters: angles } : { x: coordinates.x, y: coordinates.y, z: coordinates.z };

    try {
      const response = await fetch(`http://localhost:5000/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`HTTP error! status: ${response.status}, Error: ${errorData.error}`);
      }

      const data = await response.json();
      setResult(data);

      if (mode === 'forward') {
        // Assuming data.position might contain base rotation angle in radians
        // or that you have an input field where the user inputs this angle
        setTargetRotation1(parseFloat(angles.theta1));
        console.log(targetRotation1);
        setTargetRotation2(parseFloat(angles.theta2));
        setTargetRotation3(parseFloat(angles.theta3));
        setTargetRotation4(parseFloat(angles.theta4));
      } else if (mode === 'inverse' && data.angles) {
      }

    } catch ( error ) {
      console.error("Failed to fetch kinematics data:", error);
      setResult({ error: error.message || "Failed to fetch" });
    }
  }

  return (
    <div className="App">
      <div style={{ width: '50%', height: '100vh', float: 'left', backgroundColor: '#a0d2eb' }}>
        <label>
          <input 
            type="radio" 
            value="forward" 
            checked={mode === 'forward'} 
            onChange={() => setMode('forward')} // Ensures the mode is set to 'forward'
            style={{ marginTop: '50px' }}
          /> Forward Kinematics
        </label>
        <label>
          <input 
            type="radio" 
            value="inverse" 
            checked={mode === 'inverse'} 
            onChange={() => setMode('inverse')} // Ensures the mode is set to 'inverse'
          /> Inverse Kinematics
        </label>
        
        {Object.entries(angles).map(([key, value]) => (
          <div key={key} className="flex-container">
            <input
              type="number"
              value={value.toString()} // Ensure value is a string for the input
              onChange={e => handleAngleChange(key, e.target.value)}
              placeholder={key.toUpperCase()}
              className="input"
              disabled={mode !== 'forward'}
            />
            <progress
              value={value}
              max="6.28319"
              className="progress-bar"
              onMouseDown={e => handleMouseDown(e, key, 6.28319)}
            ></progress>
          </div>
        ))}

        {Object.entries(coordinates).map(([key, value]) => (
          <div key={key} className="flex-container">
            <input
              type="number"
              value={value.toString()} // Ensure value is a string for the input
              onChange={e => handleCoordinateChange(key, e.target.value)}
              placeholder={key.toUpperCase()}
              className="input"
              disabled={mode !== 'inverse'}
            />
            <progress
              value={value}
              max="100"
              className="progress-bar"
              onMouseDown={e => handleMouseDown(e, key, 100)}
            ></progress>
          </div>
        ))}
    
        <button onClick={handleKinematics}>Calculate {mode === 'forward' ? 'Forward' : 'Inverse'} Kinematics</button>
        <button onClick={openModal} style={{ marginLeft: '35px' }}>Draw</button>
        <DrawingModal isOpen={showModal} onClose={closeModal} />
      </div>
      <div style={{ width: '50%', float: 'right', height: "100vh", display: "flex" }}>
        <WorldPositionProvider>
          <Canvas>
            <Sky distance={450000} sunPosition={[0, 1, 0]} inclination={0} azimuth={0.25} />
            <ambientLight intensity={0.5} />
            <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} />
            <pointLight position={[-10, -10, -10]} />
            <OrbitControls />
            <Model1 targetRotation1={targetRotation1} targetRotation2={targetRotation2} targetRotation3={targetRotation3} boxPosition={[0, 1.709, 0]}/>
            <Model2 targetRotation1={targetRotation1}
                    targetRotation2={targetRotation2}
                    targetRotation3={targetRotation3}
                    initialBoxPosition={[0, 3.709, 0]} />
            <Model3 targetRotation1={targetRotation1} boxPosition={[0, 1, 0]}/>
            {/* <Model2 targetRotation1={targetRotation1} targetRotation3={targetRotation3}/> */}
            <Model4 />
            <gridHelper args={[15, 15]} />
            <axesHelper args={[5]} />
          </Canvas>
        </WorldPositionProvider>
        
      </div>
    </div>
  );
}

export default App;