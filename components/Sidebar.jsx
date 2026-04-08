import React from 'react';
import styles from '../styles/Sidebar.module.css';

export default function Sidebar({
  colors,
  colorIndex,
  brushSize,
  glowAmount,
  onColorSelect,
  onBrushChange,
  onGlowChange,
  onUndo,
  onRedo,
  onClear,
  onToggleEraser,
  onSave,
}) {
  const activeColor = colors[colorIndex];

  return (
    <div className={styles.sidebar}>
      {/* COLORS label */}
      <div className={styles.label}>COLORS</div>

      {/* Color grid */}
      <div className={styles.colorGrid}>
        {colors.map((color, idx) => (
          <button
            key={idx}
            className={`${styles.colorDot} ${idx === colorIndex ? styles.active : ''}`}
            style={{ background: color.hex, boxShadow: `0 0 8px rgba(${color.g},0.4)` }}
            onClick={() => onColorSelect(idx)}
            title={color.name}
            aria-label={color.name}
          />
        ))}
      </div>

      {/* THICKNESS label */}
      <div className={styles.label} style={{ marginTop: '12px' }}>
        THICKNESS
      </div>

      {/* Neon star preview */}
      <div
        className={styles.neonStar}
        style={{
          color: activeColor.hex,
          filter: `drop-shadow(0 0 8px rgba(${activeColor.g},0.7))`,
        }}
      >
        ✱
      </div>

      {/* Thickness slider */}
      <div className={styles.sliderSection}>
        <input
          type="range"
          min="1"
          max="40"
          value={brushSize}
          onChange={(e) => onBrushChange(parseInt(e.target.value))}
          className={styles.slider}
        />
        <div className={styles.sliderValue}>{brushSize}px</div>
      </div>

      {/* GLOW label */}
      <div className={styles.label} style={{ marginTop: '12px' }}>
        GLOW
      </div>

      {/* Glow slider */}
      <div className={styles.sliderSection}>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={glowAmount}
          onChange={(e) => onGlowChange(parseFloat(e.target.value))}
          className={styles.slider}
        />
        <div className={styles.sliderValue}>{Math.round(glowAmount * 100)}%</div>
      </div>

      {/* Divider */}
      <div className={styles.divider} />

      {/* Icon buttons */}
      <div className={styles.iconRow}>
        <button
          className={styles.iconBtn}
          onClick={onUndo}
          title="Undo (Z)"
          aria-label="Undo"
        >
          ↩
        </button>
        <button
          className={styles.iconBtn}
          onClick={onClear}
          title="Clear (C)"
          aria-label="Clear"
        >
          🗑
        </button>
        <button
          className={styles.iconBtn}
          onClick={onToggleEraser}
          title="Eraser (E)"
          aria-label="Eraser"
        >
          ⊘
        </button>
        <button
          className={styles.iconBtn}
          onClick={onSave}
          title="Save (S)"
          aria-label="Save"
        >
          💾
        </button>
      </div>
    </div>
  );
}
