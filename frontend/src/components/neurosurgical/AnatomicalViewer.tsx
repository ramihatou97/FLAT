/**
 * AnatomicalViewer Component
 * Advanced 3D anatomical visualization for neurosurgical content
 * Features interactive brain models, surgical planning, and educational overlays
 */

import React, { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Environment, Html } from '@react-three/drei';
import * as THREE from 'three';
import { Box, Typography, Slider, Switch, FormControlLabel, Chip, Paper, IconButton } from '@mui/material';
import { Visibility, VisibilityOff, Settings, Fullscreen, Download, Share } from '@mui/icons-material';
import { styled } from '@mui/material/styles';

// Types
interface AnatomicalStructure {
  id: string;
  name: string;
  latinName?: string;
  coordinates3d: {
    center: [number, number, number];
    bounds: [[number, number, number], [number, number, number]];
  };
  meshData?: {
    vertices: number[];
    faces: number[];
    normals: number[];
  };
  tissueType: string;
  eloquentArea: boolean;
  vascularSupply: Record<string, string[]>;
  clinicalSignificance: string;
  surgicalApproaches: string[];
  visible: boolean;
  opacity: number;
  color: string;
}

interface SurgicalProcedure {
  id: string;
  name: string;
  approach: string;
  targetStructures: string[];
  trajectory?: {
    entry: [number, number, number];
    target: [number, number, number];
  };
  riskZones: Array<{
    structure: string;
    riskLevel: 'low' | 'medium' | 'high' | 'critical';
    coordinates: [number, number, number];
  }>;
}

interface ViewerProps {
  structures: AnatomicalStructure[];
  selectedProcedure?: SurgicalProcedure;
  viewMode: 'anatomy' | 'surgical' | 'pathology' | 'educational';
  onStructureSelect: (structure: AnatomicalStructure) => void;
  onStructureHover: (structure: AnatomicalStructure | null) => void;
  showLabels: boolean;
  showVasculature: boolean;
  showRiskZones: boolean;
  educationalMode: boolean;
}

// Styled components
const ViewerContainer = styled(Box)(({ theme }) => ({
  position: 'relative',
  width: '100%',
  height: '600px',
  backgroundColor: '#000',
  borderRadius: theme.shape.borderRadius,
  overflow: 'hidden',
  border: `1px solid ${theme.palette.divider}`,
}));

const ControlPanel = styled(Paper)(({ theme }) => ({
  position: 'absolute',
  top: 16,
  right: 16,
  padding: theme.spacing(2),
  backgroundColor: 'rgba(255, 255, 255, 0.95)',
  backdropFilter: 'blur(10px)',
  zIndex: 10,
  minWidth: 250,
  maxHeight: '80%',
  overflowY: 'auto',
}));

const InfoPanel = styled(Paper)(({ theme }) => ({
  position: 'absolute',
  bottom: 16,
  left: 16,
  padding: theme.spacing(2),
  backgroundColor: 'rgba(255, 255, 255, 0.95)',
  backdropFilter: 'blur(10px)',
  zIndex: 10,
  maxWidth: 400,
}));

const ToolBar = styled(Box)(({ theme }) => ({
  position: 'absolute',
  top: 16,
  left: 16,
  display: 'flex',
  gap: theme.spacing(1),
  zIndex: 10,
}));

