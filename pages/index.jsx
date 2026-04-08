import React, { useEffect, useRef, useState } from 'react';
import Head from 'next/head';
import styles from '../styles/Home.module.css';
import Canvas from '../components/Canvas';
import Sidebar from '../components/Sidebar';
import Modal from '../components/Modal';
import FlashMessage from '../components/FlashMessage';

const COLORS = [
  { name: 'Cyan', hex: '#00f5ff', g: '0,245,255' },
  { name: 'Green', hex: '#22ff44', g: '34,255,68' },
  { name: 'Magenta', hex: '#ff22cc', g: '255,34,204' },
  { name: 'Blue', hex: '#4488ff', g: '68,136,255' },
  { name: 'Lime', hex: '#aaff00', g: '170,255,0' },
  { name: 'Pink', hex: '#ff4488', g: '255,68,136' },
  { name: 'Yellow', hex: '#ffdd00', g: '255,221,0' },
  { name: 'Purple', hex: '#bb44ff', g: '187,68,255' },
  { name: 'White', hex: '#ffffff', g: '255,255,255' },
  { name: 'Slate', hex: '#667788', g: '102,119,136' },
];

export default function Home() {
  const [colorIndex, setColorIndex] = useState(0);
  const [brushSize, setBrushSize] = useState(6);
  const [glowAmount, setGlowAmount] = useState(0.6);
  const [showHand, setShowHand] = useState(true);
  const [showModal, setShowModal] = useState(true);
  const [flash, setFlash] = useState({ text: '', color: '#fff' });
  const canvasRef = useRef(null);
  const videoRef = useRef(null);

  // Flash message helper
  const showFlash = (text, color = '#fff') => {
    setFlash({ text, color });
    setTimeout(() => setFlash({ text: '', color: '#fff' }), 1000);
  };

  // Canvas handlers
  const handleUndo = async () => {
    if (canvasRef.current) {
      canvasRef.current.undo();
      showFlash('Undo', '#7bd');
    }
  };

  const handleRedo = async () => {
    if (canvasRef.current) {
      canvasRef.current.redo();
      showFlash('Redo', '#7db');
    }
  };

  const handleClear = async () => {
    if (canvasRef.current) {
      canvasRef.current.clear();
      showFlash('Cleared', '#ff5566');
    }
  };

  const handleSave = async () => {
    if (canvasRef.current) {
      canvasRef.current.save();
      showFlash('Saved!', '#4ade80');
    }
  };

  const handleColorSelect = (idx) => {
    setColorIndex(idx);
    showFlash(`Colour: ${COLORS[idx].name}`, COLORS[idx].hex);
  };

  const handleToggleEraser = () => {
    if (canvasRef.current) {
      canvasRef.current.toggleEraser();
    }
  };

  const handleToggleHand = () => {
    setShowHand(!showHand);
    showFlash(showHand ? 'Hand Hidden' : 'Hand Visible', '#aaa');
  };

  return (
    <>
      <Head>
        <title>Air Draw — Gesture-Based Doodler</title>
        <meta name="description" content="Draw in the air using hand gestures" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className={styles.container}>
        <div className={styles.webcamBg}></div>

        {/* Canvas & Video */}
        <Canvas
          ref={canvasRef}
          videoRef={videoRef}
          colorIndex={colorIndex}
          brushSize={brushSize}
          glowAmount={glowAmount}
          showHand={showHand}
        />

        {/* Camera badge */}
        <div className={styles.cameraBadge}>
          <span className={styles.statusDot}></span>
          Camera ON
        </div>

        {/* Mode label */}
        <div className={styles.modeLabel}>
          Live — Using hand gestures
        </div>

        {/* Right sidebar */}
        <Sidebar
          colors={COLORS}
          colorIndex={colorIndex}
          brushSize={brushSize}
          glowAmount={glowAmount}
          onColorSelect={handleColorSelect}
          onBrushChange={setBrushSize}
          onGlowChange={setGlowAmount}
          onUndo={handleUndo}
          onRedo={handleRedo}
          onClear={handleClear}
          onToggleEraser={handleToggleEraser}
          onSave={handleSave}
        />

        {/* Bottom toggle */}
        <div className={styles.bottomToggle} onClick={handleToggleHand}>
          <span className={styles.handEmoji}>👋</span>
          <span>{showHand ? 'SHOW HAND' : 'HIDE HAND'}</span>
        </div>

        {/* Flash message */}
        <FlashMessage text={flash.text} color={flash.color} />

        {/* Onboarding modal */}
        <Modal isOpen={showModal} onClose={() => setShowModal(false)} />
      </div>
    </>
  );
}
