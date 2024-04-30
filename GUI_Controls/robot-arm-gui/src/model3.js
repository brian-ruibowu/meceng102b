import { useEffect, useRef } from 'react';
import { useLoader, useFrame, useThree } from '@react-three/fiber';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader';
import SHOULDER from './models/robotshoulder.obj';
import { Vector3, MathUtils, Box3, BoxHelper, BoxGeometry, MeshBasicMaterial, Mesh } from 'three';
import { MeshStandardMaterial } from 'three';

function setAbsolutePosition(obj, newPosition) {
    if (obj && obj.parent) {
        obj.position.set(newPosition.x, newPosition.y, newPosition.z);
        obj.parent.worldToLocal(obj.position);
    } else if (obj) {
        obj.position.set(newPosition.x, newPosition.y, newPosition.z);
    }
}

function Model3({ targetRotation1, boxPosition }) {
    const obj = useLoader(OBJLoader, SHOULDER);
    const objRef = useRef();
    const { scene } = useThree();
    const customBoxRef = useRef();
    const boxRef = useRef();

    if (targetRotation1 == null) {
        targetRotation1 = 0;
    }

    console.log(targetRotation1)

    // useEffect(() => {
    //     obj.traverse((child) => {
    //         if (child.isMesh) {
    //             child.material = new MeshStandardMaterial({ color: 'blue' });
    //         }
    //     });
    //     objRef.current = obj;
    //     setAbsolutePosition(obj, new Vector3(0, 1.71, -0.5));
    // }, [obj]);

    useEffect(() => {
        obj.traverse(child => {
            if (child.isMesh) {
                child.material = new MeshStandardMaterial({ color: 'blue' });
            }
        });

        // Set up the box
        const geometry = new BoxGeometry(3, 2, 3);
        const material = new MeshBasicMaterial({ color: 0xff0000, wireframe: true });
        const box = new Mesh(geometry, material);
        boxRef.current = box;
        box.position.set(...boxPosition); // Set initial position from prop
        box.add(obj); // Add the model as a child of the box
        scene.add(box);

        return () => {
            scene.remove(box);
        };
    }, [obj, scene, boxPosition]); // Include boxPosition in dependency array

    useFrame(() => {
        if (boxRef.current) {
            // Rotate the box towards the target rotation
            boxRef.current.rotation.y = MathUtils.lerp(boxRef.current.rotation.y, targetRotation1 || 0, 0.005);
            boxRef.color = 'blue';
            
            // Update position if it changes dynamically
            boxRef.current.position.set(...boxPosition);
        }
    });

    return (
        <primitive 
            object={obj} 
            position={[0, 0.71, -0.5]}
            scale={[0.01, 0.01, 0.01]}
        />
    );
}

export default Model3;