// 3D Brain Model Component
const BrainModel: React.FC<{
  structures: AnatomicalStructure[];
  onStructureClick: (structure: AnatomicalStructure) => void;
  onStructureHover: (structure: AnatomicalStructure | null) => void;
  selectedProcedure?: SurgicalProcedure;
  showRiskZones: boolean;
}> = ({ structures, onStructureClick, onStructureHover, selectedProcedure, showRiskZones }) => {
  const groupRef = useRef<THREE.Group>(null);
  const [hoveredStructure, setHoveredStructure] = useState<string | null>(null);

  // Create meshes for anatomical structures
  const structureMeshes = useMemo(() => {
    return structures.map((structure) => {
      if (!structure.meshData || !structure.visible) return null;

      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position', new THREE.Float32BufferAttribute(structure.meshData.vertices, 3));
      geometry.setAttribute('normal', new THREE.Float32BufferAttribute(structure.meshData.normals, 3));
      geometry.setIndex(structure.meshData.faces);

      const material = new THREE.MeshPhongMaterial({
        color: structure.color,
        transparent: true,
        opacity: structure.opacity,
        side: THREE.DoubleSide,
      });

      return {
        structure,
        geometry,
        material,
      };
    }).filter(Boolean);
  }, [structures]);

  // Handle structure interaction
  const handleStructureClick = useCallback((structure: AnatomicalStructure) => {
    onStructureClick(structure);
  }, [onStructureClick]);

  const handleStructureHover = useCallback((structure: AnatomicalStructure | null) => {
    setHoveredStructure(structure?.id || null);
    onStructureHover(structure);
  }, [onStructureHover]);

  return (
    <group ref={groupRef}>
      {/* Render anatomical structures */}
      {structureMeshes.map(({ structure, geometry, material }, index) => (
        <mesh
          key={structure.id}
          geometry={geometry}
          material={material}
          position={structure.coordinates3d.center}
          onClick={() => handleStructureClick(structure)}
          onPointerOver={() => handleStructureHover(structure)}
          onPointerOut={() => handleStructureHover(null)}
          scale={hoveredStructure === structure.id ? 1.05 : 1.0}
        >
          {/* Structure label */}
          {structure.visible && (
            <Html position={[0, 0, 0]} center>
              <div
                style={{
                  background: 'rgba(0, 0, 0, 0.8)',
                  color: 'white',
                  padding: '4px 8px',
                  borderRadius: '4px',
                  fontSize: '12px',
                  pointerEvents: 'none',
                  opacity: hoveredStructure === structure.id ? 1 : 0,
                  transition: 'opacity 0.2s',
                }}
              >
                {structure.name}
              </div>
            </Html>
          )}
        </mesh>
      ))}

      {/* Render surgical trajectory */}
      {selectedProcedure?.trajectory && (
        <group>
          {/* Entry point */}
          <mesh position={selectedProcedure.trajectory.entry}>
            <sphereGeometry args={[2, 16, 16]} />
            <meshBasicMaterial color="#00ff00" />
          </mesh>

          {/* Target point */}
          <mesh position={selectedProcedure.trajectory.target}>
            <sphereGeometry args={[1.5, 16, 16]} />
            <meshBasicMaterial color="#ff0000" />
          </mesh>

          {/* Trajectory line */}
          <line>
            <bufferGeometry>
              <bufferAttribute
                attach="attributes-position"
                count={2}
                array={new Float32Array([
                  ...selectedProcedure.trajectory.entry,
                  ...selectedProcedure.trajectory.target,
                ])}
                itemSize={3}
              />
            </bufferGeometry>
            <lineBasicMaterial color="#ffff00" linewidth={3} />
          </line>
        </group>
      )}

      {/* Render risk zones */}
      {showRiskZones && selectedProcedure?.riskZones.map((riskZone, index) => (
        <mesh key={index} position={riskZone.coordinates}>
          <sphereGeometry args={[3, 16, 16]} />
          <meshBasicMaterial
            color={
              riskZone.riskLevel === 'critical' ? '#ff0000' :
              riskZone.riskLevel === 'high' ? '#ff8800' :
              riskZone.riskLevel === 'medium' ? '#ffff00' : '#00ff00'
            }
            transparent
            opacity={0.3}
          />
          <Html position={[0, 4, 0]} center>
            <Chip
              label={`${riskZone.riskLevel.toUpperCase()} RISK`}
              size="small"
              color={
                riskZone.riskLevel === 'critical' ? 'error' :
                riskZone.riskLevel === 'high' ? 'warning' : 'default'
              }
            />
          </Html>
        </mesh>
      ))}
    </group>
  );
};

// Camera Controller Component
const CameraController: React.FC<{ viewMode: string }> = ({ viewMode }) => {
  const { camera } = useThree();

  useEffect(() => {
    // Set camera position based on view mode
    switch (viewMode) {
      case 'anatomy':
        camera.position.set(0, 0, 100);
        break;
      case 'surgical':
        camera.position.set(50, 50, 50);
        break;
      case 'pathology':
        camera.position.set(-50, 0, 50);
        break;
      case 'educational':
        camera.position.set(0, 100, 0);
        break;
      default:
        camera.position.set(0, 0, 100);
    }
    camera.lookAt(0, 0, 0);
  }, [viewMode, camera]);

  return null;
};

