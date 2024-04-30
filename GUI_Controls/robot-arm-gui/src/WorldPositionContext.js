import React, { createContext, useContext, useState } from 'react';

// Create the context
const WorldPositionContext = createContext();

// Custom hook to use the context
export const useWorldPosition = () => useContext(WorldPositionContext);

// Provider component to wrap the part of your app that needs access to this context
export const WorldPositionProvider = ({ children }) => {
    const [position, setPosition] = useState({ x: 0, y: 0, z: 0 });

    return (
        <WorldPositionContext.Provider value={{ position, setPosition }}>
            {children}
        </WorldPositionContext.Provider>
    );
};
