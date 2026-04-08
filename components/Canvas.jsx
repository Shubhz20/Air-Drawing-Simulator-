import React, { useEffect, useRef, useState, forwardRef, useImperativeHandle } from 'react';
import styles from '../styles/Canvas.module.css';

const Canvas = forwardRef(
  ({ videoRef, colorIndex, brushSize, glowAmount, showHand }, ref) => {
    const canvasRef = useRef(null);
    const [undoStack, setUndoStack] = useState([]);
    const [redoStack, setRedoStack] = useState([]);

    useImperativeHandle(ref, () => ({
      undo: () => {
        // Implement undo logic
      },
      redo: () => {
        // Implement redo logic
      },
      clear: () => {
        if (canvasRef.current) {
          const ctx = canvasRef.current.getContext('2d');
          ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
        }
      },
      save: () => {
        if (canvasRef.current) {
          const link = document.createElement('a');
          link.download = `air-drawing_${Date.now()}.png`;
          link.href = canvasRef.current.toDataURL();
          link.click();
        }
      },
      toggleEraser: () => {
        // Toggle eraser mode
      },
    }));

    useEffect(() => {
      const canvas = canvasRef.current;
      if (canvas) {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
      }

      const handleResize = () => {
        if (canvas) {
          canvas.width = window.innerWidth;
          canvas.height = window.innerHeight;
        }
      };

      window.addEventListener('resize', handleResize);
      return () => window.removeEventListener('resize', handleResize);
    }, []);

    return (
      <div className={styles.canvasContainer}>
        <canvas
          ref={canvasRef}
          className={styles.canvas}
          width={typeof window !== 'undefined' ? window.innerWidth : 1280}
          height={typeof window !== 'undefined' ? window.innerHeight : 720}
        />
        <video
          ref={videoRef}
          className={styles.video}
          autoPlay
          playsInline
          muted
          style={{ display: 'none' }}
        />
      </div>
    );
  }
);

Canvas.displayName = 'Canvas';

export default Canvas;