// Main AnatomicalViewer Component
export const AnatomicalViewer: React.FC<ViewerProps> = ({
  structures,
  selectedProcedure,
  viewMode,
  onStructureSelect,
  onStructureHover,
  showLabels,
  showVasculature,
  showRiskZones,
  educationalMode,
}) => {
  const [selectedStructure, setSelectedStructure] = useState<AnatomicalStructure | null>(null);
  const [hoveredStructure, setHoveredStructure] = useState<AnatomicalStructure | null>(null);
  const [controlsVisible, setControlsVisible] = useState(true);
  const [globalOpacity, setGlobalOpacity] = useState(0.8);

  // Handle structure selection
  const handleStructureSelect = useCallback((structure: AnatomicalStructure) => {
    setSelectedStructure(structure);
    onStructureSelect(structure);
  }, [onStructureSelect]);

  // Handle structure hover
  const handleStructureHover = useCallback((structure: AnatomicalStructure | null) => {
    setHoveredStructure(structure);
    onStructureHover(structure);
  }, [onStructureHover]);

  // Toggle structure visibility
  const toggleStructureVisibility = useCallback((structureId: string) => {
    // This would update the structures array
    console.log(`Toggle visibility for structure: ${structureId}`);
  }, []);

  // Export 3D view
  const handleExport = useCallback(() => {
    // Implementation for exporting 3D view
    console.log('Exporting 3D view...');
  }, []);

  // Share view
  const handleShare = useCallback(() => {
    // Implementation for sharing view
    console.log('Sharing view...');
  }, []);

  return (
    <ViewerContainer>
      {/* 3D Canvas */}
      <Canvas>
        <PerspectiveCamera makeDefault position={[0, 0, 100]} fov={60} />
        <CameraController viewMode={viewMode} />
        
        {/* Lighting */}
        <ambientLight intensity={0.4} />
        <directionalLight position={[10, 10, 5]} intensity={0.8} />
        <pointLight position={[-10, -10, -5]} intensity={0.5} />
        
        {/* Environment */}
        <Environment preset="studio" />
        
        {/* Brain Model */}
        <BrainModel
          structures={structures}
          onStructureClick={handleStructureSelect}
          onStructureHover={handleStructureHover}
          selectedProcedure={selectedProcedure}
          showRiskZones={showRiskZones}
        />
        
        {/* Controls */}
        <OrbitControls
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          minDistance={20}
          maxDistance={200}
        />
      </Canvas>

      {/* Toolbar */}
      <ToolBar>
        <IconButton
          onClick={() => setControlsVisible(!controlsVisible)}
          sx={{ backgroundColor: 'rgba(255, 255, 255, 0.9)' }}
        >
          <Settings />
        </IconButton>
        <IconButton
          onClick={handleExport}
          sx={{ backgroundColor: 'rgba(255, 255, 255, 0.9)' }}
        >
          <Download />
        </IconButton>
        <IconButton
          onClick={handleShare}
          sx={{ backgroundColor: 'rgba(255, 255, 255, 0.9)' }}
        >
          <Share />
        </IconButton>
        <IconButton
          sx={{ backgroundColor: 'rgba(255, 255, 255, 0.9)' }}
        >
          <Fullscreen />
        </IconButton>
      </ToolBar>

      {/* Control Panel */}
      {controlsVisible && (
        <ControlPanel>
          <Typography variant="h6" gutterBottom>
            Visualization Controls
          </Typography>

          {/* Global Opacity */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" gutterBottom>
              Global Opacity
            </Typography>
            <Slider
              value={globalOpacity}
              onChange={(_, value) => setGlobalOpacity(value as number)}
              min={0.1}
              max={1.0}
              step={0.1}
              valueLabelDisplay="auto"
            />
          </Box>

          {/* Structure Visibility */}
          <Typography variant="body2" gutterBottom>
            Anatomical Structures
          </Typography>
          {structures.slice(0, 5).map((structure) => (
            <FormControlLabel
              key={structure.id}
              control={
                <Switch
                  checked={structure.visible}
                  onChange={() => toggleStructureVisibility(structure.id)}
                  size="small"
                />
              }
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box
                    sx={{
                      width: 12,
                      height: 12,
                      backgroundColor: structure.color,
                      borderRadius: '50%',
                    }}
                  />
                  <Typography variant="body2">{structure.name}</Typography>
                </Box>
              }
            />
          ))}

          {/* View Options */}
          <Box sx={{ mt: 2 }}>
            <FormControlLabel
              control={<Switch checked={showLabels} size="small" />}
              label="Show Labels"
            />
            <FormControlLabel
              control={<Switch checked={showVasculature} size="small" />}
              label="Show Vasculature"
            />
            <FormControlLabel
              control={<Switch checked={showRiskZones} size="small" />}
              label="Show Risk Zones"
            />
          </Box>
        </ControlPanel>
      )}

      {/* Info Panel */}
      {(selectedStructure || hoveredStructure) && (
        <InfoPanel>
          {selectedStructure && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {selectedStructure.name}
              </Typography>
              {selectedStructure.latinName && (
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  <em>{selectedStructure.latinName}</em>
                </Typography>
              )}
              <Typography variant="body2" paragraph>
                {selectedStructure.clinicalSignificance}
              </Typography>
              
              {selectedStructure.eloquentArea && (
                <Chip
                  label="Eloquent Area"
                  color="error"
                  size="small"
                  sx={{ mr: 1, mb: 1 }}
                />
              )}
              
              <Chip
                label={selectedStructure.tissueType}
                variant="outlined"
                size="small"
                sx={{ mr: 1, mb: 1 }}
              />

              {selectedStructure.surgicalApproaches.length > 0 && (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="body2" fontWeight="bold">
                    Surgical Approaches:
                  </Typography>
                  {selectedStructure.surgicalApproaches.map((approach, index) => (
                    <Chip
                      key={index}
                      label={approach}
                      variant="outlined"
                      size="small"
                      sx={{ mr: 0.5, mt: 0.5 }}
                    />
                  ))}
                </Box>
              )}
            </Box>
          )}
        </InfoPanel>
      )}
    </ViewerContainer>
  );
};

export default AnatomicalViewer;
