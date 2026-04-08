import React from 'react';
import styles from '../styles/Modal.module.css';

export default function Modal({ isOpen, onClose }) {
  if (!isOpen) return null;

  const gestures = [
    { emoji: '☝️', name: 'Draw', desc: 'Point index finger to draw' },
    { emoji: '✋', name: 'Erase', desc: 'Sweep open palm to erase' },
    { emoji: '🤏', name: 'Move', desc: 'Pinch to grab & reposition' },
    { emoji: '✌️', name: 'Idle', desc: 'Close fist to rest' },
  ];

  return (
    <div className={styles.overlay}>
      <div className={styles.card}>
        <div className={styles.logo}>A</div>
        <div className={styles.title}>How to Play</div>

        <div className={styles.gestureCards}>
          {gestures.map((g, idx) => (
            <div key={idx} className={styles.gestureCard}>
              <div className={styles.emoji}>{g.emoji}</div>
              <div>
                <div className={styles.gName}>{g.name}</div>
                <div className={styles.gDesc}>{g.desc}</div>
              </div>
            </div>
          ))}
        </div>

        <button className={styles.button} onClick={onClose}>
          Let's Go!
        </button>
      </div>
    </div>
  );
}
